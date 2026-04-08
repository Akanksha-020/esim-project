"""
Tests for eSim Tool Manager
Unit and integration tests
"""

import pytest
import json
from pathlib import Path
from src.utils.logger import get_logger
from src.core.config_manager import ConfigManager
from src.utils.dependency_checker import DependencyChecker

class TestLogger:
    """Test logging functionality"""
    
    def test_logger_creation(self):
        """Test logger creation"""
        logger = get_logger()
        assert logger is not None
    
    def test_logger_info(self, tmp_path):
        """Test logger info method"""
        logger = get_logger()
        logger.info("Test message")
        # Check history
        history = logger.get_action_history()
        assert len(history) > 0

class TestConfigManager:
    """Test configuration management"""
    
    @pytest.fixture
    def config_dir(self, tmp_path):
        """Create test config directory"""
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        # Create test config files
        tools_config = {
            "tools": {
                "ngspice": {
                    "name": "Ngspice",
                    "current_version": "39",
                    "latest_version": "40",
                    "installed": False
                }
            }
        }
        
        with open(config_path / "tools.json", 'w') as f:
            json.dump(tools_config, f)
        
        settings_config = {
            "system": {
                "installation_directory": str(tmp_path / "tools"),
                "log_directory": str(tmp_path / "logs")
            }
        }
        
        with open(config_path / "settings.json", 'w') as f:
            json.dump(settings_config, f)
        
        return str(config_path)
    
    def test_config_manager_creation(self, config_dir):
        """Test config manager creation"""
        manager = ConfigManager(config_dir)
        assert manager is not None
    
    def test_get_tool_config(self, config_dir):
        """Test getting tool configuration"""
        manager = ConfigManager(config_dir)
        tool_config = manager.get_tool_config("ngspice")
        assert tool_config is not None
        assert tool_config["name"] == "Ngspice"
    
    def test_get_installation_directory(self, config_dir):
        """Test getting installation directory"""
        manager = ConfigManager(config_dir)
        install_dir = manager.get_installation_directory()
        assert install_dir is not None

class TestDependencyChecker:
    """Test dependency checking"""
    
    @pytest.fixture
    def config_dir(self, tmp_path):
        """Create test config directory"""
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        # Create test configs
        tools_config = {
            "tools": {
                "ngspice": {
                    "name": "Ngspice",
                    "dependencies": ["vcredist"],
                    "installed": False
                }
            }
        }
        
        deps_config = {
            "dependencies": {
                "vcredist": {
                    "name": "Visual C++ Redistributable",
                    "installed": False
                }
            }
        }
        
        with open(config_path / "tools.json", 'w') as f:
            json.dump(tools_config, f)
        
        with open(config_path / "dependencies.json", 'w') as f:
            json.dump(deps_config, f)
        
        return str(config_path)
    
    def test_dependency_checker_creation(self, config_dir):
        """Test dependency checker creation"""
        checker = DependencyChecker(config_dir)
        assert checker is not None
    
    def test_check_dependencies(self, config_dir):
        """Test dependency checking"""
        checker = DependencyChecker(config_dir)
        satisfied, missing = checker.check_dependencies("ngspice")
        # vcredist is not installed, so should be missing
        assert not satisfied or "vcredist" in missing

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
