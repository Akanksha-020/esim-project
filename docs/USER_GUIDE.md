# User Guide - eSim Tool Manager

## Overview

The eSim Tool Manager provides a command-line interface for managing tools and dependencies used by eSim. This guide covers all available commands and their usage.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Commands](#commands)
3. [Common Workflows](#common-workflows)
4. [Troubleshooting](#troubleshooting)

## Getting Started

### Accessing Help

```bash
# General help
python main.py --help

# Command-specific help
python main.py <command> --help

# Examples
python main.py install --help
python main.py update --help
```

### Interactive Mode

Run without arguments to open an interactive prompt:

```bash
python main.py

# Example session
tool-manager> list-tools
tool-manager> status ngspice
tool-manager> exit
```

## Commands

### List Tools

View all available and installed tools:

```bash
python main.py list-tools
```

**Output Example**:
```
┌─────────┬──────────────┬──────────────┬──────────────┬────────────────────────┐
│ Tool    │ Current Ver  │ Latest Ver   │ Status       │ Description            │
├─────────┼──────────────┼──────────────┼──────────────┼────────────────────────┤
│ ngspice │ 39           │ 40           │ Installed    │ Circuit simulator      │
│ kicad   │ None         │ 10.0.0-1     │ Not installed│ PCB design software    │
└─────────┴──────────────┴──────────────┴──────────────┴────────────────────────┘
```

### Install Tools

Install a tool or specific version:

```bash
# Install latest version
python main.py install ngspice

# Install specific version
python main.py install ngspice --version 39

# Install with version shorthand
python main.py install kicad -v 10.0.0-1
```

**Process**:
1. ✓ Software validates tool configuration
2. ✓ Downloads tool from configured URL
3. ✓ Verifies file integrity (if checksum available)
4. ✓ Installs package (`.zip` extraction or `.exe`/`.msi` installer execution)
5. ✓ Configures environment variables
6. ✓ Verifies installation success

### Check for Updates

View available updates for installed tools:

```bash
# Check all tools
python main.py checks-updates

# Interactive update
python main.py update --all
```

**Output Example**:
```
============================================================
eSim Tool Manager - Update Report
============================================================

Total Tools: 3
Updates Available: 1

Tool                 Current        Latest         Status
────────────────────────────────────────────────────────
Ngspice              39             40             ⚠ Update available
KiCad                9.0.0          10.0.0-1       ⚠ Update available
Python               3.11.7         3.11.8         ✓ Up to date
============================================================
```

### Update Tools

Update a specific tool to its configured latest version, or update all tools:

```bash
# Update specific tool
python main.py update ngspice

# Update all tools with updates
python main.py update --all
```

**Update Process**:
1. ✓ Creates backup of current version
2. ✓ Uninstalls current version
3. ✓ Installs new version
4. ✓ Verifies installation
5. ✓ Cleans up backups on success

### Uninstall Tools

Remove installed tools:

```bash
# Uninstall tool (interactive)
python main.py uninstall ngspice

# The tool will prompt for confirmation
```

### View Tool Status

Get detailed information about a specific tool:

```bash
python main.py status ngspice
```

**Output Example**:
```
Status for ngspice:
==================================================
Name                 Ngspice
Description          Open-source circuit simulator
Status               Installed
Current Version      39
Latest Version       40
Installation Path    C:\eSim\Tools\ngspice
==================================================

Dependency Report for ngspice:
  vcredist             ✓ Installed       v2022
```

### Check Dependencies

View dependency information for a tool:

```bash
# Show dependencies
python main.py dependencies ngspice

# Output shows:
# - Required dependencies
# - Installation status of each
# - Download links for missing deps
```

### View Logs

Display action history and logs:

```bash
# View last 20 actions (default)
python main.py logs

# View last N actions
python main.py logs --last 50
python main.py logs -l 10

# Logs show timestamps, level (INFO/ERROR/SUCCESS), and messages
```

**Log Levels**:
- 🟢 INFO: Informational messages
- 🔴 ERROR: Errors and failures
- 🟡 WARNING: Warnings and cautions
- 🟢 SUCCESS: Successful operations

### View Tool Configuration

Display tool configuration details:

```bash
python main.py config ngspice

# Shows JSON configuration including:
# - Name and description
# - Version information
# - Download URLs
# - Dependencies
# - Installation path
```

### System Information

Display system and configuration details:

```bash
python main.py system-info

# Shows:
# - Operating System and version
# - Python version
# - System architecture
# - Installation directories
# - Log directory
```

### Display Help

```bash
python main.py --help
python main.py --version
```

## Common Workflows

### Workflow 1: Fresh Installation

Setup eSim tools from scratch:

```bash
# Step 1: See what's available
python main.py list-tools

# Step 2: Install main tools
python main.py install ngspice
python main.py install kicad

# Step 3: Verify installations
python main.py status ngspice
python main.py status kicad

# Step 4: Check updates
python main.py checks-updates
```

### Workflow 2: Update Everything

Keep all tools current:

```bash
# Step 1: Check available updates
python main.py checks-updates

# Step 2: Update all with one command
python main.py update --all

# Step 3: Verify update success
python main.py logs --last 5
```

### Workflow 3: Troubleshoot Tool Issue

Diagnose and fix tool problems:

```bash
# Step 1: Check tool status
python main.py status ngspice

# Step 2: View dependencies
python main.py dependencies ngspice

# Step 3: Check recent actions
python main.py logs --last 20

# Step 4: If needed, reinstall
python main.py uninstall ngspice
python main.py install ngspice
```

### Workflow 4: Add New Tool

Add a new tool to the manager:

1. Edit `config/tools.json` and add tool definition
2. Edit `config/dependencies.json` if needed
3. Run:

```bash
python main.py list-tools  # Verify tool appears
python main.py install <tool_name>
```

## Configuration

### User Configuration

Edit `config/settings.json` to customize:

```json
{
  "system": {
    "installation_directory": "D:\\MyTools",
    "log_directory": "./logs",
    "auto_check_updates": true,
    "update_check_interval_days": 7,
    "download_timeout_seconds": 300,
    "verify_checksums": true,
    "retry_attempts": 3
  }
}
```

### Tool Definitions

Edit `config/tools.json` to:
- Add new tools
- Change download URLs
- Update version information
- Manage dependencies

## Troubleshooting

### Problem: Installation fails

**Solution Steps**:
1. Check dependencies: `python main.py dependencies <tool>`
2. Verify internet connection
3. Check disk space: `python main.py system-info`
4. Try again with specific version: `python main.py install <tool> -v <version>`
5. Check logs: `python main.py logs`

### Problem: Tool not found after installation

**Solution Steps**:
1. Verify installation: `python main.py status <tool>`
2. Check PATH: `python main.py system-info`
3. Don't worry, this might be a PATH refresh issue
4. Restart terminal/command prompt
5. Test tool: `<tool> --version`

### Problem: Update failed

**Solution Steps**:
1. Check logs: `python main.py logs --last 10`
2. Manual rollback: `python main.py install <tool> -v <old_version>`
3. For persistent issues, uninstall and reinstall

### Problem: Permission errors

**Solution Steps**:
1. Run as Administrator
2. Check directory permissions
3. Ensure sufficient disk space
4. Verify antivirus isn't blocking operations

### Problem: Network timeout

**Solution Steps**:
1. Check internet connection
2. Try again (automatic retry happens 3 times)
3. Increase timeout in `config/settings.json`
4. Try different mirror/download URL

## Tips & Tricks

### Speed Up Installation

- Keep `verify_checksums: false` in config for faster installation
- But recommend keeping it `true` for security

### Monitor Installation Progress

```bash
# Watch logs in real-time
python main.py logs --last 20
```

### Automate with Scripts

Create batch/shell script:

```bash
#!/bin/bash
python main.py install ngspice
python main.py install kicad
python main.py install python
```

### Clean Up

Remove temporary files:

```bash
# The tool automatically cleans up after installation
# To manually clean: just delete ./temp_downloads/ directory
```

## Advanced Features

### Dependency Resolution

The tool automatically:
- Detects missing dependencies
- Alerts you with download links
- Can auto-install some dependencies

### Environment Variable Setup

Automatically configures:
- PATH entries
- Tool-specific environment variables
- System-wide accessibility

### Checksum Verification

Verifies downloaded files:
- SHA256 checksum validation
- Detects corrupted downloads
- Ensures file integrity

## Support & Help

- **Full Help**: `python main.py --help`
- **Command Help**: `python main.py <command> --help`
- **System Info**: `python main.py system-info`
- **Recent Logs**: `python main.py logs`
- **Email Support**: contact-esim@fossee.in

---

**Version**: 1.0.0  
**Last Updated**: April 2026
