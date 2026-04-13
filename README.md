# eSim Tool Manager
> **Automated Installation, Update, and Configuration Management for eSim Tools**

**Status**: Prototype/PoC | **Python**: 3.8+ | **Platform**: Windows (Extensible)

## Overview

eSim Tool Manager automates the installation, configuration, updates, and dependency management of external tools used by **eSim** (an open-source EDA tool for circuit design and simulation). It provides a unified command-line interface for managing tools like Ngspice, KiCad, and other dependencies.

## Key Features

✅ **Tool Installation Management** - Download and install external tools with version control  
✅ **Automatic Update Checking** - Detect available updates for all installed tools  
✅ **Update & Upgrade System** - Install updates with compatible dependency handling  
✅ **Configuration Management** - Automate tool setup and environment variable configuration  
✅ **Dependency Checker** - Validate dependencies and alert on missing/incompatible versions  
✅ **CLI Interface** - User-friendly command-line tool for all operations  
✅ **Interactive Mode** - Run without arguments and execute commands in a live prompt  
✅ **Action Logging** - Comprehensive logging of all operations for audit and debugging  
✅ **Cross-Platform Ready** - Windows focus with Linux/macOS extensibility  

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows OS (Linux/macOS support can be added)
- Administrator privileges (for environment variable modifications)
- Internet connection for downloads

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd esim-tool-manager

# Install dependencies
pip install -r requirements.txt

# Verify installation
python main.py --version
```

### Basic Usage

```bash
# Install a tool
python main.py install ngspice --version 39

# Check for available updates
python main.py checks-updates

# Update all tools
python main.py update --all

# List installed tools
python main.py list-tools

# View tool status
python main.py status ngspice

# View recent logs
python main.py logs --last 10

# Get help
python main.py --help

# Interactive mode
python main.py
# Then type commands such as: list-tools, checks-updates, exit
```

## Project Structure

```
esim-tool-manager/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── installer.py        # Tool installation logic
│   │   ├── updater.py          # Update checking and upgrade
│   │   └── config_manager.py   # Configuration handling
│   ├── ui/
│   │   ├── __init__.py
│   │   └── cli.py              # Command-line interface
│   └── utils/
│       ├── __init__.py
│       ├── downloader.py       # File download utilities
│       ├── dependency_checker.py
│       ├── logger.py           # Logging system
│       └── system_utils.py     # OS-specific utilities
├── config/
│   ├── tools.json              # Tool definitions & versions
│   ├── settings.json           # System configuration
│   └── dependencies.json       # Dependency specifications
├── logs/                        # Application logs (auto-created)
├── tests/
│   ├── __init__.py
│   └── test_*.py               # Unit tests
├── docs/
│   ├── INSTALLATION.md         # Installation guide
│   ├── USER_GUIDE.md           # Usage documentation
│   └── API_REFERENCE.md        # Developer API reference
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── DESIGN_DOCUMENT.md          # Architecture & design
├── README.md                    # This file
└── .gitignore
```

## Architecture

The tool manager follows a modular, layered architecture:

```
┌──────────────────────────────────────┐
│    CLI Interface (Command Parser)    │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  Core Managers (Install, Update,     │
│  Config, Dependencies)               │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  Utilities (Download, Logger,        │
│  System Interactions)                │
└──────────────────────────────────────┘
```

See [DESIGN_DOCUMENT.md](DESIGN_DOCUMENT.md) for detailed architecture.

## Requirements Met

This prototype meets **3 out of 5** requirements:

1. ✅ **Tool Installation Management** (Requirement #1)
   - Download and install tools (Ngspice, KiCad, etc.)
   - Version control with specific version selection
   - Windows compatibility

2. ✅ **Update and Upgrade System** (Requirement #2)
   - Check for available updates
   - Upgrade tools with dependency checking
   - Version tracking

3. ✅ **User Interface** (Requirement #5)
   - CLI with intuitive commands
   - Tool status and version viewing
   - Action logging and history

**Additional met requirements**:
- ✅ **Dependency Checker** - Validates dependencies during installation
- ✅ **Configuration Handling** - Manages environment variables and paths

## Usage Examples

### Example 1: Install Ngspice
```bash
$ python main.py install ngspice --version 39
[INFO] Checking dependencies for ngspice...
[INFO] Downloading ngspice v39...
[INFO] Installing ngspice...
[INFO] Configuring environment variables...
✓ ngspice v39 installed successfully at C:\eSim\Tools\ngspice
```

### Example 2: Check Updates
```bash
$ python main.py checks-updates
Checking for updates...
┌─────────────────────────────────────────────────┐
│ Tool      │ Current │ Latest │ Update Available │
├─────────────────────────────────────────────────┤
│ Ngspice   │ 39      │ 40     │ Yes               │
│ KiCad     │ 9.0.0   │ 10.0.0-1 │ Yes             │
└─────────────────────────────────────────────────┘
```

### Example 3: Update Tool
```bash
$ python main.py update ngspice
[INFO] Backing up current installation...
[INFO] Downloading ngspice v40...
[INFO] Installing update...
✓ ngspice successfully updated to v40
```

## Configuration

Edit `config/tools.json` to add or modify tool definitions:

```json
{
  "tools": {
    "ngspice": {
      "name": "Ngspice",
      "current_version": "39",
      "windows_download_url": "...",
      "dependencies": ["vcredist"],
      "installed": true,
      "install_path": "C:\\eSim\\Tools\\ngspice"
    }
  }
}
```

## Logging

All operations are logged to `logs/tool_manager.log`:

```
2026-04-05 14:30:21 [INFO] Tool installation started: ngspice v39
2026-04-05 14:30:25 [INFO] Download completed: 45.2 MB
2026-04-05 14:30:45 [INFO] Installation completed successfully
2026-04-05 14:30:47 [INFO] Environment variables configured
```

## Extensibility

Future enhancements:
- **GUI Interface** - Graphical frontend for non-technical users
- **Package Manager Integration** - Support Chocolatey, Winget
- **Linux/macOS Support** - Platform-specific implementations
- **Auto-Updates** - Background update checking
- **Beta Channels** - Support release channels (stable/beta)
- **Tool Scripts** - Custom post-install configuration scripts

## Error Handling

The manager includes robust error handling:
- **Network Errors** - Automatic retry with backoff
- **Installation Errors** - Clear error messages with remediation
- **Dependency Issues** - Auto-detect and suggest resolutions
- **Rollback Support** - Revert to previous versions on failure

## Security

- ✅ HTTPS downloads only
- ✅ Checksum verification of downloaded files
- ✅ Path validation and sanitization
- ✅ Audit logging of all operations
- ✅ Permission checks before system modifications

## Testing

Run tests with:

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_installer.py -v

# With coverage
python -m pytest tests/ --cov=src
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Documenta

See the `docs/` directory for:
- [Installation Guide](docs/INSTALLATION.md)
- [User Guide](docs/USER_GUIDE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Development Guide](docs/DEVELOPMENT.md)

## License

This project is licensed under MIT License - see LICENSE file for details.

## Support

For issues, questions, or suggestions:
- 📧 Email: contact-esim@fossee.in
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

## Authors

- **Developer**: eSim Summer Fellowship 2026 Participant
- **Project**: eSim Automated Tool Manager
- **Organization**: FOSSEE, IIT Bombay

## Acknowledgments

- eSim Project Team
- FOSSEE Initiative
- Open-source tool developers (Ngspice, KiCad, etc.)

---

**Version**: 1.0.0-beta  
**Last Updated**: April 2026  
**Status**: Prototype/PoC Phase
