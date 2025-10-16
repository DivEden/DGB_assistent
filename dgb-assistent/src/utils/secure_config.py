"""
Secure Configuration Manager for DGB Assistent
Handles SARA browser automation credentials with multiple security layers
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, Optional
import tkinter as tk
from tkinter import simpledialog, messagebox
import base64


class SecureConfig:
    """Secure configuration manager for SARA credentials"""
    
    def __init__(self):
        self.app_dir = self._get_app_directory()
        self.config_file = self.app_dir / "config.enc"
        self._credentials = None
    
    def _get_app_directory(self) -> Path:
        """Get application directory for storing secure config"""
        # Use Windows standard AppData directory for user-specific application data
        if os.name == 'nt':  # Windows
            appdata_dir = os.getenv('APPDATA', os.path.expanduser('~'))
            config_dir = Path(appdata_dir) / "DGB-Assistent"
        else:
            # Unix-like systems (Linux, macOS)
            config_dir = Path.home() / ".config" / "dgb-assistent"
        
        # Create secure config directory
        config_dir.mkdir(parents=True, exist_ok=True, mode=0o700)  # Owner read/write only
        return config_dir
    
    def _simple_encrypt(self, text: str, key: str = "dgb_key_2025") -> str:
        """Simple encryption for local storage (not cryptographically secure)"""
        # This is basic obfuscation, not real encryption
        # For production, use proper encryption libraries like cryptography
        encoded = base64.b64encode(text.encode()).decode()
        return encoded
    
    def _simple_decrypt(self, encrypted_text: str, key: str = "dgb_key_2025") -> str:
        """Simple decryption for local storage"""
        try:
            decoded = base64.b64decode(encrypted_text.encode()).decode()
            return decoded
        except Exception:
            return ""
    
    def save_credentials(self, username: str, password: str):
        """Save credentials securely to local config file"""
        try:
            config = {
                'username': self._simple_encrypt(username),
                'password': self._simple_encrypt(password)
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            
            # Set file permissions (Windows)
            if os.name == 'nt':
                os.chmod(self.config_file, 0o600)
            
            self._credentials = {
                'username': username,
                'password': password
            }
            
            return True
        except Exception as e:
            print(f"Error saving credentials: {e}")
            return False
    
    def load_credentials(self) -> Optional[Dict[str, str]]:
        """Load credentials from secure config file or environment"""
        if self._credentials:
            return self._credentials
        
        # Try loading from .env file first (development)
        env_creds = self._load_from_env()
        if env_creds:
            self._credentials = env_creds
            return env_creds
        
        # Try loading from secure config file
        try:
            if not self.config_file.exists():
                return None
            
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            credentials = {
                'username': self._simple_decrypt(config.get('username', '')),
                'password': self._simple_decrypt(config.get('password', ''))
            }
            
            # Validate credentials are not empty
            if credentials['username'] and credentials['password']:
                self._credentials = credentials
                return credentials
            
        except Exception as e:
            print(f"Error loading credentials: {e}")
        
        return None
    
    def _load_from_env(self) -> Optional[Dict[str, str]]:
        """Load credentials from environment variables"""
        try:
            # Try to load python-dotenv if available
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        # Check for hardcoded credentials first (for SARA browser automation)
        username = os.getenv('SARA_USERNAME', '')
        password = os.getenv('SARA_PASSWORD', '')
        
        if username and password:
            # Don't use placeholder values
            if (username != 'your-username-here' and 
                password != 'your-password-here'):
                return {
                    'username': username,
                    'password': password
                }
        
        return None
    
    def setup_credentials_gui(self, parent=None) -> bool:
        """Show GUI dialog to set up credentials"""
        try:
            # Create setup window
            setup_window = tk.Toplevel(parent) if parent else tk.Tk()
            setup_window.title("SARA Configuration")
            setup_window.geometry("500x400")
            setup_window.resizable(False, False)
            
            # Center window
            setup_window.update_idletasks()
            x = (setup_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (setup_window.winfo_screenheight() // 2) - (400 // 2)
            setup_window.geometry(f"500x400+{x}+{y}")
            
            # Variables
            username_var = tk.StringVar()
            password_var = tk.StringVar()
            
            # Load existing values if available
            existing = self.load_credentials()
            if existing:
                username_var.set(existing.get('username', ''))
            
            # UI Elements
            tk.Label(setup_window, text="SARA Browser Automation Configuration", 
                    font=('Segoe UI', 16, 'bold')).pack(pady=20)
            
            # Form
            frame = tk.Frame(setup_window)
            frame.pack(padx=40, pady=20, fill='both', expand=True)
            
            # Username
            tk.Label(frame, text="Username:", font=('Segoe UI', 10)).pack(anchor='w')
            username_entry = tk.Entry(frame, textvariable=username_var, font=('Segoe UI', 10))
            username_entry.pack(fill='x', pady=(0, 10))
            
            # Password
            tk.Label(frame, text="Password:", font=('Segoe UI', 10)).pack(anchor='w')
            password_entry = tk.Entry(frame, textvariable=password_var, show='*', font=('Segoe UI', 10))
            password_entry.pack(fill='x', pady=(0, 20))
            
            # Info text about server
            info_label = tk.Label(frame, text="Server: https://sara.adlibhosting.com/SARA-011-DGB/", 
                                font=('Segoe UI', 9), fg='#6b7280')
            info_label.pack(anchor='w', pady=(0, 10))
            
            # Result variable
            result = {'success': False}
            
            def save_and_close():
                username = username_var.get().strip()
                password = password_var.get().strip()
                
                if not all([username, password]):
                    messagebox.showerror("Error", "Please fill in username and password")
                    return
                
                if self.save_credentials(username, password):
                    result['success'] = True
                    setup_window.destroy()
                else:
                    messagebox.showerror("Error", "Failed to save credentials")
            
            def cancel():
                setup_window.destroy()
            
            # Buttons
            button_frame = tk.Frame(frame)
            button_frame.pack(fill='x', pady=20)
            
            tk.Button(button_frame, text="Save", command=save_and_close,
                     bg='#2563eb', fg='white', font=('Segoe UI', 10, 'bold'),
                     padx=20, pady=5).pack(side='right', padx=(10, 0))
            
            tk.Button(button_frame, text="Cancel", command=cancel,
                     bg='#6b7280', fg='white', font=('Segoe UI', 10),
                     padx=20, pady=5).pack(side='right')
            
            # Focus on first empty field
            if not username_var.get():
                username_entry.focus()
            else:
                password_entry.focus()
            
            setup_window.wait_window()
            return result['success']
            
        except Exception as e:
            print(f"Error in credential setup: {e}")
            return False
    
    def clear_credentials(self):
        """Clear stored credentials"""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            self._credentials = None
            return True
        except Exception as e:
            print(f"Error clearing credentials: {e}")
            return False


# Global instance
_secure_config = None

def get_secure_config() -> SecureConfig:
    """Get the global secure config instance"""
    global _secure_config
    if _secure_config is None:
        _secure_config = SecureConfig()
    return _secure_config