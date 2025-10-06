"""
Auto-Updater System for DGB Assistent
Checks GitHub releases and handles automatic updates
"""

import requests
import json
import os
import sys
import threading
import zipfile
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
from datetime import datetime, timedelta


class AutoUpdater:
    """Handles automatic updates from GitHub releases"""
    
    def __init__(self, current_version, repo_owner, repo_name):
        self.current_version = current_version
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        self.check_interval_days = 1  # Check daily
        self.last_check_file = Path.home() / "AppData" / "Local" / "DGB-Assistent" / "last_update_check.txt"
        
    def should_check_for_updates(self):
        """Check if it's time to check for updates"""
        try:
            if not self.last_check_file.exists():
                return True
                
            with open(self.last_check_file, 'r') as f:
                last_check = datetime.fromisoformat(f.read().strip())
                
            return datetime.now() - last_check > timedelta(days=self.check_interval_days)
        except:
            return True
    
    def update_last_check_time(self):
        """Update the last check time"""
        try:
            self.last_check_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.last_check_file, 'w') as f:
                f.write(datetime.now().isoformat())
        except:
            pass
    
    def get_latest_release_info(self):
        """Get latest release information from GitHub"""
        try:
            response = requests.get(self.github_api_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Failed to check for updates: {e}")
            return None
    
    def compare_versions(self, latest_version):
        """Compare current version with latest version"""
        def parse_version(version):
            # Remove 'v' prefix if present and split by '.'
            version = version.lstrip('v')
            return [int(x) for x in version.split('.')]
        
        try:
            current = parse_version(self.current_version)
            latest = parse_version(latest_version)
            
            # Compare version numbers
            for i in range(max(len(current), len(latest))):
                c = current[i] if i < len(current) else 0
                l = latest[i] if i < len(latest) else 0
                
                if l > c:
                    return True  # Update available
                elif l < c:
                    return False  # Current version is newer
            
            return False  # Versions are equal
        except:
            return False
    
    def check_for_updates_async(self, callback=None):
        """Check for updates in background thread"""
        def check():
            try:
                if not self.should_check_for_updates():
                    return
                
                release_info = self.get_latest_release_info()
                if not release_info:
                    return
                
                latest_version = release_info['tag_name']
                if self.compare_versions(latest_version):
                    if callback:
                        callback(release_info)
                
                self.update_last_check_time()
            except Exception as e:
                print(f"Update check error: {e}")
        
        thread = threading.Thread(target=check, daemon=True)
        thread.start()
    
    def download_update(self, download_url, progress_callback=None):
        """Download the update file with progress tracking"""
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            # Create temporary download location
            temp_dir = Path.home() / "AppData" / "Local" / "DGB-Assistent" / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            download_path = temp_dir / "update.zip"
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            return download_path
        except Exception as e:
            print(f"Download error: {e}")
            return None
    
    def install_update(self, update_path):
        """Install the downloaded update"""
        try:
            # Get current application directory
            if getattr(sys, 'frozen', False):
                # Running as executable
                app_dir = Path(sys.executable).parent
            else:
                # Running as script
                app_dir = Path(__file__).parent.parent.parent
            
            # Create backup
            backup_dir = app_dir.parent / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree(app_dir, backup_dir)
            
            # Extract update
            with zipfile.ZipFile(update_path, 'r') as zip_ref:
                zip_ref.extractall(app_dir.parent / "temp_update")
            
            # Find the extracted application folder
            temp_update_dir = app_dir.parent / "temp_update"
            extracted_dirs = [d for d in temp_update_dir.iterdir() if d.is_dir()]
            
            if extracted_dirs:
                new_app_dir = extracted_dirs[0]
                
                # Replace application files
                for item in new_app_dir.iterdir():
                    dest = app_dir / item.name
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink()
                    
                    if item.is_dir():
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)
            
            # Cleanup
            shutil.rmtree(temp_update_dir)
            update_path.unlink()
            
            return True
        except Exception as e:
            print(f"Installation error: {e}")
            return False


