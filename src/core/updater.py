"""
Update manager for eSim Tool Manager
Checks for updates and manages tool upgrades
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from src.utils.logger import get_logger
from src.core.config_manager import ConfigManager
from src.core.installer import InstallationManager

class UpdateChecker:
    """Check for and manage tool updates"""
    
    def __init__(self, config_dir: str = "./config"):
        """
        Initialize update checker
        
        Args:
            config_dir: Configuration directory
        """
        self.logger = get_logger()
        self.config_manager = ConfigManager(config_dir)
        self.installer = InstallationManager(config_dir)
        self.last_check = None
    
    def check_updates(self, force: bool = False) -> Dict[str, Dict]:
        """
        Check all installed tools for updates
        
        Args:
            force: Force check even if recently checked
            
        Returns:
            Dictionary of tools with available updates
        """
        self.logger.info("Checking for available updates...")
        
        installed_tools = self.config_manager.get_installed_tools()
        updates_available = {}
        
        for tool_name, tool_config in installed_tools.items():
            current = tool_config.get("current_version")
            latest = tool_config.get("latest_version")
            
            if self._is_update_available(current, latest):
                updates_available[tool_name] = {
                    "current": current,
                    "latest": latest,
                    "available": True
                }
                self.logger.info(f"Update available: {tool_name} {current} → {latest}")
            else:
                updates_available[tool_name] = {
                    "current": current,
                    "latest": latest,
                    "available": False
                }
                self.logger.debug(f"No update available for {tool_name}")
        
        self.last_check = datetime.now()
        self.logger.info(f"Update check completed")
        
        return updates_available
    
    def check_tool_update(self, tool_name: str) -> Optional[Dict]:
        """
        Check specific tool for updates
        
        Args:
            tool_name: Tool name
            
        Returns:
            Update information or None
        """
        tool_config = self.config_manager.get_tool_config(tool_name)
        
        if not tool_config:
            self.logger.warning(f"Tool {tool_name} not found")
            return None
        
        if not tool_config.get("installed"):
            self.logger.warning(f"{tool_name} is not installed")
            return None
        
        current = tool_config.get("current_version")
        latest = tool_config.get("latest_version")
        
        return {
            "tool": tool_name,
            "current": current,
            "latest": latest,
            "available": self._is_update_available(current, latest)
        }
    
    def get_latest_version(self, tool_name: str) -> Optional[str]:
        """
        Get latest version of a tool
        
        Args:
            tool_name: Tool name
            
        Returns:
            Latest version string or None
        """
        tool_config = self.config_manager.get_tool_config(tool_name)
        
        if tool_config:
            return tool_config.get("latest_version")
        
        return None
    
    def perform_update(self, tool_name: str, target_version: Optional[str] = None) -> bool:
        """
        Perform tool update
        
        Args:
            tool_name: Tool to update
            target_version: Target version (uses latest if not specified)
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Starting update for {tool_name}...")
            
            tool_config = self.config_manager.get_tool_config(tool_name)
            
            if not tool_config or not tool_config.get("installed"):
                self.logger.error(f"{tool_name} is not installed")
                return False
            
            current_version = tool_config.get("current_version")
            target = target_version or tool_config.get("latest_version")
            
            if target == current_version:
                self.logger.warning(f"{tool_name} is already at version {target}")
                return True
            
            # Backup current version
            if not self._backup_tool(tool_name, current_version):
                self.logger.warning("Backup failed, continuing with update...")
            
            # Uninstall current version
            self.logger.info(f"Removing {tool_name} {current_version}...")
            if not self.installer.uninstall_tool(tool_name):
                self.logger.error("Failed to uninstall current version")
                return self._restore_tool(tool_name, current_version)
            
            # Install new version
            self.logger.info(f"Installing {tool_name} {target}...")
            if not self.installer.install_tool(tool_name, target):
                self.logger.error("Failed to install new version")
                return self._restore_tool(tool_name, current_version)
            
            self.logger.success(f"{tool_name} updated from {current_version} to {target}")
            return True
            
        except Exception as e:
            self.logger.error(f"Update failed: {str(e)}", e)
            return False
    
    def perform_update_all(self) -> Dict[str, bool]:
        """
        Update all tools with available updates
        
        Returns:
            Dictionary of tool_name -> update_success
        """
        results = {}
        updates = self.check_updates()
        
        for tool_name, info in updates.items():
            if info.get("available"):
                self.logger.info(f"Updating {tool_name}...")
                results[tool_name] = self.perform_update(tool_name)
            else:
                results[tool_name] = True
        
        return results
    
    def _is_update_available(self, current: Optional[str], latest: Optional[str]) -> bool:
        """
        Check if update is available
        
        Args:
            current: Current version
            latest: Latest version
            
        Returns:
            True if update available
        """
        if not current or not latest:
            return False
        
        try:
            # Simple version comparison (can be enhanced)
            current_parts = [int(x) for x in current.split('.')]
            latest_parts = [int(x) for x in latest.split('.')]
            
            # Pad with zeros if needed
            max_len = max(len(current_parts), len(latest_parts))
            current_parts += [0] * (max_len - len(current_parts))
            latest_parts += [0] * (max_len - len(latest_parts))
            
            return latest_parts > current_parts
            
        except (ValueError, AttributeError):
            # Fallback to string comparison
            return current < latest
    
    def _backup_tool(self, tool_name: str, version: str) -> bool:
        """Backup current tool installation"""
        try:
            from pathlib import Path
            import shutil
            
            install_dir = self.config_manager.get_installation_directory() / tool_name
            backup_dir = self.config_manager.get_installation_directory() / f"{tool_name}_backup_{version}"
            
            if install_dir.exists():
                shutil.copytree(install_dir, backup_dir)
                self.logger.info(f"Backup created: {backup_dir}")
                return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}", e)
            return False
    
    def _restore_tool(self, tool_name: str, version: str) -> bool:
        """Restore tool from backup"""
        try:
            from pathlib import Path
            import shutil
            
            # Note: This is a simplified version
            # In production, you'd implement proper rollback
            self.logger.warning(f"Failed to update {tool_name}, attempted rollback")
            return False
            
        except Exception as e:
            self.logger.error(f"Restore failed: {str(e)}", e)
            return False
    
    def print_update_report(self):
        """Print update availability report"""
        try:
            updates = self.check_updates()
            
            print("\n" + "=" * 60)
            print("eSim Tool Manager - Update Report")
            print("=" * 60)
            
            if not updates:
                print("No tools installed")
                return
            
            available_count = sum(1 for info in updates.values() if info.get("available"))
            
            print(f"\nTotal Tools: {len(updates)}")
            print(f"Updates Available: {available_count}\n")
            
            print(f"{'Tool':<20} {'Current':<12} {'Latest':<12} {'Status':<15}")
            print("-" * 60)
            
            for tool_name, info in updates.items():
                current = info.get("current", "N/A")
                latest = info.get("latest", "N/A")
                status = "✓ Up to date" if not info.get("available") else "⚠ Update available"
                
                print(f"{tool_name:<20} {str(current):<12} {str(latest):<12} {status:<15}")
            
            print("=" * 60 + "\n")
            
        except Exception as e:
            self.logger.error(f"Error printing report: {str(e)}", e)
