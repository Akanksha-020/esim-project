# Installation Guide - eSim Tool Manager

## Prerequisites

Before installing eSim Tool Manager, ensure you have the following:

### System Requirements

- **Operating System**: Windows 10/11 (Linux/macOS support coming soon)
- **Python**: 3.8 or higher
- **RAM**: 2 GB minimum
- **Disk Space**: 5 GB for tool installations
- **Administrator Privileges**: Required for PATH modifications and installations

### Check Your System

Verify your Python installation:

```bash
python --version
# Should output Python 3.8 or higher
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd esim-tool-manager
```

### 2. Create Virtual Environment (Recommended)

Creating a virtual environment isolates dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

This will install:
- Click 8.1.7 (CLI framework)
- Requests 2.31.0 (HTTP downloads)
- PyYAML 6.0.1 (Config handling)
- Colorlog 6.8.0 (Colored logging)
- And other utilities

### 4. Verify Installation

```bash
# Test the installation
python main.py --help

# Should display help information
```

### 5. Configuration Setup

The application uses JSON configuration files located in `config/`:

```
config/
├── tools.json          # Tool definitions
├── settings.json       # System settings
└── dependencies.json   # Dependency specifications
```

**Default Settings** are automatically loaded from `config/settings.json`:

```json
{
  "system": {
    "installation_directory": "C:\\eSim\\Tools",
    "log_directory": "./logs",
    "auto_check_updates": true
  }
}
```

## Quick Start after Installation

### 1. Check Available Tools

```bash
python main.py list
```

### 2. Install Your First Tool

```bash
python main.py install ngspice --version 39
```

### 3. Check Installation Status

```bash
python main.py status ngspice
```

### 4. View Logs

```bash
python main.py logs --last 10
```

## Troubleshooting

### Issue: Python not found

**Solution**: Ensure Python is in your system PATH
```bash
# Add Python to PATH (Windows)
set PATH=%PATH%;C:\Python3X

# Verify
python --version
```

### Issue: Permission denied errors

**Solution**: Run command prompt or PowerShell as Administrator

```bash
# Right-click on Command Prompt/PowerShell
# Select "Run as administrator"
```

### Issue: Package installation fails

**Solution**: Update pip and setuptools

```bash
python -m pip install --upgrade pip setuptools
pip install -r requirements.txt
```

### Issue: No module named 'src'

**Solution**: Ensure you're running from the project root directory

```bash
# Correct
cd C:\path\to\esim-tool-manager
python main.py

# Wrong
cd config/
python ..\main.py
```

## Environment Variable Setup

The tool manager automatically configures environment variables. To use tools system-wide:

1. **Manual Configuration** (if needed):

   ```bash
   # Set NGSPICE_PATH
   setx NGSPICE_PATH "C:\eSim\Tools\ngspice"
   
   # Set PATH
   setx PATH "%PATH%;C:\eSim\Tools\ngspice\bin"
   ```

2. **Verify Setup**:

   ```bash
   # Test tool is accessible
   ngspice --version
   ```

## Advanced Configuration

### Custom Installation Directory

Edit `config/settings.json`:

```json
{
  "system": {
    "installation_directory": "D:\\CustomTools",
    "log_directory": "./logs"
  }
}
```

### Add New Tool

Edit `config/tools.json`:

```json
{
  "tools": {
    "my_tool": {
      "name": "My Tool",
      "description": "Tool description",
      "current_version": null,
      "latest_version": "1.0.0",
      "windows_download_url": "https://example.com/download",
      "dependencies": [],
      "installed": false,
      "install_path": null
    }
  }
}
```

## Uninstallation

To uninstall the tool manager:

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rmdir /s venv

# Remove project directory
rmdir /s esim-tool-manager
```

To uninstall specific tools:

```bash
python main.py uninstall ngspice
```

## Getting Help

Unable to proceed? Try these:

1. **Check Logs**:
   ```bash
   python main.py logs
   ```

2. **System Information**:
   ```bash
   python main.py system-info
   ```

3. **Specific Tool Status**:
   ```bash
   python main.py status ngspice
   ```

4. **Help Command**:
   ```bash
   python main.py --help
   python main.py install --help
   ```

## Next Steps

- Read [USER_GUIDE.md](USER_GUIDE.md) for usage instructions
- See [API_REFERENCE.md](API_REFERENCE.md) for developer documentation
- Check [../DESIGN_DOCUMENT.md](../DESIGN_DOCUMENT.md) for architecture details

## Support

For issues or questions:
- 📧 Email: contact-esim@fossee.in
- 🐛 Report bugs on GitHub
- 💬 Ask questions in Discussions

---

**Last Updated**: April 2026  
**Version**: 1.0.0