class UpdateDialog:
    """Modern update notification dialog"""
    
    def __init__(self, parent, release_info, updater):
        self.parent = parent
        self.release_info = release_info
        self.updater = updater
        self.dialog = None
        
    def show(self):
        """Show the update dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Opdatering Tilgængelig - DGB Assistent")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the update dialog widgets"""
        main_frame = tk.Frame(self.dialog, bg='#ffffff', padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Update icon and title
        title_frame = tk.Frame(main_frame, bg='#ffffff')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        icon_label = tk.Label(title_frame, text="🚀", font=('Segoe UI', 32), bg='#ffffff')
        icon_label.pack(side=tk.LEFT)
        
        title_text_frame = tk.Frame(title_frame, bg='#ffffff')
        title_text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(15, 0))
        
        title_label = tk.Label(title_text_frame, 
                              text="Ny Opdatering Tilgængelig!", 
                              font=('Segoe UI', 16, 'bold'), 
                              fg='#1e293b', bg='#ffffff')
        title_label.pack(anchor=tk.W)
        
        version_label = tk.Label(title_text_frame,
                               text=f"Version {self.release_info['tag_name']} er klar til download",
                               font=('Segoe UI', 10),
                               fg='#475569', bg='#ffffff')
        version_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Release notes
        notes_frame = tk.LabelFrame(main_frame, text="Hvad er nyt:", 
                                  font=('Segoe UI', 10, 'bold'),
                                  fg='#1e293b', bg='#ffffff',
                                  padx=15, pady=15)
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Scrollable text for release notes
        text_frame = tk.Frame(notes_frame, bg='#ffffff')
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        release_text = tk.Text(text_frame,
                             yscrollcommand=scrollbar.set,
                             font=('Segoe UI', 9),
                             bg='#f8fafc', fg='#334155',
                             relief=tk.FLAT, bd=0,
                             wrap=tk.WORD, padx=10, pady=10)
        release_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=release_text.yview)
        
        # Insert release notes
        release_notes = self.release_info.get('body', 'Ingen detaljer tilgængelige.')
        release_text.insert(tk.END, release_notes)
        release_text.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#ffffff')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Later button
        later_btn = tk.Button(button_frame, 
                            text="Senere",
                            font=('Segoe UI', 10),
                            fg='#475569', bg='#f1f5f9',
                            activebackground='#e2e8f0',
                            relief=tk.FLAT, bd=0,
                            padx=20, pady=10,
                            cursor='hand2',
                            command=self.close_dialog)
        later_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # View on GitHub button
        github_btn = tk.Button(button_frame,
                             text="Se på GitHub",
                             font=('Segoe UI', 10),
                             fg='#1e293b', bg='#e2e8f0',
                             activebackground='#cbd5e1',
                             relief=tk.FLAT, bd=0,
                             padx=20, pady=10,
                             cursor='hand2',
                             command=self.open_github)
        github_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Update button
        update_btn = tk.Button(button_frame,
                             text="Opdater Nu",
                             font=('Segoe UI', 10, 'bold'),
                             fg='#ffffff', bg='#3b82f6',
                             activebackground='#2563eb',
                             relief=tk.FLAT, bd=0,
                             padx=20, pady=10,
                             cursor='hand2',
                             command=self.start_update)
        update_btn.pack(side=tk.RIGHT)
    
    def close_dialog(self):
        """Close the update dialog"""
        if self.dialog:
            self.dialog.destroy()
    
    def open_github(self):
        """Open the GitHub release page"""
        webbrowser.open(self.release_info['html_url'])
    
    def start_update(self):
        """Start the update process"""
        self.close_dialog()
        
        # Find the downloadable asset (zip file)
        download_url = None
        for asset in self.release_info.get('assets', []):
            if asset['name'].endswith('.zip'):
                download_url = asset['browser_download_url']
                break
        
        if not download_url:
            messagebox.showerror("Fejl", 
                               "Kunne ikke finde download link for opdateringen.\n"
                               "Besøg GitHub manuelt for at downloade.")
            return
        
        # Show progress dialog
        self.show_progress_dialog(download_url)
    
    def show_progress_dialog(self, download_url):
        """Show download and installation progress"""
        progress_dialog = tk.Toplevel(self.parent)
        progress_dialog.title("Opdaterer DGB Assistent")
        progress_dialog.geometry("400x150")
        progress_dialog.resizable(False, False)
        progress_dialog.transient(self.parent)
        progress_dialog.grab_set()
        
        # Center dialog
        progress_dialog.update_idletasks()
        x = (progress_dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (progress_dialog.winfo_screenheight() // 2) - (150 // 2)
        progress_dialog.geometry(f"400x150+{x}+{y}")
        
        frame = tk.Frame(progress_dialog, bg='#ffffff', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        status_label = tk.Label(frame, text="Downloader opdatering...",
                               font=('Segoe UI', 10),
                               fg='#1e293b', bg='#ffffff')
        status_label.pack(pady=(0, 10))
        
        progress_bar = ttk.Progressbar(frame, mode='determinate', length=350)
        progress_bar.pack(pady=(0, 10))
        
        def update_progress(percentage):
            progress_bar['value'] = percentage
            progress_dialog.update()
        
        def download_and_install():
            try:
                # Download
                status_label.config(text="Downloader opdatering...")
                download_path = self.updater.download_update(download_url, update_progress)
                
                if download_path:
                    # Install
                    status_label.config(text="Installerer opdatering...")
                    progress_bar['value'] = 100
                    progress_dialog.update()
                    
                    if self.updater.install_update(download_path):
                        progress_dialog.destroy()
                        result = messagebox.showinfo("Opdatering Fuldført", 
                                                   "DGB Assistent er blevet opdateret!\n"
                                                   "Applikationen vil nu genstarte.")
                        if result:
                            # Restart application
                            if getattr(sys, 'frozen', False):
                                subprocess.Popen([sys.executable])
                            else:
                                subprocess.Popen([sys.executable, __file__])
                            sys.exit()
                    else:
                        progress_dialog.destroy()
                        messagebox.showerror("Fejl", "Opdateringen fejlede. Prøv igen senere.")
                else:
                    progress_dialog.destroy()
                    messagebox.showerror("Fejl", "Download fejlede. Tjek din internetforbindelse.")
            except Exception as e:
                progress_dialog.destroy()
                messagebox.showerror("Fejl", f"Opdateringsfejl: {str(e)}")
        
        # Start download in thread
        thread = threading.Thread(target=download_and_install, daemon=True)
        thread.start()