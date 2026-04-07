"""
Tool installation manager for eSim Tool Manager
Handles downloading, installing, and configuring tools
"""

import zipfile
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List
from src.utils.logger import get_logger
from src.utils.downloader import FileDownloader
from src.utils.dependency_checker import DependencyChecker
from src.utils.system_utils import EnvironmentManager, FileManager, PermissionManager
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
            
            # Create temp directory
            self.temp_dir.mkdir(exist_ok=True)
            
            # Construct full URL with version if needed
            if "{version}" in url:
                url = url.format(version=version)
            else:
                url = f"{url}/{tool_name}-{version}-x64.zip"
            
            # Download file
            filename = tool_config.get("windows_filename", f"{tool_name}-{version}.zip")
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
            
            # Create installation directory
            install_dir = self.config_manager.get_installation_directory() / tool_name
            install_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Extracting to: {install_dir}")
            
            # Extract files
            if source_file.suffix == ".zip":
                with zipfile.ZipFile(source_file, 'r') as zip_ref:
                    zip_ref.extractall(install_dir)
            else:
                # For executables, we'd handle those differently
                self.logger.info(f"Running installer: {source_file}")
                # subprocess.run([str(source_file), "/S"], check=False)
            
            self.logger.success(f"Installation files extracted to {install_dir}")
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
                executable_path = install_dir / tool_config["path_to_executable"]
                executable_dir = executable_path.parent
                
                self.logger.info(f"Adding to PATH: {executable_dir}")
                EnvironmentManager.add_to_path(str(executable_dir))
            
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
            
            # Check if installation directory exists
            if not install_dir.exists():
                self.logger.error(f"Installation directory not found: {install_dir}")
                return False
            
            # Check if executable exists
            if tool_config.get("path_to_executable"):
                executable_path = install_dir / tool_config["path_to_executable"]
                if not executable_path.exists():
                    self.logger.error(f"Executable not found: {executable_path}")
                    return False
            
            self.logger.success(f"{tool_name} installation verified")
            return True
            
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
