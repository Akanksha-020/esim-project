"""
System utilities for eSim Tool Manager
Handles OS-specific operations and environment variable management
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional, List, Dict
import shutil
import winreg  # Windows registry

class SystemInfo:
    """Get system information"""
    
    @staticmethod
    def get_os() -> str:
        """Get operating system"""
        return platform.system()
    
    @staticmethod
    def get_os_version() -> str:
        """Get OS version"""
        return platform.version()
    
    @staticmethod
    def get_python_version() -> str:
        """Get Python version"""
        return platform.python_version()
    
    @staticmethod
    def get_architecture() -> str:
        """Get system architecture (32-bit or 64-bit)"""
        return platform.machine()
    
    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows"""
        return platform.system() == "Windows"
    
    @staticmethod
    def is_linux() -> bool:
        """Check if running on Linux"""
        return platform.system() == "Linux"
    
    @staticmethod
    def is_macos() -> bool:
        """Check if running on macOS"""
        return platform.system() == "Darwin"
    
    @staticmethod
    def get_disk_free_space(path: str = ".") -> int:
        """
        Get free disk space in bytes
        
        Args:
            path: Path to check
            
        Returns:
            Free space in bytes
        """
        import shutil
        stat = shutil.disk_usage(path)
        return stat.free


class EnvironmentManager:
    """Manage environment variables and PATH"""
    
    @staticmethod
    def add_to_path(directory: str) -> bool:
        """
        Add directory to system PATH
        
        Args:
            directory: Directory path to add
            
        Returns:
            True if successful
        """
        if SystemInfo.is_windows():
            return EnvironmentManager._add_to_path_windows(directory)
        elif SystemInfo.is_linux() or SystemInfo.is_macos():
            return EnvironmentManager._add_to_path_unix(directory)
        return False
    
    @staticmethod
    def _add_to_path_windows(directory: str) -> bool:
        """Add directory to PATH on Windows"""
        try:
            # Access Windows registry
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment",
                0,
                winreg.KEY_READ | winreg.KEY_WRITE
            )
            
            # Get current PATH
            current_path, _ = winreg.QueryValueEx(key, "Path")
            
            # Check if already in PATH
            if directory in current_path:
                winreg.CloseKey(key)
                return True
            
            # Add to PATH
            new_path = f"{current_path};{directory}"
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
            
            # Notify system of PATH change
            os.system(f'setx PATH "{new_path}"')
            return True
            
        except Exception as e:
            print(f"Error adding to PATH: {e}")
            return False
    
    @staticmethod
    def _add_to_path_unix(directory: str) -> bool:
        """Add directory to PATH on Unix-like systems"""
        try:
            # This is a simplified version, actual implementation would modify shell rc files
            os.environ["PATH"] = f"{directory}:{os.environ.get('PATH', '')}"
            return True
        except Exception:
            return False
    
    @staticmethod
    def set_environment_variable(name: str, value: str) -> bool:
        """
        Set environment variable
        
        Args:
            name: Variable name
            value: Variable value
            
        Returns:
            True if successful
        """
        try:
            if SystemInfo.is_windows():
                os.system(f'setx {name} "{value}"')
            else:
                os.environ[name] = value
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_environment_variable(name: str) -> Optional[str]:
        """Get environment variable"""
        return os.environ.get(name)


class ProcessManager:
    """Manage system processes"""
    
    @staticmethod
    def is_command_available(command: str) -> bool:
        """
        Check if a command is available in PATH
        
        Args:
            command: Command name to check
            
        Returns:
            True if command is available
        """
        return shutil.which(command) is not None
    
    @staticmethod
    def get_command_path(command: str) -> Optional[str]:
        """
        Get full path to a command
        
        Args:
            command: Command name
            
        Returns:
            Full path to command or None
        """
        return shutil.which(command)
    
    @staticmethod
    def run_command(command: str, shell: bool = False) -> Dict[str, any]:
        """
        Run a system command
        
        Args:
            command: Command to run
            shell: Whether to use shell
            
        Returns:
            Dictionary with returncode, stdout, stderr
        """
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timeout",
                "success": False
            }
        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }
    
    @staticmethod
    def get_process_info(process_name: str) -> Optional[Dict]:
        """Get information about a running process"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                if process_name.lower() in proc.info['name'].lower():
                    return {
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "running": True
                    }
        except Exception:
            pass
        return {"running": False}


class FileManager:
    """Manage file operations"""
    
    @staticmethod
    def verify_path_exists(path: str) -> bool:
        """Check if path exists"""
        return Path(path).exists()
    
    @staticmethod
    def create_directory(path: str, exist_ok: bool = True) -> bool:
        """
        Create directory
        
        Args:
            path: Directory path
            exist_ok: If True, don't raise error if exists
            
        Returns:
            True if successful or already exists
        """
        try:
            Path(path).mkdir(parents=True, exist_ok=exist_ok)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_directory_size(path: str) -> int:
        """
        Get total size of directory in bytes
        
        Args:
            path: Directory path
            
        Returns:
            Size in bytes
        """
        total = 0
        try:
            for entry in Path(path).rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except Exception:
            pass
        return total
    
    @staticmethod
    def list_files(path: str, pattern: str = "*") -> List[str]:
        """
        List files in directory
        
        Args:
            path: Directory path
            pattern: File pattern (e.g., "*.exe")
            
        Returns:
            List of file paths
        """
        try:
            return [str(f) for f in Path(path).glob(pattern)]
        except Exception:
            return []


class PermissionManager:
    """Check and manage file permissions"""
    
    @staticmethod
    def has_write_permission(path: str) -> bool:
        """Check if path is writable"""
        try:
            # Try to write a test file
            test_file = Path(path) / ".permission_test"
            test_file.touch()
            test_file.unlink()
            return True
        except PermissionError:
            return False
        except Exception:
            return os.access(path, os.W_OK)
    
    @staticmethod
    def has_read_permission(path: str) -> bool:
        """Check if path is readable"""
        return os.access(path, os.R_OK)
    
    @staticmethod
    def is_admin() -> bool:
        """Check if running with admin privileges"""
        try:
            if SystemInfo.is_windows():
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except Exception:
            return False
