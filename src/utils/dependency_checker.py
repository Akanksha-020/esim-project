"""
Dependency checker module for eSim Tool Manager
Validates and manages tool dependencies
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from src.utils.logger import get_logger
from src.utils.system_utils import ProcessManager, FileManager

class DependencyChecker:
    """Check and manage tool dependencies"""
    
    def __init__(self, config_dir: str = "./config"):
        """
        Initialize dependency checker
        
        Args:
            config_dir: Configuration directory path
        """
        self.config_dir = Path(config_dir)
        self.logger = get_logger()
        self.dependencies = self._load_dependencies()
        self.tools_config = self._load_tools_config()
    
    def _load_dependencies(self) -> Dict:
        """Load dependencies configuration"""
        try:
            with open(self.config_dir / "dependencies.json", 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load dependencies config: {str(e)}", e)
            return {"dependencies": {}}
    
    def _load_tools_config(self) -> Dict:
        """Load tools configuration"""
        try:
            with open(self.config_dir / "tools.json", 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load tools config: {str(e)}", e)
            return {"tools": {}}
    
    def check_dependencies(self, tool_name: str) -> Tuple[bool, List[str]]:
        """
        Check if all dependencies for a tool are installed
        
        Args:
            tool_name: Name of tool to check dependencies for
            
        Returns:
            Tuple of (all_satisfied, missing_dependencies)
        """
        self.logger.info(f"Checking dependencies for {tool_name}...")
        
        tool = self.tools_config.get("tools", {}).get(tool_name)
        if not tool:
            self.logger.warning(f"Tool {tool_name} not found in configuration")
            return False, []
        
        dependencies = tool.get("dependencies", [])
        missing = []
        
        for dep in dependencies:
            if not self._is_dependency_installed(dep):
                missing.append(dep)
                self.logger.warning(f"Missing dependency: {dep}")
            else:
                self.logger.debug(f"Dependency satisfied: {dep}")
        
        if missing:
            self.logger.warning(f"Missing {len(missing)} dependencies")
            return False, missing
        else:
            self.logger.success(f"All dependencies for {tool_name} are satisfied")
            return True, []
    
    def _is_dependency_installed(self, dep_name: str) -> bool:
        """
        Check if a dependency is installed
        
        Args:
            dep_name: Dependency name
            
        Returns:
            True if installed
        """
        dep = self.dependencies.get("dependencies", {}).get(dep_name)
        
        if not dep:
            self.logger.debug(f"Dependency {dep_name} not found in config")
            return False
        
        # Check if it's a command in PATH
        if ProcessManager.is_command_available(dep_name):
            return True
        
        # Check install path if specified
        if dep.get("installed"):
            return True
        
        # Check for Windows registry (for redistributables)
        if dep_name == "vcredist":
            return self._check_vcredist_installed()
        
        return False
    
    def _check_vcredist_installed(self) -> bool:
        """Check if Visual C++ Redistributable is installed"""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64")
            version, _ = winreg.QueryValueEx(key, "Version")
            winreg.CloseKey(key)
            return True
        except Exception:
            return False
    
    def get_dependency_tree(self, tool_name: str) -> Dict:
        """
        Get dependency tree for a tool
        
        Args:
            tool_name: Tool name
            
        Returns:
            Dependency tree
        """
        tool = self.tools_config.get("tools", {}).get(tool_name)
        if not tool:
            return {}
        
        tree = {
            "tool": tool_name,
            "dependencies": tool.get("dependencies", []),
            "dependency_details": {}
        }
        
        for dep in tool.get("dependencies", []):
            dep_info = self.dependencies.get("dependencies", {}).get(dep, {})
            tree["dependency_details"][dep] = {
                "installed": self._is_dependency_installed(dep),
                "version": dep_info.get("version"),
                "required_for": dep_info.get("required_by", [])
            }
        
        return tree
    
    def validate_compatibility(
        self,
        tool_name: str,
        version: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate tool compatibility
        
        Args:
            tool_name: Tool name
            version: Version to check
            
        Returns:
            Tuple of (is_compatible, issues)
        """
        issues = []
        tool = self.tools_config.get("tools", {}).get(tool_name)
        
        if not tool:
            issues.append(f"Tool {tool_name} not found")
            return False, issues
        
        # Check if version is available
        if version != tool.get("latest_version"):
            issues.append(f"Version {version} may not be the latest ({tool.get('latest_version')})")
        
        # Check dependencies compatibility
        deps_satisfied, missing = self.check_dependencies(tool_name)
        if not deps_satisfied:
            issues.append(f"Missing dependencies: {', '.join(missing)}")
        
        return len(issues) == 0, issues
    
    def get_missing_dependencies(self, tool_name: str) -> List[Dict]:
        """
        Get list of missing dependencies with download info
        
        Args:
            tool_name: Tool name
            
        Returns:
            List of missing dependency info
        """
        _, missing = self.check_dependencies(tool_name)
        
        missing_deps = []
        for dep_name in missing:
            dep = self.dependencies.get("dependencies", {}).get(dep_name, {})
            missing_deps.append({
                "name": dep_name,
                "description": dep.get("description"),
                "download_url": dep.get("windows_download_url"),
                "version": dep.get("version")
            })
        
        return missing_deps
    
    def mark_dependency_installed(self, dep_name: str, status: bool = True):
        """Mark a dependency as installed"""
        try:
            deps = self.dependencies.get("dependencies", {})
            if dep_name in deps:
                deps[dep_name]["installed"] = status
                # Save to config
                with open(self.config_dir / "dependencies.json", 'w') as f:
                    json.dump(self.dependencies, f, indent=2)
                self.logger.info(f"Marked {dep_name} as installed: {status}")
        except Exception as e:
            self.logger.error(f"Failed to update dependency status: {str(e)}", e)
    
    def print_dependency_report(self, tool_name: str):
        """Print dependency report for a tool"""
        try:
            tree = self.get_dependency_tree(tool_name)
            print(f"\nDependency Report for {tool_name}:")
            print("=" * 50)
            
            if not tree.get("dependencies"):
                print("No dependencies required.")
                return
            
            for dep_name, dep_info in tree.get("dependency_details", {}).items():
                status = "✓ Installed" if dep_info["installed"] else "✗ Missing"
                version = dep_info.get("version", "N/A")
                print(f"  {dep_name:20} {status:20} v{version}")
            
            print("=" * 50)
            
        except Exception as e:
            self.logger.error(f"Error printing report: {str(e)}", e)
