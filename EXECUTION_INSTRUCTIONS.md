# Execution Instructions - eSim Tool Manager

## Quick Start Guide

Complete instructions on how to run and test the eSim Automated Tool Manager prototype.

## Prerequisites Checklist

Before executing, ensure you have:

- ✅ Windows 10/11 OS
- ✅ Python 3.8 or higher installed
- ✅ Administrator access (for PATH/registry modifications)
- ✅ Internet connection (for tool downloads)
- ✅ 5 GB free disk space
- ✅ Git installed (for version control)

## Step 1: Clone Repository

```bash
# Clone the eSim Tool Manager repository
git clone <repository-url> esim-tool-manager
cd esim-tool-manager

# Verify structure
dir

# Expected output:
# config/
# docs/
# logs/
# src/
# tests/
# main.py
# requirements.txt
# etc.
```

## Step 2: Setup Python Environment

### Option A: Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows Command Prompt:
venv\Scripts\activate

# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# If you get execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# On Linux/macOS:
source venv/bin/activate

# Verify activation (you should see (venv) in command prompt)
```

### Option B: Using System Python

```bash
# Skip if using venv (Step 2A)
python --version  # Verify 3.8+
```

## Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list

# Should see: click, requests, pyyaml, colorlog, tqdm, etc.
```

## Step 4: Verify Installation

```bash
# Test basic functionality
python main.py --version
# Expected: Should display version information

python main.py --help
# Expected: Should show available commands
```

## Step 5: Run the Tool Manager

### Using Help

```bash
# Get general help
python main.py --help

# Get command-specific help
python main.py install --help
python main.py update --help
python main.py list-tools --help
```

### Using Interactive Mode

```bash
# Start interactive shell
python main.py

# Example session
tool-manager> list-tools
tool-manager> checks-updates
tool-manager> exit
```

### Basic Operations

#### 5.1 List Available Tools

```bash
python main.py list-tools

# Output shows all configured tools and their status
```

#### 5.2 Install a Tool

```bash
# Install Ngspice (latest version)
python main.py install ngspice

# Install specific version
python main.py install ngspice --version 39

# Output shows download progress and installation status
```

#### 5.3 Check Tool Status

```bash
# View tool status after installation
python main.py status ngspice

# Shows:
# - Installation status
# - Current and latest versions
# - Installation path
# - Dependency status
```

#### 5.4 Check for Updates

```bash
# Check available updates for all tools
python main.py checks-updates

# Shows table with current vs latest versions
```

#### 5.5 Update Tools

```bash
# Update specific tool
python main.py update ngspice

# Update all tools with available updates
python main.py update --all
```

#### 5.6 View Logs

```bash
# View last 20 actions
python main.py logs

# View last N actions
python main.py logs --last 50
```

#### 5.7 System Information

```bash
# Display system and configuration info
python main.py system-info
```

## Step 6: Run Tests

### Unit Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_manager.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Check coverage report
# Open htmlcov/index.html in browser
```

### Manual Testing

#### Test 1: Dependency Checking

```bash
# Show dependencies for a tool
python main.py dependencies ngspice

# Expected:
# - Lists required dependencies
# - Shows installation status
# - Provides download links for missing deps
```

#### Test 2: Configuration Viewing

```bash
# View tool configuration
python main.py config ngspice

# Expected:
# - JSON formatted configuration
# - All tool parameters
```

#### Test 3: Tool Uninstalling

```bash
# Uninstall a tool
python main.py uninstall ngspice

