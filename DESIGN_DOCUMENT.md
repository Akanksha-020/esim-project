# eSim Automated Tool Manager - Design Document

## Executive Summary
The **eSim Automated Tool Manager** is a comprehensive Python-based application that automates the installation, configuration, updates, and dependency management of external tools required by eSim. The tool is designed with a modular architecture to support Windows initially, with extensibility for Linux and macOS.

## 1. Architecture Overview

### 1.1 System Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Interface Layer                      │
│  (Command Parser, User Interactions, Output Formatting)    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Tool Manager Core                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Installation │  │   Updates    │  │ Configuration│      │
│  │   Manager    │  │   Checker    │  │   Handler    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                 Utility Modules                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Downloader   │  │   Logger     │  │ Dependencies │      │
│  │              │  │              │  │   Checker    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  External Resources (APIs, Package Managers, Repositories)  │
└─────────────────────────────────────────────────────────────┘
```

## 2. Module Breakdown

### 2.1 Core Modules

#### **Installation Manager** (`src/core/installer.py`)
- **Purpose**: Handles tool discovery, download, and installation
- **Key Functions**:
  - `install_tool(tool_name, version)`: Install a specific tool with version
  - `verify_installation(tool_path)`: Verify tool is installed correctly
  - `set_environment_variables(tool_name, tool_path)`: Configure PATH and env vars
  - `handle_dependencies(tool_name)`: Install prerequisites

#### **Update Checker** (`src/core/updater.py`)
- **Purpose**: Checks for available updates and manages upgrades
- **Key Functions**:
  - `check_updates()`: Check all installed tools for updates
  - `check_tool_update(tool_name)`: Check specific tool for updates
  - `get_latest_version(tool_name)`: Fetch latest version from repository
  - `perform_update(tool_name, version)`: Execute update process
  - `rollback_update(tool_name)`: Rollback to previous version if needed

#### **Configuration Handler** (`src/core/config_manager.py`)
- **Purpose**: Manages tool configurations and settings
- **Key Functions**:
  - `load_config(config_file)`: Load configuration from JSON/YAML
  - `save_config(config_data)`: Persist configuration changes
  - `get_tool_config(tool_name)`: Retrieve tool-specific settings
  - `update_config(tool_name, settings)`: Update tool settings
  - `validate_config(config_data)`: Validate configuration structure

### 2.2 Utility Modules

#### **Downloader** (`src/utils/downloader.py`)
- **Purpose**: Handle file downloads with progress tracking
- **Key Functions**:
  - `download_file(url, destination)`: Download with progress indicator
  - `verify_checksum(file_path, expected_hash)`: Verify file integrity
  - `get_download_url(tool_name, version)`: Resolve download URL

#### **Dependency Checker** (`src/utils/dependency_checker.py`)
- **Purpose**: Validate and manage tool dependencies
- **Key Functions**:
  - `check_dependencies(tool_name)`: Check if dependencies are installed
  - `resolve_missing_dependencies(tool_name)`: Auto-install missing deps
  - `get_dependency_tree(tool_name)`: Build dependency graph
  - `validate_compatibility(tool_name, version)`: Check OS/version compatibility

#### **Logger** (`src/utils/logger.py`)
- **Purpose**: Centralized logging for all operations
- **Key Functions**:
  - `log_action(action, details)`: Log operations with timestamps
  - `log_error(error_msg, exception)`: Log errors and exceptions
  - `get_log_history()`: Retrieve action history

### 2.3 UI/CLI Module

#### **Command Line Interface** (`src/ui/cli.py`)
- **Purpose**: User-friendly command-line interface
- **Commands**:
  - `tmgr install <tool> [--version V]`: Install a tool
  - `tmgr update [<tool> | --all]`: Update tools
  - `tmgr list-tools`: Show installed tools and versions
  - `tmgr checks-updates`: Check available updates
  - `tmgr status <tool>`: Show tool status
  - `tmgr logs [--last N]`: Display action logs
  - `tmgr config <tool>`: Show/edit tool configuration
  - `tmgr uninstall <tool>`: Remove a tool

## 3. Data Flow

### 3.1 Installation Flow
```
User Command
    ↓
CLI Parser → Installation Manager
    ↓
Check Dependencies → Downloader
    ↓
Verify Download → Extract/Setup
    ↓
Configure Environment
    ↓
Verify Installation
    ↓
Log Action → Complete
```

### 3.2 Update Flow
```
User Command (update)
    ↓
Update Checker → Fetch Latest Versions
    ↓
Compare Installed vs Latest
    ↓
