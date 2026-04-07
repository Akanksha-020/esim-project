"""
Configuration manager for eSim Tool Manager
Manages tool settings and system configuration
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from src.utils.logger import get_logger

class ConfigManager:
    """Manage tool and system configuration"""
    
    def __init__(self, config_dir: str = "./config"):
        """
        Initialize configuration manager
        
        Args:
            config_dir: Configuration directory path
        """
        self.config_dir = Path(config_dir)
        self.logger = get_logger()
        self.tools_config = self._load_config("tools.json")
        self.system_config = self._load_config("settings.json")
    
    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration file"""
        try:
            config_path = self.config_dir / filename
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Config file not found: {filename}")
                return {}
        except Exception as e:
            self.logger.error(f"Failed to load config {filename}: {str(e)}", e)
            return {}
    
    def _save_config(self, filename: str, data: Dict[str, Any]) -> bool:
        """Save configuration file"""
        try:
            config_path = self.config_dir / filename
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"Configuration saved: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save config {filename}: {str(e)}", e)
            return False
    
    def get_tool_config(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific tool
        
        Args:
            tool_name: Tool name
            
        Returns:
            Tool configuration dictionary
        """
        return self.tools_config.get("tools", {}).get(tool_name)
    
    def update_tool_config(
        self,
        tool_name: str,
        settings: Dict[str, Any]
    ) -> bool:
        """
        Update tool configuration
        
        Args:
            tool_name: Tool name
            settings: Settings to update
            
        Returns:
            True if successful
        """
        try:
            if "tools" not in self.tools_config:
                self.tools_config["tools"] = {}
            
            if tool_name not in self.tools_config["tools"]:
                self.tools_config["tools"][tool_name] = {}
            
            # Update settings
            self.tools_config["tools"][tool_name].update(settings)
            
            # Save changes
            return self._save_config("tools.json", self.tools_config)
            
        except Exception as e:
            self.logger.error(f"Failed to update tool config: {str(e)}", e)
            return False
    
    def get_system_config(self, key: Optional[str] = None) -> Any:
        """
        Get system configuration
        
        Args:
            key: Optional specific key to retrieve
            
        Returns:
            Configuration value or dict
        """
        if key:
            return self.system_config.get(key)
        return self.system_config
    
    def get_installation_directory(self) -> Path:
        """Get tool installation directory"""
        default = "C:\\eSim\\Tools"
        install_dir = self.system_config.get("system", {}).get(
            "installation_directory",
            default
        )
        return Path(install_dir)
    
    def get_log_directory(self) -> Path:
        """Get log directory"""
        log_dir = self.system_config.get("system", {}).get(
            "log_directory",
            "./logs"
        )
        return Path(log_dir)
    
    def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all tools configuration"""
        return self.tools_config.get("tools", {})
    
    def get_installed_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get only installed tools"""
        all_tools = self.get_all_tools()
        return {
            tool_name: tool_config
            for tool_name, tool_config in all_tools.items()
            if tool_config.get("installed", False)
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate configuration structure
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        # Check required sections
        if "tools" in config:
            for tool_name, tool_config in config["tools"].items():
                if not isinstance(tool_config, dict):
                    errors.append(f"Tool {tool_name} config must be a dictionary")
                
                # Check required fields
                required_fields = ["name", "current_version", "latest_version"]
                for field in required_fields:
                    if field not in tool_config:
                        errors.append(f"Tool {tool_name} missing required field: {field}")
        
        return len(errors) == 0, errors
    
    def reload_config(self) -> bool:
        """Reload configuration from files"""
        try:
            self.tools_config = self._load_config("tools.json")
            self.system_config = self._load_config("settings.json")
            self.logger.info("Configuration reloaded")
            return True
        except Exception as e:
            self.logger.error(f"Failed to reload config: {str(e)}", e)
            return False
    
    def set_tool_installed(self, tool_name: str, installed: bool, path: Optional[str] = None) -> bool:
        """
        Mark tool as installed/uninstalled
        
        Args:
            tool_name: Tool name
            installed: Installation status
            path: Installation path (if installed)
            
        Returns:
            True if successful
        """
        settings = {
            "installed": installed,
            "install_path": path if installed else None
        }
        return self.update_tool_config(tool_name, settings)
    
    def update_tool_version(self, tool_name: str, version: str) -> bool:
        """
        Update tool version
        
        Args:
            tool_name: Tool name
            version: New version
            
        Returns:
            True if successful
        """
        return self.update_tool_config(tool_name, {"current_version": version})
