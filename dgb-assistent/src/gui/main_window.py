"""
Modern App Hub - Main W                "color": "#3b82f6"  # Consistent premium blue
            },
            {
                "name": "Data Analyse", 
                "description": "Analysér og visualiser data",
                "category": "Analyse",
                "icon": "📈",
                "color": "#3b82f6"  # Consistent premium blue
            },
            {
                "name": "Indstillinger", 
                "description": "Konfigurer applikationsindstillinger",
                "category": "System",
                "icon": "⚙️",
                "color": "#3b82f6"  # Consistent premium blueeates a sleek, modern dashboard inspired by the most beautiful applications
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import os
import sys
import math

# Handle imports for both development and packaged versions
try:
    from utils.updater import AutoUpdater, UpdateDialog
    from utils.settings import SettingsManager, SettingsDialog
    from config import APP_VERSION, GITHUB_REPO_OWNER, GITHUB_REPO_NAME
    # Import image processing tools
    from apps.image_tools.simple_resizer import SimpleImageResizer
    from apps.image_tools.group_processor import GroupImageProcessor
    from apps.image_tools.individual_processor import IndividualImageProcessor
except ImportError:
    # Fallback for development with relative imports
    from ..utils.updater import AutoUpdater, UpdateDialog
    from ..utils.settings import SettingsManager, SettingsDialog
    from ..config import APP_VERSION, GITHUB_REPO_OWNER, GITHUB_REPO_NAME
    # Import image processing tools
    from ..apps.image_tools.simple_resizer import SimpleImageResizer
    from ..apps.image_tools.group_processor import GroupImageProcessor
    from ..apps.image_tools.individual_processor import IndividualImageProcessor


class ModernAppHub:
    """Modern application hub with dashboard-style interface"""
    
    def __init__(self, master):
        self.master = master
        self.search_var = tk.StringVar()
        self.selected_category = tk.StringVar(value="Alle")
        
        # Initialize auto-updater and settings
        self.settings_manager = SettingsManager()
        self.updater = AutoUpdater(APP_VERSION, GITHUB_REPO_OWNER, GITHUB_REPO_NAME)
        
        # DGB Assistent apps (customizable)
        self.apps = [
            {
                "name": "Simpel Billedkomprimering", 
                "description": "Komprimér billeder til bestemt KB størrelse",
                "category": "Billeder",
                "icon": "🖼️",
                "color": "#002852",
                "action": "simple_resizer"
            },
            {
                "name": "Gruppe Billedbehandler", 
                "description": "Gruppér billeder og navngiv systematisk",
                "category": "Billeder",
                "icon": "👥",
                "color": "#002852",
                "action": "group_processor"
            },
            {
                "name": "Individuel Billedbehandler", 
                "description": "Navngiv hvert billede individuelt",
                "category": "Billeder",
                "icon": "🏷️",
                "color": "#002852",
                "action": "individual_processor"
            },
            {
                "name": "Indstillinger", 
                "description": "Konfigurer applikationsindstillinger",
                "category": "Billeder",
                "icon": "⚙️",
                "color": "#002852"
            }
        ]
        
        self.setup_window()
        self.create_modern_interface()
        
        # Check for updates after UI is ready
        self.check_for_updates()
        
    def setup_window(self):
        """Configure the main window with modern styling"""
        self.master.title("DGB Assistent")
        self.master.geometry("1200x800")
        self.master.minsize(900, 600)
        self.master.configure(bg='#ffffff')
        
        # Center window
        self.center_window()
        
        # Premium color palette - elegant and cohesive
        self.colors = {
            'bg_primary': '#f8fafc',      # Premium light background
            'bg_secondary': '#ffffff',    # Pure white cards
            'bg_sidebar': '#1e293b',      # Premium dark sidebar
            'sidebar_accent': '#334155',  # Darker accent for sidebar
            'accent': '#3b82f6',          # Premium blue
            'accent_hover': '#2563eb',    # Darker blue for hover
            'accent_light': '#eff6ff',    # Very light blue
            'accent_ultra_light': '#f0f9ff',  # Ultra light blue for tiles
            'text_primary': '#0f172a',    # Premium dark text
            'text_secondary': '#475569',  # Medium gray text
            'text_tertiary': '#94a3b8',   # Light gray for captions
            'text_white': '#ffffff',      # White text
            'text_sidebar': '#cbd5e1',    # Light gray for sidebar text
            'success': '#10b981',         # Premium green
            'warning': '#f59e0b',         # Premium amber
            'danger': '#ef4444',          # Premium red
            'border': '#e2e8f0',          # Premium borders
            'border_light': '#f1f5f9',    # Lighter borders
            'shadow': 'rgba(15, 23, 42, 0.04)'  # Premium shadow
        }
        
        self.setup_fonts()
        
    def setup_fonts(self):
        """Setup premium font system"""
        # Use modern, elegant system fonts
        try:
            # Try Inter font (modern and elegant)
            title_font = 'Inter'
        except:
            try:
                # Fallback to SF Pro Display style
                title_font = 'Segoe UI Variable Display'
            except:
                # Final fallback to clean Segoe UI
                title_font = 'Segoe UI'
            
        self.fonts = {
            'heading': (title_font, 28, 'normal'),    # Clean, modern title
            'subheading': ('Segoe UI', 18, 'normal'),
            'title': ('Segoe UI', 14, 'bold'),
            'body': ('Segoe UI', 11, 'normal'),
            'caption': ('Segoe UI', 9, 'normal'),
            'button': ('Segoe UI', 10, 'bold')
        }
        
    def create_modern_interface(self):
        """Create the modern dashboard interface"""
        # Configure main grid
        self.master.columnconfigure(1, weight=1)
        self.master.rowconfigure(0, weight=1)
        
        # Create main layout
        self.create_sidebar()
        self.create_main_content()
        
    def create_sidebar(self):
        """Create modern sidebar navigation"""
        sidebar = tk.Frame(self.master, bg=self.colors['bg_sidebar'], width=260)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_propagate(False)
        
        # Add subtle border on the right
        border_frame = tk.Frame(sidebar, bg=self.colors['sidebar_accent'], width=1)
        border_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # DGB Assistent title in sidebar
        title_frame = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
        title_frame.pack(fill=tk.X, padx=20, pady=(30, 40))
        
        title_label = tk.Label(title_frame, text="DGB Assistent", 
                              font=self.fonts['heading'], 
                              fg=self.colors['text_white'], 
                              bg=self.colors['bg_sidebar'])
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(title_frame, text="Dit Digitale Værktøj", 
                                 font=self.fonts['caption'], 
                                 fg=self.colors['text_sidebar'], 
                                 bg=self.colors['bg_sidebar'])
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Categories removed - only Billeder category now
        
        # Quick stats
        self.create_quick_stats(sidebar)
        
        # Settings at bottom
        self.create_sidebar_footer(sidebar)
        
    def create_category_nav(self, parent):
        """Create category navigation - removed, only Billeder category now"""
        pass
            
    def create_quick_stats(self, parent):
        """Create quick statistics display"""
        stats_frame = tk.Frame(parent, bg=self.colors['bg_sidebar'])
        stats_frame.pack(fill=tk.X, padx=20, pady=30)
        
        stats_title = tk.Label(stats_frame, text="STATISTIK", 
                              font=self.fonts['caption'], 
                              fg=self.colors['text_sidebar'], 
                              bg=self.colors['bg_sidebar'])
        stats_title.pack(anchor=tk.W, pady=(0, 12))
        
        # App count
        app_count = len(self.apps)
        count_label = tk.Label(stats_frame, text=f"{app_count} Apps", 
                              font=self.fonts['title'], 
                              fg=self.colors['text_white'], 
                              bg=self.colors['bg_sidebar'])
        count_label.pack(anchor=tk.W)
        
        # Version info
        version_label = tk.Label(stats_frame, text="Version 1.1", 
                            font=self.fonts['body'], 
                            fg=self.colors['text_sidebar'], 
                            bg=self.colors['bg_sidebar'])
        version_label.pack(anchor=tk.W, pady=(6, 0))
        
    def create_sidebar_footer(self, parent):
        """Create sidebar footer with GitHub and settings"""
        footer_frame = tk.Frame(parent, bg=self.colors['bg_sidebar'])
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        
        # GitHub button with dark theme styling
        github_btn = tk.Button(footer_frame, text="💻 GitHub",
                              font=self.fonts['body'],
                              fg=self.colors['text_sidebar'],
                              bg=self.colors['bg_sidebar'],
                              activebackground=self.colors['sidebar_accent'],
                              activeforeground=self.colors['text_white'],
                              relief=tk.FLAT,
                              anchor=tk.W,
                              padx=16, pady=10,
                              cursor='hand2',
                              bd=0,
                              command=self.open_github)
        github_btn.pack(fill=tk.X, pady=1)
        
        # API Configuration button
        api_config_btn = tk.Button(footer_frame, text="🔑 API Konfiguration",
                                  font=self.fonts['body'],
                                  fg=self.colors['text_sidebar'],
                                  bg=self.colors['bg_sidebar'],
                                  activebackground=self.colors['sidebar_accent'],
                                  activeforeground=self.colors['text_white'],
                                  relief=tk.FLAT,
                                  anchor=tk.W,
                                  padx=16, pady=10,
                                  cursor='hand2',
                                  bd=0,
                                  command=self.open_api_config)
        api_config_btn.pack(fill=tk.X, pady=1)
        
        settings_btn = tk.Button(footer_frame, text="⚙️ Indstillinger",
                                font=self.fonts['body'],
                                fg=self.colors['text_sidebar'],
                                bg=self.colors['bg_sidebar'],
                                activebackground=self.colors['sidebar_accent'],
                                activeforeground=self.colors['text_white'],
                                relief=tk.FLAT,
                                anchor=tk.W,
                                padx=16, pady=10,
                                cursor='hand2',
                                bd=0,
                                command=self.open_settings)
        settings_btn.pack(fill=tk.X, pady=1)
        
        about_btn = tk.Button(footer_frame, text="ℹ️ Om",
                             font=self.fonts['body'],
                             fg=self.colors['text_sidebar'],
                             bg=self.colors['bg_sidebar'],
                             activebackground=self.colors['sidebar_accent'],
                             activeforeground=self.colors['text_white'],
                             relief=tk.FLAT,
                             anchor=tk.W,
                             padx=16, pady=10,
                             cursor='hand2',
                             bd=0,
                             command=self.show_about)
        about_btn.pack(fill=tk.X, pady=1)
        
        # Add dark theme hover effects to footer buttons
        for btn in [github_btn, api_config_btn, settings_btn, about_btn]:
            btn.bind("<Enter>", lambda e, button=btn: self.on_sidebar_button_hover(button, True))
            btn.bind("<Leave>", lambda e, button=btn: self.on_sidebar_button_hover(button, False))
        
    def create_main_content(self):
        """Create the main content area with app tiles"""
        main_frame = tk.Frame(self.master, bg=self.colors['bg_primary'])
        main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header with search
        self.create_content_header(main_frame)
        
        # Scrollable app grid
        self.create_app_grid(main_frame)
        
    def create_content_header(self, parent):
        """Create the content header with search and welcome"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 20))
        header_frame.columnconfigure(1, weight=1)
        
        # Welcome text removed as requested
        
        # Search bar
        search_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        search_frame.grid(row=0, column=0, sticky="ew", pady=10)
        
        search_icon = tk.Label(search_frame, text="�", 
                              font=self.fonts['body'], 
                              fg=self.colors['text_secondary'], 
                              bg=self.colors['bg_secondary'])
        search_icon.pack(side=tk.LEFT, padx=(15, 5), pady=10)
        
        search_entry = tk.Entry(search_frame, 
                               textvariable=self.search_var,
                               font=self.fonts['body'],
                               fg=self.colors['text_primary'],
                               bg=self.colors['bg_secondary'],
                               relief=tk.FLAT,
                               bd=0)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=10, padx=(0, 15))
        search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Style the search frame
        search_frame.configure(bg=self.colors['bg_secondary'], relief=tk.FLAT, bd=1)
        search_entry.insert(0, "Søg apps...")
        search_entry.bind('<FocusIn>', self.on_search_focus_in)
        search_entry.bind('<FocusOut>', self.on_search_focus_out)
        
        # Quick actions removed - Tilføj App button removed as requested
        
    def create_app_grid(self, parent):
        """Create scrollable grid of app tiles"""
        # Create canvas for scrolling
        canvas_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        canvas_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(canvas_frame, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg_primary'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind mousewheel to canvas
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        
        # Create app tiles
        self.update_app_display()
        
    def update_app_display(self):
        """Update the display of app tiles based on current filter/search"""
        # Clear existing tiles
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Filter apps based on category and search
        filtered_apps = self.filter_apps()
        
        # Calculate grid layout (4 columns)
        cols = 4
        col_width = 250
        
        # Create app tiles
        for i, app in enumerate(filtered_apps):
            row = i // cols
            col = i % cols
            
            self.create_app_tile(self.scrollable_frame, app, row, col)
            
        # Update canvas scroll region
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def create_app_tile(self, parent, app, row, col):
        """Create a beautiful app tile"""
        # Premium tile container with elegant border
        tile_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], 
                             relief=tk.SOLID, bd=1, 
                             highlightbackground=self.colors['border_light'],
                             highlightthickness=1)
        tile_frame.grid(row=row, column=col, padx=15, pady=15, sticky="w")
        
        # Inner content frame with premium spacing
        content_frame = tk.Frame(tile_frame, bg=self.colors['bg_secondary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=28, pady=28)
        
        # App icon with consistent ultra-light background
        icon_frame = tk.Frame(content_frame, bg=self.colors['accent_ultra_light'], width=60, height=60)
        icon_frame.pack(anchor=tk.W, pady=(0, 20))
        icon_frame.pack_propagate(False)
        
        icon_label = tk.Label(icon_frame, text=app['icon'], 
                             font=('Segoe UI Emoji', 24), 
                             bg=self.colors['accent_ultra_light'], 
                             fg=self.colors['accent'])
        icon_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # App name
        name_label = tk.Label(content_frame, text=app['name'], 
                             font=self.fonts['title'], 
                             fg=self.colors['text_primary'], 
                             bg=self.colors['bg_secondary'],
                             anchor=tk.W)
        name_label.pack(anchor=tk.W, fill=tk.X)
        
        # App description with better spacing
        desc_label = tk.Label(content_frame, text=app['description'], 
                             font=self.fonts['body'], 
                             fg=self.colors['text_secondary'], 
                             bg=self.colors['bg_secondary'],
                             anchor=tk.W, wraplength=200)
        desc_label.pack(anchor=tk.W, fill=tk.X, pady=(6, 20))
        
        # Modern launch button
        launch_btn = tk.Button(content_frame, text="Start",
                              font=self.fonts['button'],
                              fg=self.colors['text_white'],
                              bg=self.colors['accent'],
                              activebackground=self.colors['accent_hover'],
                              relief=tk.FLAT,
                              padx=18, pady=8,
                              cursor='hand2',
                              bd=0,
                              command=lambda: self.launch_app(app))
        launch_btn.pack(anchor=tk.W)
        
        # Add hover effects to tile
        self.add_tile_hover_effects(tile_frame, content_frame, launch_btn)
        
    def add_tile_hover_effects(self, tile_frame, content_frame, button):
        """Add premium hover effects to app tiles"""
        def on_enter(e):
            tile_frame.configure(highlightbackground=self.colors['accent'], 
                               highlightthickness=2,
                               bg=self.colors['accent_ultra_light'])
            content_frame.configure(bg=self.colors['accent_ultra_light'])
            
        def on_leave(e):
            tile_frame.configure(highlightbackground=self.colors['border_light'],
                               highlightthickness=1,
                               bg=self.colors['bg_secondary'])
            content_frame.configure(bg=self.colors['bg_secondary'])
            
        # Bind to all tile elements
        for widget in [tile_frame, content_frame]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            
        # Add premium hover effect to launch button
        button.bind("<Enter>", lambda e: button.configure(bg=self.colors['accent_hover']))
        button.bind("<Leave>", lambda e: button.configure(bg=self.colors['accent']))
            
    def filter_apps(self):
        """Filter apps based on search only (no categories anymore)"""
        apps = self.apps.copy()
            
        # Filter by search
        search_term = self.search_var.get().lower()
        if search_term and search_term != "søg apps...":
            apps = [app for app in apps if 
                   search_term in app['name'].lower() or 
                   search_term in app['description'].lower()]
                   
        return apps
    
    # Event handlers and utility methods
    def center_window(self):
        """Center the window on the screen"""
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f"{width}x{height}+{x}+{y}")
        
    def on_button_hover(self, button, is_enter):
        """Handle button hover effects (legacy)"""
        if is_enter:
            button.configure(bg=self.colors['accent_light'])
        else:
            button.configure(bg=self.colors['bg_sidebar'])
            
    def on_modern_button_hover(self, button, is_enter):
        """Handle modern button hover effects"""
        if is_enter:
            button.configure(bg=self.colors['accent_light'], 
                           fg=self.colors['accent'])
        else:
            button.configure(bg=self.colors['bg_sidebar'], 
                           fg=self.colors['text_secondary'])
    
    def on_sidebar_button_hover(self, button, is_enter):
        """Handle dark sidebar button hover effects"""
        if is_enter:
            button.configure(bg=self.colors['sidebar_accent'], 
                           fg=self.colors['text_white'])
        else:
            button.configure(bg=self.colors['bg_sidebar'], 
                           fg=self.colors['text_sidebar'])
            
    def on_search_focus_in(self, event):
        """Handle search entry focus in"""
        if event.widget.get() == "Søg apps...":
            event.widget.delete(0, tk.END)
            event.widget.configure(fg=self.colors['text_primary'])
            
    def on_search_focus_out(self, event):
        """Handle search entry focus out"""
        if not event.widget.get():
            event.widget.insert(0, "Søg apps...")
            event.widget.configure(fg=self.colors['text_secondary'])
            
    def on_search_change(self, event):
        """Handle search text changes"""
        self.update_app_display()
        
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def filter_by_category(self, category):
        """Filter apps by category - removed"""
        pass
        
    def launch_app(self, app):
        """Launch an application"""
        action = app.get('action')
        
        if action == 'simple_resizer':
            try:
                resizer = SimpleImageResizer(self.master)
                resizer.show()
                # Ensure proper window focus
                if hasattr(resizer, 'window') and resizer.window:
                    resizer.window.lift()
                    resizer.window.focus_force()
            except Exception as e:
                messagebox.showerror("Fejl", f"Kunne ikke starte Simpel Billedkomprimering:\n{str(e)}", parent=self.master)
        
        elif action == 'group_processor':
            try:
                processor = GroupImageProcessor(self.master)
                processor.show()
                # Ensure proper window focus
                if hasattr(processor, 'window') and processor.window:
                    processor.window.lift()
                    processor.window.focus_force()
            except Exception as e:
                messagebox.showerror("Fejl", f"Kunne ikke starte Gruppe Billedbehandler:\n{str(e)}", parent=self.master)
        
        elif action == 'individual_processor':
            try:
                processor = IndividualImageProcessor(self.master)
                processor.show()
                # Ensure proper window focus
                if hasattr(processor, 'window') and processor.window:
                    processor.window.lift()
                    processor.window.focus_force()
            except Exception as e:
                messagebox.showerror("Fejl", f"Kunne ikke starte Individuel Billedbehandler:\n{str(e)}", parent=self.master)
        
        elif app['name'] == 'Indstillinger':
            self.open_settings()
        
        else:
            # Default placeholder for other apps
            messagebox.showinfo("Start App", 
                               f"Starter {app['name']}...\n\n"
                               f"{app['description']}\n\n"
                               "Dette er en placeholder. Du kan integrere rigtig app-start her.")
        
    def add_new_app(self):
        """Add a new app to the hub - removed"""
        pass
    
    def open_github(self):
        """Open GitHub repository"""
        import webbrowser
        try:
            github_url = "https://github.com/DivEden/DGB_assistent"
            webbrowser.open(github_url)
        except Exception as e:
            messagebox.showinfo("GitHub", 
                               "Kunne ikke åbne GitHub repository.\n\n"
                               "Du kan besøge https://github.com/DivEden/DGB_assistent manuelt.")
        
    def open_api_config(self):
        """Open API configuration dialog"""
        try:
            from utils.secure_config import get_secure_config
            secure_config = get_secure_config()
            
            # Show credentials setup dialog
            success = secure_config.setup_credentials_gui(self.master)
            
            if success:
                messagebox.showinfo("API Konfiguration", 
                                   "API legitimationsoplysninger er gemt sikkert!\n\n"
                                   "Du kan nu bruge API-funktioner i applikationen.",
                                   parent=self.master)
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke åbne API konfiguration: {str(e)}")
    
    def open_settings(self):
        """Open application settings"""
        try:
            dialog = SettingsDialog(self.master, self.settings_manager)
            dialog.show()
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke åbne indstillinger: {str(e)}")
        
    def show_about(self):
        """Show about dialog"""
        about_text = (f"DGB Assistent\n"
                     f"Version 1.0.0\n\n"
                     f"En moderne applikationslauncher og arbejdsområde hub.\n"
                     f"Bygget med Python og Tkinter.\n\n"
                     f"Python Version: {sys.version.split()[0]}\n"
                     f"Platform: {sys.platform}\n"
                     f"Tilgængelige Apps: {len(self.apps)}")
        
        messagebox.showinfo("Om DGB Assistent", about_text)
    
    def check_for_updates(self):
        """Check for application updates in background"""
        # Only check if auto-updates are enabled
        if not self.settings_manager.get('auto_update_enabled', True):
            return
            
        def on_update_available(release_info):
            """Called when an update is available"""
            # Only show notification if enabled
            if self.settings_manager.get('show_update_notifications', True):
                # Schedule the dialog to show on the main thread
                self.master.after(0, lambda: self.show_update_dialog(release_info))
        
        # Update the check frequency
        self.updater.check_interval_days = self.settings_manager.get('check_frequency_days', 1)
        
        # Start background check
        self.updater.check_for_updates_async(on_update_available)
    
    def show_update_dialog(self, release_info):
        """Show the update notification dialog"""
        try:
            dialog = UpdateDialog(self.master, release_info, self.updater)
            dialog.show()
        except Exception as e:
            print(f"Error showing update dialog: {e}")


# Create alias for backward compatibility
MainWindow = ModernAppHub