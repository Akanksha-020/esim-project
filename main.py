#!/usr/bin/env python3
"""
eSim Tool Manager - Main Entry Point
Automated installation and management of eSim external tools
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ui.cli import main
from src.utils.logger import get_logger

def setup_environment():
    """Setup logging and basic environment"""
    logger = get_logger()
    logger.info("eSim Tool Manager started")

if __name__ == "__main__":
    try:
        setup_environment()
        main()
    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        sys.exit(1)
