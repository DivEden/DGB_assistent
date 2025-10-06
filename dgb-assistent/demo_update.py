"""
Test Script for DGB Assistent Auto-Update System
This demonstrates how the update system works
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.updater import UpdateDialog
from config import APP_VERSION

def demo_update_dialog():
    """Demo the update notification dialog"""
    
    # Create a simple root window
    root = tk.Tk()
    root.title("DGB Assistent Update Demo")
    root.geometry("400x200")
    root.configure(bg='#ffffff')
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (400 // 2)
    y = (root.winfo_screenheight() // 2) - (200 // 2)
    root.geometry(f"400x200+{x}+{y}")
    
    # Demo content
    title_label = tk.Label(root, 
                          text="🚀 DGB Assistent Update Demo",
                          font=('Segoe UI', 14, 'bold'),
                          fg='#1e293b', bg='#ffffff')
    title_label.pack(pady=20)
    
    version_label = tk.Label(root,
                           text=f"Nuværende version: {APP_VERSION}",
                           font=('Segoe UI', 10),
                           fg='#475569', bg='#ffffff')
    version_label.pack(pady=5)
    
    info_label = tk.Label(root,
                         text="Klik knappen for at se opdateringsnotifikationen",
                         font=('Segoe UI', 10),
                         fg='#64748b', bg='#ffffff')
    info_label.pack(pady=10)
    
    def show_demo_update():
        # Create fake release info
        fake_release_info = {
            'tag_name': 'v1.2.0',
            'name': 'DGB Assistent v1.2.0',
            'html_url': 'https://github.com/your-username/dgb-assistent/releases/tag/v1.2.0',
            'body': '''🚀 **Nye Funktioner:**
• Forbedret brugergrænse med hurtigere navigation
• Ny søgefunktionalitet med filtrering
• Optimeret ydeevne og hurtigere opstart
• Opdateret sikkerhed og stabilitet

🔧 **Fejlrettelser:**
• Løst problem med app-ikoner på høj-DPI skærme
• Forbedret kompatibilitet med Windows 11
• Mindre UI-forbedringer og polering

📱 **Tekniske Forbedringer:**
• Reduceret hukommelsesforbrug med 25%
• Hurtigere app-loading og responsivitet
• Forbedret auto-opdateringssystem''',
            'assets': [
                {
                    'name': 'DGB-Assistent-v1.2.0.zip',
                    'browser_download_url': 'https://github.com/your-username/dgb-assistent/releases/download/v1.2.0/DGB-Assistent-v1.2.0.zip'
                }
            ]
        }
        
        # Create fake updater (we won't actually update)
        class FakeUpdater:
            def download_update(self, url, progress_callback=None):
                return None  # Fake download
        
        fake_updater = FakeUpdater()
        
        # Show the update dialog
        dialog = UpdateDialog(root, fake_release_info, fake_updater)
        dialog.show()
    
    # Demo button
    demo_btn = tk.Button(root,
                        text="Vis Opdateringsnotifikation",
                        font=('Segoe UI', 10, 'bold'),
                        fg='#ffffff', bg='#3b82f6',
                        activebackground='#2563eb',
                        relief=tk.FLAT, bd=0,
                        padx=20, pady=10,
                        cursor='hand2',
                        command=show_demo_update)
    demo_btn.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    print("🚀 Starting DGB Assistent Update Demo...")
    print(f"Current Version: {APP_VERSION}")
    print("Demonstrating the auto-update system...")
    demo_update_dialog()