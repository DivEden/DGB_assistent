"""
Helper Utilities for Python Desktop Application
Contains useful functions and utilities used throughout the application
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path


def setup_logging(app_name="DGB-Assistent", log_level=logging.INFO):
    """Setup logging configuration for the application"""
    # Use consistent directory structure with secure_config
    if os.name == 'nt':  # Windows
        appdata_dir = os.getenv('APPDATA', os.path.expanduser('~'))
        log_dir = Path(appdata_dir) / app_name / "logs"
    else:
        # Unix-like systems
        log_dir = Path.home() / ".config" / app_name.lower() / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"{app_name}_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(app_name)


def get_app_data_dir(app_name="DGB-Assistent"):
    """Get the application data directory"""
    # Use consistent directory structure with secure_config
    if os.name == 'nt':  # Windows
        appdata_dir = os.getenv('APPDATA', os.path.expanduser('~'))
        app_dir = Path(appdata_dir) / app_name
    elif sys.platform == "darwin":  # macOS
        app_dir = Path.home() / "Library" / "Application Support" / app_name
    else:  # Linux and others
        app_dir = Path.home() / ".config" / app_name.lower()
    
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def save_settings(settings, app_name="DGB-Assistent"):
    """Save application settings to a JSON file"""
    try:
        app_dir = get_app_data_dir(app_name)
        settings_file = app_dir / "settings.json"
        
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        
        return True
    except Exception as e:
        logging.error(f"Failed to save settings: {e}")
        return False


def load_settings(app_name="PythonDesktopApp", default_settings=None):
    """Load application settings from a JSON file"""
    try:
        app_dir = get_app_data_dir(app_name)
        settings_file = app_dir / "settings.json"
        
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                return json.load(f)
        else:
            return default_settings or {}
    except Exception as e:
        logging.error(f"Failed to load settings: {e}")
        return default_settings or {}


def validate_email(email):
    """Validate email address format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def format_date(date_obj, format_string='%d %B %Y'):
    """Format a date object to a string"""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
        except ValueError:
            return date_obj
    
    return date_obj.strftime(format_string)


def format_file_size(size_bytes):
    """Format file size in bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def generate_unique_id():
    """Generate a unique identifier"""
    import uuid
    return str(uuid.uuid4())


def center_window(window, width=None, height=None):
    """Center a tkinter window on the screen"""
    window.update_idletasks()
    
    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()
        
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    
    window.geometry(f"{width}x{height}+{x}+{y}")


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """Check if internet connection is available"""
    import socket
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False