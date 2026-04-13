# API Reference - eSim Tool Manager

## Overview

This document provides API documentation for developers extending or integrating eSim Tool Manager.

## Table of Contents

1. [Core Modules](#core-modules)
2. [Utility Modules](#utility-modules)
3. [Configuration](#configuration)
4. [Examples](#examples)

## Core Modules

### ConfigManager

Manage tool and system configuration.

```python
from src.core import ConfigManager

config = ConfigManager(config_dir="./config")
```

#### Methods

**`get_tool_config(tool_name: str) -> Dict`**
```python
tool_config = config.get_tool_config("ngspice")
# Returns: {"name": "Ngspice", "current_version": "39", ...}
```

**`update_tool_config(tool_name: str, settings: Dict) -> bool`**
```python
success = config.update_tool_config("ngspice", {
    "current_version": "40",
    "install_path": "C:\\eSim\\Tools\\ngspice"
})
```

**`get_all_tools() -> Dict`**
```python
all_tools = config.get_all_tools()
# Returns all tool configurations as dictionary
```

**`get_installed_tools() -> Dict`**
```python
installed = config.get_installed_tools()
# Returns only installed tools
```

**`get_installation_directory() -> Path`**
```python
install_dir = config.get_installation_directory()
# Returns: Path("C:\\eSim\\Tools")
```

**`set_tool_installed(tool_name: str, installed: bool, path: str = None) -> bool`**
```python
config.set_tool_installed("ngspice", True, "C:\\eSim\\Tools\\ngspice")
```

**`update_tool_version(tool_name: str, version: str) -> bool`**
```python
config.update_tool_version("ngspice", "40")
```

### InstallationManager

Handle tool installation and setup.

```python
from src.core import InstallationManager

installer = InstallationManager(config_dir="./config")
```

#### Methods

**`install_tool(tool_name: str, version: str = None) -> bool`**
```python
success = installer.install_tool("ngspice", "39")
# Returns True if installation successful

# Install latest version
success = installer.install_tool("ngspice")
```

Installer behavior notes:
- Supports `.zip` packages (extract into managed install directory)
- Supports `.exe` and `.msi` installers (runs installer process)
- Resolves download URL templates with `{version}`, `{filename}`, and `{tool_name}` placeholders
- Verifies install via configured executable path, command lookup, or verification paths

**`uninstall_tool(tool_name: str) -> bool`**
```python
success = installer.uninstall_tool("ngspice")
# Returns True if uninstallation successful
```

**`cleanup_temp_files() -> bool`**
```python
cleaned = installer.cleanup_temp_files()
# Removes temporary download files
```

### UpdateChecker

Check for and manage tool updates.

```python
from src.core import UpdateChecker

updater = UpdateChecker(config_dir="./config")
```

#### Methods

**`check_updates(force: bool = False) -> Dict`**
```python
updates = updater.check_updates()
# Returns: {
#     "ngspice": {"current": "39", "latest": "40", "available": True},
#     "kicad": {"current": "9.0.0", "latest": "10.0.0-1", "available": True}
# }
```

**`check_tool_update(tool_name: str) -> Dict`**
```python
update_info = updater.check_tool_update("ngspice")
# Returns: {"tool": "ngspice", "current": "39", "latest": "40", "available": True}
```

**`perform_update(tool_name: str, target_version: str = None) -> bool`**
```python
success = updater.perform_update("ngspice", "40")

# Use latest version
success = updater.perform_update("ngspice")
```

**`perform_update_all() -> Dict`**
```python
results = updater.perform_update_all()
# Returns: {"ngspice": True, "kicad": True, ...}
```

## Utility Modules

### Logger

Centralized logging system.

```python
from src.utils import get_logger

logger = get_logger()
```

#### Methods

**`info(message: str, **kwargs)`**
```python
logger.info("Installation started")
```

**`error(message: str, exception: Exception = None, **kwargs)`**
```python
try:
    # code
except Exception as e:
    logger.error("Installation failed", e)
```

**`warning(message: str, **kwargs)`**
```python
logger.warning("Tool already installed")
```

**`success(message: str, **kwargs)`**
```python
logger.success("Installation completed")
```

**`get_action_history(last_n: int = None) -> List`**
```python
recent_actions = logger.get_action_history(10)  # Last 10 actions
all_actions = logger.get_action_history()       # All actions
```

### FileDownloader

Download files with progress tracking.

```python
from src.utils import FileDownloader

downloader = FileDownloader(timeout=300)
```

#### Methods

**`download_file(url: str, destination: str, progress_callback = None, verify_ssl = True) -> bool`**
```python
success = downloader.download_file(
    "https://example.com/tool.zip",
    "./downloads/tool.zip"
)
```

**`download_with_progress(url: str, destination: str) -> bool`**
```python
# Downloads with progress bar displayed
success = downloader.download_with_progress(
    "https://example.com/tool.zip",
    "./downloads/tool.zip"
)
```

**`verify_checksum(file_path: str, expected_hash: str, algorithm: str = "sha256") -> bool`**
```python
is_valid = downloader.verify_checksum(
    "./downloads/tool.zip",
    "abc123def456...",
    "sha256"
)
```

**`calculate_checksum(file_path: str, algorithm: str = "sha256") -> str`**
```python
hash_value = downloader.calculate_checksum("./tool.zip")
# Returns: "abc123def456..."
```

### DependencyChecker

Validate and manage dependencies.

```python
from src.utils import DependencyChecker

dep_checker = DependencyChecker(config_dir="./config")
```

#### Methods

**`check_dependencies(tool_name: str) -> Tuple[bool, List[str]]`**
```python
satisfied, missing = dep_checker.check_dependencies("ngspice")
# Returns: (False, ["vcredist", "python"])
```

**`get_dependency_tree(tool_name: str) -> Dict`**
```python
tree = dep_checker.get_dependency_tree("ngspice")
# Returns nested dependency information
```

**`validate_compatibility(tool_name: str, version: str) -> Tuple[bool, List[str]]`**
```python
is_compatible, issues = dep_checker.validate_compatibility("ngspice", "40")
```

**`get_missing_dependencies(tool_name: str) -> List[Dict]`**
```python
missing = dep_checker.get_missing_dependencies("ngspice")
# Returns list of missing dependencies with download info
```

### SystemInfo

Get system information.

```python
from src.utils import SystemInfo

# All methods are static
os_type = SystemInfo.get_os()  # "Windows"
py_version = SystemInfo.get_python_version()  # "3.8.10"
is_windows = SystemInfo.is_windows()  # True
```

#### Methods

- `get_os() -> str` - Get OS name
- `get_os_version() -> str` - Get OS version
- `get_python_version() -> str` - Get Python version
- `get_architecture() -> str` - Get system architecture (x86_64, etc.)
- `is_windows() -> bool` - Check if Windows
- `is_linux() -> bool` - Check if Linux
- `is_macos() -> bool` - Check if macOS
- `get_disk_free_space(path: str = ".") -> int` - Get free disk space in bytes

### EnvironmentManager

Manage environment variables and PATH.

```python
from src.utils import EnvironmentManager

# Add directory to PATH
EnvironmentManager.add_to_path("C:\\eSim\\Tools\\ngspice\\bin")

# Set environment variable
EnvironmentManager.set_environment_variable("NGSPICE_PATH", "C:\\eSim\\Tools\\ngspice")

# Get environment variable
value = EnvironmentManager.get_environment_variable("NGSPICE_PATH")
```

### ProcessManager

Manage system processes and commands.

```python
from src.utils import ProcessManager

# Check if command is available
available = ProcessManager.is_command_available("ngspice")

# Get command path
path = ProcessManager.get_command_path("ngspice")
# Returns: "C:\\eSim\\Tools\\ngspice\\bin\\ngspice.exe"

# Run command
result = ProcessManager.run_command("ngspice --version")
# Returns: {"returncode": 0, "stdout": "...", "stderr": "", "success": True}
```

## Configuration

### Tools Configuration (tools.json)

```json
{
  "tools": {
    "tool_name": {
      "name": "Tool Display Name",
      "description": "Tool description",
      "category": "simulator",
      "current_version": "1.0.0",
      "latest_version": "1.0.0",
      "windows_download_url": "https://...",
    "windows_filename": "tool-installer.exe",
      "dependencies": [],
    "path_to_executable": "bin/tool.exe",
    "command_name": "tool",
    "verification_paths": ["C:/Program Files/Tool/bin/tool.exe"],
    "windows_installer_args": ["/S"],
      "env_var_name": "TOOL_PATH",
      "installed": false,
      "install_path": null,
      "checksum": "sha256:abc123..."
    }
  }
}
```

### System Configuration (settings.json)

```json
{
  "system": {
    "installation_directory": "C:\\eSim\\Tools",
    "log_directory": "./logs",
    "auto_check_updates": true,
    "update_check_interval_days": 7,
    "download_timeout_seconds": 300,
    "verify_checksums": true,
    "retry_attempts": 3
  },
  "logging": {
    "level": "INFO",
    "format": "[%(asctime)s] [%(levelname)s] %(message)s",
    "max_file_size_mb": 10,
    "backup_count": 5
  }
}
```

## Examples

### Example 1: Basic Tool Installation

```python
from src.core import ConfigManager, InstallationManager

config = ConfigManager()
installer = InstallationManager()

# Check if tool is available
if config.get_tool_config("ngspice"):
    # Install tool
    if installer.install_tool("ngspice"):
        print("Installation successful!")
    else:
        print("Installation failed!")
```

### Example 2: Check and Install Updates

```python
from src.core import UpdateChecker

updater = UpdateChecker()

# Check for updates
updates = updater.check_updates()

# Install updates for tools that have them
for tool_name, info in updates.items():
    if info.get("available"):
        print(f"Updating {tool_name} to {info['latest']}...")
        updater.perform_update(tool_name)
```

### Example 3: Validate Dependencies

```python
from src.utils import DependencyChecker

dep_checker = DependencyChecker()

tool_name = "ngspice"
satisfied, missing = dep_checker.check_dependencies(tool_name)

if not satisfied:
    print(f"Missing dependencies for {tool_name}:")
    missing_deps = dep_checker.get_missing_dependencies(tool_name)
    for dep in missing_deps:
        print(f"  - {dep['name']}: {dep['download_url']}")
else:
    print(f"All dependencies for {tool_name} are satisfied")
```

### Example 4: Custom Installation Script

```python
from src.core import ConfigManager, InstallationManager
from src.utils import get_logger

logger = get_logger()
config = ConfigManager()
installer = InstallationManager()

tools_to_install = ["ngspice", "kicad", "python"]

for tool in tools_to_install:
    if config.get_tool_config(tool):
        logger.info(f"Installing {tool}...")
        if installer.install_tool(tool):
            logger.success(f"{tool} installed successfully")
        else:
            logger.error(f"Failed to install {tool}")
    else:
        logger.warning(f"Tool {tool} not found in configuration")

installer.cleanup_temp_files()
logger.info("Installation complete")
```

## Error Handling

Common exceptions and handling:

```python
from src.core import InstallationManager

installer = InstallationManager()

try:
    installer.install_tool("ngspice")
except Exception as e:
    logger.error(f"Installation error: {str(e)}", e)
```

## Best Practices

1. **Always cleanup**: Call `installer.cleanup_temp_files()` after installations
2. **Log operations**: Use logger for all significant operations
3. **Validate input**: Check tool exists before trying to install
4. **Handle exceptions**: Wrap operations in try-except blocks
5. **Check dependencies**: Validate dependencies before installation

---

**Version**: 1.0.0  
**Last Updated**: April 2026
