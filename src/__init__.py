"""
eSim Automated Tool Manager
Automated installation, configuration, updates, and management of external tools
"""

__version__ = "1.0.0"
__author__ = "eSim Summer Fellowship 2026"
__description__ = "Automated Tool Manager for eSim"

from src.core import ConfigManager, InstallationManager, UpdateChecker
from src.utils import (
    get_logger,
    FileDownloader,
    DependencyChecker,
    SystemInfo,
    EnvironmentManager,
    ProcessManager,
    FileManager,
    PermissionManager
)

__all__ = [
    'ConfigManager',
    'InstallationManager',
    'UpdateChecker',
    'get_logger',
    'FileDownloader',
    'DependencyChecker',
    'SystemInfo',
    'EnvironmentManager',
    'ProcessManager',
    'FileManager',
    'PermissionManager'
]
