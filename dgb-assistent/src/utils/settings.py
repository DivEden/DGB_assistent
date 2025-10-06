"""
Settings Manager for DGB Assistent
Handles user preferences and auto-update settings
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path


class SettingsManager:
    """Manages application settings and preferences"""
    
    def __init__(self):
        self.settings_dir = Path.home() / "AppData" / "Local" / "DGB-Assistent"
        self.settings_file = self.settings_dir / "settings.json"
        self.default_settings = {
            "auto_update_enabled": True,
            "check_frequency_days": 1,
            "show_update_notifications": True,
            "download_updates_automatically": False,
            "backup_before_update": True,
            "theme": "modern",
            "language": "da"
        }
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file or return defaults"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    settings = self.default_settings.copy()
                    settings.update(saved_settings)
                    return settings
            else:
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            self.settings_dir.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.default_settings.copy()


class SettingsDialog:
    """Modern settings dialog for DGB Assistent"""
    
    def __init__(self, parent, settings_manager):
        self.parent = parent
        self.settings_manager = settings_manager
        self.dialog = None
        self.temp_settings = settings_manager.settings.copy()
        
    def show(self):
        """Show the settings dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Indstillinger - DGB Assistent")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the settings interface"""
        main_frame = tk.Frame(self.dialog, bg='#ffffff', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame,
                              text="⚙️ Applikationsindstillinger",
                              font=('Segoe UI', 16, 'bold'),
                              fg='#1e293b', bg='#ffffff')
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Update settings tab
        update_frame = tk.Frame(notebook, bg='#ffffff', padx=20, pady=20)
        notebook.add(update_frame, text="Opdateringer")
        self.create_update_settings(update_frame)
        
        # General settings tab
        general_frame = tk.Frame(notebook, bg='#ffffff', padx=20, pady=20)
        notebook.add(general_frame, text="Generelt")
        self.create_general_settings(general_frame)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#ffffff')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Buttons
        cancel_btn = tk.Button(button_frame,
                             text="Annuller",
                             font=('Segoe UI', 10),
                             fg='#475569', bg='#f1f5f9',
                             activebackground='#e2e8f0',
                             relief=tk.FLAT, bd=0,
                             padx=20, pady=10,
                             cursor='hand2',
                             command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        reset_btn = tk.Button(button_frame,
                            text="Nulstil til Standard",
                            font=('Segoe UI', 10),
                            fg='#dc2626', bg='#fef2f2',
                            activebackground='#fee2e2',
                            relief=tk.FLAT, bd=0,
                            padx=20, pady=10,
                            cursor='hand2',
                            command=self.reset_to_defaults)
        reset_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_btn = tk.Button(button_frame,
                           text="Gem Indstillinger",
                           font=('Segoe UI', 10, 'bold'),
                           fg='#ffffff', bg='#3b82f6',
                           activebackground='#2563eb',
                           relief=tk.FLAT, bd=0,
                           padx=20, pady=10,
                           cursor='hand2',
                           command=self.save_settings)
        save_btn.pack(side=tk.RIGHT)
    
    def create_update_settings(self, parent):
        """Create update-related settings"""
        # Auto-update enabled
        self.auto_update_var = tk.BooleanVar(value=self.temp_settings['auto_update_enabled'])
        auto_update_frame = tk.Frame(parent, bg='#ffffff')
        auto_update_frame.pack(fill=tk.X, pady=(0, 15))
        
        auto_update_check = tk.Checkbutton(auto_update_frame,
                                         text="Aktivér automatiske opdateringer",
                                         variable=self.auto_update_var,
                                         font=('Segoe UI', 10, 'bold'),
                                         fg='#1e293b', bg='#ffffff',
                                         activebackground='#ffffff',
                                         selectcolor='#3b82f6',
                                         command=self.toggle_auto_update)
        auto_update_check.pack(anchor=tk.W)
        
        # Check frequency
        freq_frame = tk.Frame(parent, bg='#ffffff')
        freq_frame.pack(fill=tk.X, pady=(0, 15))
        
        freq_label = tk.Label(freq_frame,
                            text="Tjek for opdateringer hver:",
                            font=('Segoe UI', 10),
                            fg='#1e293b', bg='#ffffff')
        freq_label.pack(anchor=tk.W)
        
        freq_control_frame = tk.Frame(freq_frame, bg='#ffffff')
        freq_control_frame.pack(anchor=tk.W, pady=(5, 0))
        
        self.frequency_var = tk.IntVar(value=self.temp_settings['check_frequency_days'])
        frequency_spin = tk.Spinbox(freq_control_frame,
                                  from_=1, to=30,
                                  textvariable=self.frequency_var,
                                  width=5, font=('Segoe UI', 10))
        frequency_spin.pack(side=tk.LEFT)
        
        freq_unit_label = tk.Label(freq_control_frame,
                                 text="dag(e)",
                                 font=('Segoe UI', 10),
                                 fg='#475569', bg='#ffffff')
        freq_unit_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Notification settings
        self.notifications_var = tk.BooleanVar(value=self.temp_settings['show_update_notifications'])
        notifications_check = tk.Checkbutton(parent,
                                           text="Vis notifikationer om nye opdateringer",
                                           variable=self.notifications_var,
                                           font=('Segoe UI', 10),
                                           fg='#1e293b', bg='#ffffff',
                                           activebackground='#ffffff',
                                           selectcolor='#3b82f6')
        notifications_check.pack(anchor=tk.W, pady=(0, 15))
        
        # Auto-download settings
        self.auto_download_var = tk.BooleanVar(value=self.temp_settings['download_updates_automatically'])
        auto_download_check = tk.Checkbutton(parent,
                                           text="Download opdateringer automatisk (kræver manuel installation)",
                                           variable=self.auto_download_var,
                                           font=('Segoe UI', 10),
                                           fg='#1e293b', bg='#ffffff',
                                           activebackground='#ffffff',
                                           selectcolor='#3b82f6')
        auto_download_check.pack(anchor=tk.W, pady=(0, 15))
        
        # Backup settings
        self.backup_var = tk.BooleanVar(value=self.temp_settings['backup_before_update'])
        backup_check = tk.Checkbutton(parent,
                                    text="Lav backup før opdatering (anbefalet)",
                                    variable=self.backup_var,
                                    font=('Segoe UI', 10),
                                    fg='#1e293b', bg='#ffffff',
                                    activebackground='#ffffff',
                                    selectcolor='#3b82f6')
        backup_check.pack(anchor=tk.W)
    
    def create_general_settings(self, parent):
        """Create general application settings"""
        # Language setting
        lang_frame = tk.Frame(parent, bg='#ffffff')
        lang_frame.pack(fill=tk.X, pady=(0, 15))
        
        lang_label = tk.Label(lang_frame,
                            text="Sprog:",
                            font=('Segoe UI', 10, 'bold'),
                            fg='#1e293b', bg='#ffffff')
        lang_label.pack(anchor=tk.W)
        
        self.language_var = tk.StringVar(value=self.temp_settings['language'])
        language_combo = ttk.Combobox(lang_frame,
                                    textvariable=self.language_var,
                                    values=['da', 'en'],
                                    state='readonly',
                                    width=20)
        language_combo.pack(anchor=tk.W, pady=(5, 0))
        
        # Theme setting
        theme_frame = tk.Frame(parent, bg='#ffffff')
        theme_frame.pack(fill=tk.X, pady=(0, 15))
        
        theme_label = tk.Label(theme_frame,
                             text="Tema:",
                             font=('Segoe UI', 10, 'bold'),
                             fg='#1e293b', bg='#ffffff')
        theme_label.pack(anchor=tk.W)
        
        self.theme_var = tk.StringVar(value=self.temp_settings['theme'])
        theme_combo = ttk.Combobox(theme_frame,
                                 textvariable=self.theme_var,
                                 values=['modern', 'classic', 'dark'],
                                 state='readonly',
                                 width=20)
        theme_combo.pack(anchor=tk.W, pady=(5, 0))
    
    def toggle_auto_update(self):
        """Handle auto-update toggle"""
        # You could disable/enable related controls here if needed
        pass
    
    def save_settings(self):
        """Save the current settings"""
        try:
            # Update temp settings with current values
            self.temp_settings['auto_update_enabled'] = self.auto_update_var.get()
            self.temp_settings['check_frequency_days'] = self.frequency_var.get()
            self.temp_settings['show_update_notifications'] = self.notifications_var.get()
            self.temp_settings['download_updates_automatically'] = self.auto_download_var.get()
            self.temp_settings['backup_before_update'] = self.backup_var.get()
            self.temp_settings['language'] = self.language_var.get()
            self.temp_settings['theme'] = self.theme_var.get()
            
            # Save to settings manager
            self.settings_manager.settings = self.temp_settings.copy()
            if self.settings_manager.save_settings():
                messagebox.showinfo("Indstillinger Gemt", 
                                  "Dine indstillinger er blevet gemt.\n"
                                  "Nogle ændringer kræver muligvis genstart af applikationen.")
                self.dialog.destroy()
            else:
                messagebox.showerror("Fejl", "Kunne ikke gemme indstillinger.")
        except Exception as e:
            messagebox.showerror("Fejl", f"Fejl ved gemning af indstillinger: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset settings to defaults"""
        result = messagebox.askyesno("Nulstil Indstillinger",
                                   "Er du sikker på, at du vil nulstille alle indstillinger til standardværdier?")
        if result:
            self.settings_manager.reset_to_defaults()
            self.temp_settings = self.settings_manager.settings.copy()
            
            # Update UI to reflect defaults
            self.auto_update_var.set(self.temp_settings['auto_update_enabled'])
            self.frequency_var.set(self.temp_settings['check_frequency_days'])
            self.notifications_var.set(self.temp_settings['show_update_notifications'])
            self.auto_download_var.set(self.temp_settings['download_updates_automatically'])
            self.backup_var.set(self.temp_settings['backup_before_update'])
            self.language_var.set(self.temp_settings['language'])
            self.theme_var.set(self.temp_settings['theme'])
    
    def cancel(self):
        """Cancel and close dialog"""
        self.dialog.destroy()