"""
Logging module for eSim Tool Manager
Provides centralized logging for all operations
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any

class ToolManagerLogger:
    """Centralized logger for all tool manager operations"""
    
    def __init__(self, log_dir: str = "./logs", log_file: str = "tool_manager.log"):
        """
        Initialize the logger
        
        Args:
            log_dir: Directory to store log files
            log_file: Name of the log file
        """
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / log_file
        self.action_log_file = self.log_dir / "actions.json"
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup file logger
        self.logger = logging.getLogger("eSim-ToolManager")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        file_formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            fmt='%(levelname)s - %(message)s'
        )
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Action history tracking
        self.actions = []
    
    def info(self, message: str, **kwargs):
        """Log info level message"""
        self.logger.info(message)
        self._record_action("INFO", message, kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error level message"""
        if exception:
            self.logger.error(f"{message}\nException: {str(exception)}", exc_info=True)
        else:
            self.logger.error(message)
        self._record_action("ERROR", message, kwargs, exception)
    
    def warning(self, message: str, **kwargs):
        """Log warning level message"""
        self.logger.warning(message)
        self._record_action("WARNING", message, kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug level message"""
        self.logger.debug(message)
        self._record_action("DEBUG", message, kwargs)
    
    def success(self, message: str, **kwargs):
        """Log success message"""
        self.logger.info(f"✓ {message}")
        self._record_action("SUCCESS", message, kwargs)
    
    def _record_action(self, level: str, message: str, details: Dict[str, Any], exception: Optional[Exception] = None):
        """Record action to action history"""
        action = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "details": details,
            "exception": str(exception) if exception else None
        }
        self.actions.append(action)
        self._save_action_history()
    
    def _save_action_history(self):
        """Save action history to JSON file"""
        try:
            with open(self.action_log_file, 'w') as f:
                json.dump(self.actions, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save action history: {e}")
    
    def get_action_history(self, last_n: Optional[int] = None) -> list:
        """
        Get action history
        
        Args:
            last_n: Return only the last N actions
            
        Returns:
            List of actions
        """
        if last_n:
            return self.actions[-last_n:]
        return self.actions
    
    def clear_history(self):
        """Clear action history"""
        self.actions = []
        self._save_action_history()
    
    def get_log_file_path(self) -> Path:
        """Get path to main log file"""
        return self.log_file


# Global logger instance
_logger_instance = None

def get_logger(log_dir: str = "./logs", log_file: str = "tool_manager.log") -> ToolManagerLogger:
    """Get or create global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ToolManagerLogger(log_dir, log_file)
    return _logger_instance