Show Available Updates
    ↓
User Confirmation
    ↓
Installation Manager (upgrade)
    ↓
Verify Update → Log Action
```

## 4. Configuration Schema

### 4.1 Tool Definition (`config/tools.json`)
```json
{
  "tools": {
    "ngspice": {
      "name": "Ngspice",
      "description": "Open-source circuit simulator",
      "current_version": "39",
      "latest_version": "39",
      "windows_download_url": "https://sourceforge.net/projects/ngspice/files/ng-spice-rework/",
      "description": "Circuit simulator for eSim",
      "dependencies": ["vcredist"],
      "path_to_executable": "bin/ngspice.exe",
      "installed": true,
      "install_path": "C:\\eSim\\Tools\\ngspice"
    },
    "kicad": {
      "name": "KiCad",
      "description": "PCB design software",
      "current_version": null,
      "latest_version": "10.0.0-1",
      "windows_download_url": "https://kicad-downloads.s3.cern.ch/windows/stable/{filename}",
      "dependencies": [],
      "installed": false,
      "install_path": null
    }
  }
}
```

### 4.2 System Configuration (`config/settings.json`)
```json
{
  "system": {
    "installation_directory": "C:\\eSim\\Tools",
    "log_directory": "./logs",
    "auto_check_updates": true,
    "update_check_interval_days": 7,
    "download_timeout_seconds": 300,
    "verify_checksums": true
  },
  "platform": "windows",
  "python_version": "3.8+"
}
```

## 5. Component Interactions

### 5.1 Sequence Diagram - Installation
```
User → CLI: install ngspice --version 39
CLI → InstallationMgr: install_tool("ngspice", "39")
InstallationMgr → DependencyChecker: check_dependencies("ngspice")
DependencyChecker → Logger: log_action("Dependencies checked")
InstallationMgr → Downloader: download_file(url, dest)
Downloader → Logger: log_action("File downloaded")
InstallationMgr → Installer: extract_and_setup(file)
Installer → ConfigManager: set_environment_variables()
ConfigManager → Logger: log_action("Environment configured")
InstallationMgr → CLI: Installation complete
```

### 5.2 Sequence Diagram - Update
```
User → CLI: checks-updates
CLI → UpdateChecker: check_updates()
UpdateChecker → RepositoryAPI: get_latest_versions()
UpdateChecker → Logger: log_action("Updates checked")
UpdateChecker → CLI: Display available updates
User → CLI: update ngspice
CLI → UpdateChecker: perform_update("ngspice", None)
UpdateChecker → InstallationMgr: install_tool("ngspice", latest)
(Installation flow continues...)
UpdateChecker → Logger: log_action("Update completed")
```

## 6. Error Handling

### 6.1 Error Categories
- **Network Errors**: Download failures, timeout, connectivity issues
- **Installation Errors**: Insufficient permissions, disk space, missing dependencies
- **Configuration Errors**: Invalid parameters, corrupted config files
- **Compatibility Errors**: Unsupported OS, Python version, dependencies

### 6.2 Recovery Strategies
- **Automatic Retry**: Network operations with exponential backoff
- **Rollback Support**: Revert to previous version on failed updates
- **Dependency Resolution**: Auto-install missing dependencies
- **User Notification**: Clear error messages with resolution suggestions

## 7. Security Considerations

- **Checksum Verification**: Verify downloaded files against published checksums
- **HTTPS Downloads**: Use secure connections for file downloads
- **Path Validation**: Validate and sanitize file paths
- **Permission Checks**: Verify sufficient permissions before operations
- **Audit Logging**: Log all installation and modification actions

## 8. Extensibility

The design supports future extensions:
- **Additional Tools**: Add new tools via configuration
- **Package Managers**: Integration with Chocolatey, Winget
- **Platform Support**: Extend to Linux, macOS with platform-specific modules
- **GUI Interface**: Parallel CLI with GUI implementation
- **Update Channels**: Support beta, stable release channels

## 9. Technology Stack

- **Language**: Python 3.8+
- **Core Libraries**: 
  - `requests`: HTTP downloads
  - `click`: CLI framework
  - `pyyaml`/`json`: Configuration files
  - `logging`: System logging
- **Platform**: Windows (extendable to Linux/macOS)

## 10. Deployment

- **Installation**: pip-based installation
- **Configuration**: JSON-based config files
- **Logging**: Local log files with rotation
- **Portability**: Standalone executable or Python package

---

**Document Version**: 1.0  
**Last Updated**: April 2026  
**Status**: Design Phase Complete
