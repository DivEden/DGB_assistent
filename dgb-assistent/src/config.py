"""
Application Configuration
Contains constants, settings, and configuration for the Python Desktop Application
"""

import os
import sys

# Application Information
APP_NAME = "DGB Assistent"
APP_VERSION = "1.0.0"
APP_AUTHOR = "DGB Team"
APP_DESCRIPTION = "En moderne applikationslauncher og digitalt arbejdsområde"

# GitHub Repository for Updates
GITHUB_REPO_OWNER = "diveden"        # Your GitHub username
GITHUB_REPO_NAME = "dgb-assistent"   # Your repository name

# Window Configuration
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 900
MIN_WINDOW_HEIGHT = 600

# Modern DGB Assistent Color Scheme - Soft & Contemporary
COLORS = {
    'primary': '#0969da',        # Modern GitHub-style blue
    'secondary': '#0550ae',      # Darker blue for hover
    'accent': '#0969da',         # Primary blue accent
    'background': '#fafbfc',     # Very soft gray-white
    'text': '#24292f',           # Soft dark gray text
    'success': '#1a7f37',        # Soft green
    'danger': '#cf222e',         # Soft red
    'warning': '#bf8700',        # Soft amber
    'info': '#0969da',           # Primary blue for info
    'light_gray': '#f6f8fa',     # Very light gray
    'medium_gray': '#656d76',    # Medium soft gray
    'dark_gray': '#24292f'       # Soft dark gray
}

# Fonts
FONTS = {
    'title': ('Arial', 24, 'bold'),
    'subtitle': ('Arial', 12, 'normal'),
    'body': ('Arial', 11, 'normal'),
    'small': ('Arial', 9, 'normal'),
    'button': ('Arial', 11, 'bold')
}

# File Paths
def get_asset_path(filename):
    """Get the path to an asset file"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(os.path.dirname(__file__))
    
    return os.path.join(base_path, 'assets', filename)

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Application Settings
SETTINGS = {
    'auto_save': True,
    'theme': 'light',
    'debug_mode': False,
    'check_updates': True
}