# The tool will prompt for confirmation
# Type 'y' to confirm
```

## Step 7: Verify Functionality

### Test Matrix - ✅ Functionality Verification

Run through this checklist to verify all features work:

#### Installation Management
- [ ] `list-tools` command displays all tools
- [ ] `install` command downloads tool
- [ ] `status` command shows tool status
- [ ] `uninstall` command removes tool
- [ ] Version control works (`--version` flag)

#### Update and Upgrade System
- [ ] `checks-updates` shows available updates
- [ ] `update` command upgrades tool
- [ ] Version comparison works correctly
- [ ] Logs track update operations

#### User Interface
- [ ] CLI commands parse arguments correctly
- [ ] Help text displays for all commands
- [ ] Error messages are clear and helpful
- [ ] Progress indicators work (downloads)

#### Configuration Handling
- [ ] Configuration files load correctly
- [ ] Environment variables are set
- [ ] PATH is updated after installation
- [ ] Tool executables are accessible

#### Dependency Checking
- [ ] Dependencies are identified
- [ ] Missing dependencies are reported
- [ ] Dependency status is displayed
- [ ] Download links provided for missing deps

#### Logging
- [ ] All operations are logged
- [ ] Log levels are appropriate
- [ ] Timestamps are accurate
- [ ] `logs` command displays history

## Step 8: Configuration Customization

### Modify Installation Directory

Edit `config/settings.json`:

```json
{
  "system": {
    "installation_directory": "D:\\CustomPath\\Tools",
    "log_directory": "./logs"
  }
}
```

Reload configuration by running command again.

### Add New Tool

Edit `config/tools.json`:

```json
{
  "tools": {
    "my_tool": {
      "name": "My Tool",
      "description": "Description",
      "current_version": null,
      "latest_version": "1.0.0",
      "windows_download_url": "https://example.com/download",
      "windows_filename": "my_tool.zip",
      "dependencies": [],
      "installed": false,
      "install_path": null
    }
  }
}
```

Test new tool:

```bash
python main.py list-tools  # Should show my_tool
python main.py install my_tool  # Try to install
```

## Step 9: Troubleshooting

### Issue: "Python is not recognized"

```bash
# Solution: Add Python to PATH
# Windows: setx PATH "%PATH%;C:\Python311"
# Then restart terminal
```

### Issue: "ModuleNotFoundError: No module named 'src'"

```bash
# Solution: Ensure running from project root directory
cd path\to\esim-tool-manager
python main.py
```

### Issue: "Permission denied" during installation

```bash
# Solution: Run as Administrator
# Right-click PowerShell/CMD → Run as administrator
```

### Issue: "Checksum verification failed"

```bash
# Solution: Disable checksum verification (temporary)
# Edit config/settings.json:
{
  "features": {
    "checksums_verification": false
  }
}
```

### Check Logs for Details

```bash
# Always check logs when issues occur
python main.py logs --last 50

# Or read log file directly
type logs\tool_manager.log  # Windows
cat logs/tool_manager.log   # Linux/macOS
```

## Step 10: Performance Metrics

### Expected Performance

- **Tool Listing**: < 1 second
- **Dependency Check**: < 2 seconds
- **Download** (small tool): 10-60 seconds (depends on internet)
- **Installation**: 5-30 seconds (depends on tool size)
- **Update Check**: < 2 seconds
- **Log Display**: < 1 second

## Step 11: Testing Advanced Features

### Workflow: Complete Setup

Test the full workflow:

```bash
# 1. List available tools
python main.py list-tools

# 2. Install primary tool
python main.py install ngspice

# 3. Verify installation
python main.py status ngspice

# 4. Check for updates
python main.py checks-updates

# 5. View logs of all operations
python main.py logs --last 20

# 6. System information
python main.py system-info

# 7. Uninstall (optional cleanup)
python main.py uninstall ngspice
```

## Step 12: Deactivation/Cleanup

### Deactivate Virtual Environment

```bash
# When done testing
deactivate

# Or close terminal
```

### Clean Up (Optional)

```bash
# Remove virtual environment
rmdir /s /q venv

# Remove temporary downloads (already auto-cleaned)
rmdir /s /q temp_downloads

# Remove logs (if desired)
rmdir /s /q logs
```

## Documentation Files to Review

After executing, review these documents:

1. **[DESIGN_DOCUMENT.md](DESIGN_DOCUMENT.md)** - Architecture and design
2. **[README.md](README.md)** - Project overview
3. **[docs/INSTALLATION.md](docs/INSTALLATION.md)** - Installation details
4. **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)** - Complete user guide
5. **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)** - Developer API

## Support for Issues

If you encounter issues:

1. Check [docs/INSTALLATION.md](docs/INSTALLATION.md#troubleshooting)
2. Check [docs/USER_GUIDE.md](docs/USER_GUIDE.md#troubleshooting)
3. Review logs: `python main.py logs`
4. Review [README.md](README.md) section "Error Handling"

## Submission Notes

### Project Deliverables Checklist

- ✅ Design Document: [DESIGN_DOCUMENT.md](DESIGN_DOCUMENT.md)
- ✅ Code Implementation: `src/` directory with all modules
- ✅ Execution Instructions: This file
- ✅ Requirements Met:
  - ✅ Tool Installation Management
  - ✅ Update and Upgrade System
  - ✅ User Interface (CLI)
  - ✅ Dependency Checker
  - ✅ Configuration Handling

### Additional Requirements Met

- ✅ Configuration Management
- ✅ Dependency Resolution
- ✅ Comprehensive Logging
- ✅ Error Handling
- ✅ Code Documentation
- ✅ Test Suite


