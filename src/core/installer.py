"""
Tool installation manager for eSim Tool Manager
Handles downloading, installing, and configuring tools
"""

import zipfile
import subprocess
import shlex
from pathlib import Path
from typing import Optional, Tuple, List
from src.utils.logger import get_logger
from src.utils.downloader import FileDownloader
from src.utils.dependency_checker import DependencyChecker
from src.utils.system_utils import EnvironmentManager, ProcessManager
from src.core.config_manager import ConfigManager

class InstallationManager:
    """Manage tool installation"""
    
    def __init__(self, config_dir: str = "./config"):
        """
        Initialize installation manager
        
        Args:
            config_dir: Configuration directory
        """
        self.logger = get_logger()
        self.config_manager = ConfigManager(config_dir)
        self.dependency_checker = DependencyChecker(config_dir)
        self.downloader = FileDownloader()
        self.temp_dir = Path("./temp_downloads")
    
    def install_tool(self, tool_name: str, version: Optional[str] = None) -> bool:
        """
        Install a tool
        
        Args:
            tool_name: Tool to install
            version: Specific version (optional)
            
        Returns:
            True if successful
        """
        self.logger.info(f"Starting installation of {tool_name}...")
        
        # Get tool configuration
        tool_config = self.config_manager.get_tool_config(tool_name)
        if not tool_config:
            self.logger.error(f"Tool {tool_name} not found in configuration")
            return False
        
        # Check if already installed
        if tool_config.get("installed"):
            self.logger.warning(f"{tool_name} is already installed at {tool_config.get('install_path')}")
            return True
        
        # Check dependencies
        self.logger.info(f"Checking dependencies for {tool_name}...")
        deps_ok, missing = self.dependency_checker.check_dependencies(tool_name)
        if not deps_ok:
            self.logger.warning(f"Missing dependencies: {', '.join(missing)}")
            # Don't fail,  just warn
        
        # Determine version to install
        if not version:
            version = tool_config.get("latest_version")
        
        self.logger.info(f"Installing {tool_name} version {version}...")
        
        # Download tool
        if not self._download_tool(tool_name, version, tool_config):
            return False
        
        # Install tool
        if not self._execute_installation(tool_name, version, tool_config):
            return False
        
        # Configure tool
        if not self._configure_tool(tool_name, tool_config):
            return False
        
        # Verify installation
        if not self._verify_installation(tool_name, tool_config):
            return False
        
        # Update configuration
        install_path = self.config_manager.get_installation_directory() / tool_name
        self.config_manager.set_tool_installed(tool_name, True, str(install_path))
        self.config_manager.update_tool_version(tool_name, version)
        
        self.logger.success(f"{tool_name} {version} installed successfully!")
        return True
    
    def _download_tool(self, tool_name: str, version: str, tool_config: dict) -> bool:
        """Download tool files"""
        try:
            url = tool_config.get("windows_download_url")
            if not url:
                self.logger.error(f"No download URL for {tool_name}")
                return False

            filename = tool_config.get("windows_filename", f"{tool_name}-{version}.zip")
            
            # Create temp directory
            self.temp_dir.mkdir(exist_ok=True)
            
            # Construct full URL using placeholders or fallback conventions.
            if "{" in url and "}" in url:
                url = url.format(version=version, filename=filename, tool_name=tool_name)
            elif url.lower().endswith((".zip", ".exe", ".msi")):
                pass
            else:
                url = f"{url.rstrip('/')}/{filename}"
            
            # Download file
            destination = self.temp_dir / filename
            
            self.logger.info(f"Downloading from: {url}")
            if not self.downloader.download_with_progress(url, str(destination)):
                return False
            
            # Verify checksum if available
            checksum = tool_config.get("checksum")
            if checksum and ":" in checksum:
                algo, expected_hash = checksum.split(":", 1)
                if not self.downloader.verify_checksum(str(destination), expected_hash, algo):
                    self.logger.warning(f"Checksum verification failed for {tool_name}")
                    # Don't fail on checksum mismatch for now
            
            return True
            
        except Exception as e:
            self.logger.error(f"Download failed: {str(e)}", e)
            return False
    
    def _execute_installation(self, tool_name: str, version: str, tool_config: dict) -> bool:
        """Execute installation process"""
        try:
            filename = tool_config.get("windows_filename", f"{tool_name}-{version}.zip")
            source_file = self.temp_dir / filename

            if not source_file.exists():
                self.logger.error(f"Installer file not found: {source_file}")
                return False
            
            # Create installation directory
            install_dir = self.config_manager.get_installation_directory() / tool_name
            install_dir.mkdir(parents=True, exist_ok=True)
            
            file_suffix = source_file.suffix.lower()

            if file_suffix == ".zip":
                self.logger.info(f"Extracting to: {install_dir}")
                with zipfile.ZipFile(source_file, 'r') as zip_ref:
                    zip_ref.extractall(install_dir)
            elif file_suffix == ".exe":
                installer_args = tool_config.get("windows_installer_args")
                if installer_args is None:
                    command = [str(source_file)]
                elif isinstance(installer_args, str):
                    command = [str(source_file)] + shlex.split(installer_args)
                else:
                    command = [str(source_file)] + list(installer_args)

                self.logger.info(f"Running installer: {' '.join(command)}")
                result = subprocess.run(command, check=False, capture_output=True, text=True)

                if result.returncode not in (0, 3010):
                    self.logger.error(
                        f"Installer failed with exit code {result.returncode}: {result.stderr.strip() or result.stdout.strip()}"
                    )
                    return False
            elif file_suffix == ".msi":
                installer_args = tool_config.get("windows_installer_args", ["/qn", "/norestart"])
                if isinstance(installer_args, str):
                    extra_args = shlex.split(installer_args)
                else:
                    extra_args = list(installer_args)

                command = ["msiexec", "/i", str(source_file)] + extra_args
                self.logger.info(f"Running installer: {' '.join(command)}")
                result = subprocess.run(command, check=False, capture_output=True, text=True)

                if result.returncode not in (0, 3010):
                    self.logger.error(
                        f"MSI installer failed with exit code {result.returncode}: {result.stderr.strip() or result.stdout.strip()}"
                    )
                    return False
            else:
                self.logger.error(f"Unsupported installer type: {file_suffix}")
                return False
            
            self.logger.success(f"Installation process completed for {tool_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Installation failed: {str(e)}", e)
            return False
    
    def _configure_tool(self, tool_name: str, tool_config: dict) -> bool:
        """Configure installed tool"""
        try:
            install_dir = self.config_manager.get_installation_directory() / tool_name
            
            # Add to PATH
            if tool_config.get("path_to_executable"):
                executable_cfg = Path(tool_config["path_to_executable"])
                executable_path = executable_cfg if executable_cfg.is_absolute() else install_dir / executable_cfg
                executable_dir = executable_path.parent

                if executable_dir.exists():
                    self.logger.info(f"Adding to PATH: {executable_dir}")
                    EnvironmentManager.add_to_path(str(executable_dir))
                else:
                    self.logger.warning(f"Skipping PATH update; directory not found: {executable_dir}")
            
            # Set environment variable if specified
            if tool_config.get("env_var_name"):
                env_var = tool_config["env_var_name"]
                self.logger.info(f"Setting {env_var} = {install_dir}")
                EnvironmentManager.set_environment_variable(env_var, str(install_dir))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration failed: {str(e)}", e)
            return False
    
    def _verify_installation(self, tool_name: str, tool_config: dict) -> bool:
        """Verify tool installation"""
        try:
            install_dir = self.config_manager.get_installation_directory() / tool_name

            executable_path = None
            executable_cfg = tool_config.get("path_to_executable")
            if executable_cfg:
                configured_path = Path(executable_cfg)
                executable_path = configured_path if configured_path.is_absolute() else install_dir / configured_path
                if executable_path.exists():
                    self.logger.success(f"Verified executable at {executable_path}")
                    return True

            # Fallback: verify by command availability.
            command_name = tool_config.get("command_name") or tool_name
            if ProcessManager.is_command_available(command_name):
                command_path = ProcessManager.get_command_path(command_name)
                self.logger.success(f"Verified command '{command_name}' at {command_path}")
                return True

            # Optional explicit paths to check for installer-based tools.
            for candidate in tool_config.get("verification_paths", []):
                candidate_path = Path(candidate)
                if candidate_path.exists():
                    self.logger.success(f"Verified installation via path {candidate_path}")
                    return True

            # If no executable path is configured, at least require install directory to exist.
            if not executable_cfg and install_dir.exists():
                self.logger.success(f"Verified installation directory at {install_dir}")
                return True

            if executable_path:
                self.logger.error(f"Executable not found: {executable_path}")
            else:
                self.logger.error(f"Could not verify installation for {tool_name}")
            return False
            
        except Exception as e:
            self.logger.error(f"Verification failed: {str(e)}", e)
            return False
    
    def uninstall_tool(self, tool_name: str) -> bool:
        """
        Uninstall a tool
        
        Args:
            tool_name: Tool to uninstall
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Uninstalling {tool_name}...")
            
            tool_config = self.config_manager.get_tool_config(tool_name)
            if not tool_config or not tool_config.get("installed"):
                self.logger.warning(f"{tool_name} is not installed")
                return False
            
            install_dir = self.config_manager.get_installation_directory() / tool_name
            
            # Remove installation directory
            if install_dir.exists():
                import shutil
                shutil.rmtree(install_dir)
                self.logger.info(f"Removed {install_dir}")
            
            # Update configuration
            self.config_manager.set_tool_installed(tool_name, False)
            
            self.logger.success(f"{tool_name} uninstalled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Uninstallation failed: {str(e)}", e)
            return False
    
    def cleanup_temp_files(self) -> bool:
        """Clean up temporary download files"""
        try:
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
                self.logger.info("Cleaned up temporary files")
            return True
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}", e)
            return False
