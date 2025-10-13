"""
Test model af SARA Søge App
En simpel prototype til at teste Axiell API funktionalitet
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from utils.axiell_api import AxiellAPIClient
except ImportError as e:
    print(f"Import error: {e}")
    print("Kunne ikke importere AxiellAPIClient")

class SaraSearchTestApp:
    """Test prototype af SARA søgefunktion"""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("SARA Søge Test - DGB Assistent")
        self.window.geometry("600x500")
        self.window.configure(bg='#f8fafc')
        
        # Colors matching DGB Assistent
        self.colors = {
            'primary': '#002852',
            'secondary': '#ffffff', 
            'accent': '#3b82f6',
            'text': '#1e293b',
            'text_light': '#64748b',
            'border': '#e2e8f0'
        }
        
        self.setup_ui()
        
        # Initialize API client
        try:
            self.api_client = AxiellAPIClient()
            self.status_label.config(text="✅ API client initialiseret", fg='#10b981')
        except Exception as e:
            self.api_client = None
            self.status_label.config(text=f"❌ API fejl: {str(e)}", fg='#ef4444')
    
    def setup_ui(self):
        """Opret brugerinterface"""
        # Header
        header_frame = tk.Frame(self.window, bg=self.colors['primary'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                              text="🔍 SARA Objektsøgning", 
                              font=('Segoe UI', 18, 'bold'),
                              fg='white', bg=self.colors['primary'])
        title_label.pack(pady=20)
        
        # Main content
        main_frame = tk.Frame(self.window, bg=self.colors['secondary'], padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search section
        search_label = tk.Label(main_frame, text="Objektnummer:", 
                               font=('Segoe UI', 12, 'bold'),
                               fg=self.colors['text'], bg=self.colors['secondary'])
        search_label.pack(anchor=tk.W, pady=(0, 5))
        
        search_frame = tk.Frame(main_frame, bg=self.colors['secondary'])
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.search_entry = tk.Entry(search_frame, font=('Segoe UI', 11),
                                    relief=tk.SOLID, bd=1, 
                                    highlightbackground=self.colors['border'])
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.search_entry.insert(0, "0054x0007")  # Test eksempel
        
        search_btn = tk.Button(search_frame, text="Søg",
                              font=('Segoe UI', 10, 'bold'),
                              fg='white', bg=self.colors['accent'],
                              relief=tk.FLAT, padx=20, pady=8,
                              cursor='hand2',
                              command=self.search_object)
        search_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Status
        self.status_label = tk.Label(main_frame, text="Venter på søgning...",
                                    font=('Segoe UI', 9),
                                    fg=self.colors['text_light'], 
                                    bg=self.colors['secondary'])
        self.status_label.pack(pady=(0, 15))
        
        # Results area
        results_label = tk.Label(main_frame, text="Søgeresultater:",
                                font=('Segoe UI', 12, 'bold'),
                                fg=self.colors['text'], bg=self.colors['secondary'])
        results_label.pack(anchor=tk.W, pady=(10, 5))
        
        # Scrollable text area for results
        text_frame = tk.Frame(main_frame, bg=self.colors['secondary'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(text_frame, font=('Consolas', 10),
                                   relief=tk.SOLID, bd=1,
                                   highlightbackground=self.colors['border'],
                                   wrap=tk.WORD, padx=15, pady=15)
        
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind Enter key to search
        self.search_entry.bind('<Return>', lambda e: self.search_object())
        
        # Instructions
        instructions = (
            "Indtast et objektnummer (f.eks. '0054x0007') og tryk Søg.\n"
            "Dette tester forbindelsen til SARA API'en."
        )
        self.results_text.insert(tk.END, instructions)
        
    def search_object(self):
        """Søg efter objekt i SARA"""
        if not self.api_client:
            messagebox.showerror("Fejl", "API client ikke tilgængelig")
            return
            
        objektnummer = self.search_entry.get().strip()
        if not objektnummer:
            messagebox.showwarning("Advarsel", "Indtast et objektnummer")
            return
            
        # Clear results og vis loading
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Søger efter '{objektnummer}'...\n\n")
        self.window.update()
        
        try:
            # Test authentication først
            self.status_label.config(text="🔄 Autentificerer...", fg=self.colors['text_light'])
            self.window.update()
            
            auth_success = self.api_client.authenticate()
            if not auth_success:
                self.results_text.insert(tk.END, "❌ Autentificering fejlede\n")
                self.status_label.config(text="❌ Autentificering fejlede", fg='#ef4444')
                return
                
            self.results_text.insert(tk.END, "✅ Autentificeret succesfuldt\n\n")
            
            # Søg efter objektet
            self.status_label.config(text="🔍 Søger i SARA...", fg=self.colors['text_light'])
            self.window.update()
            
            results = self.api_client.search_objects(objektnummer)
            
            if results and len(results) > 0:
                self.status_label.config(text=f"✅ Fundet {len(results)} resultat(er)", fg='#10b981')
                
                for i, obj in enumerate(results, 1):
                    self.results_text.insert(tk.END, f"═══ RESULTAT {i} ═══\n")
                    
                    # Vis vigtige felter
                    if 'object_number' in obj:
                        self.results_text.insert(tk.END, f"Objektnummer: {obj['object_number']}\n")
                    if 'title' in obj:
                        self.results_text.insert(tk.END, f"Titel: {obj['title']}\n")
                    if 'description' in obj:
                        self.results_text.insert(tk.END, f"Beskrivelse: {obj['description']}\n")
                    if 'priref' in obj:
                        self.results_text.insert(tk.END, f"Priref: {obj['priref']}\n")
                    
                    # Vis alle data
                    self.results_text.insert(tk.END, f"\nAlle data:\n")
                    for key, value in obj.items():
                        if value:  # Kun vis felter med indhold
                            self.results_text.insert(tk.END, f"  {key}: {value}\n")
                    
                    self.results_text.insert(tk.END, f"\n")
            else:
                self.status_label.config(text="❌ Ingen resultater fundet", fg='#ef4444')
                self.results_text.insert(tk.END, f"Ingen objekter fundet for '{objektnummer}'\n")
                
        except Exception as e:
            error_msg = f"Fejl under søgning: {str(e)}"
            self.status_label.config(text="❌ Søgefejl", fg='#ef4444')
            self.results_text.insert(tk.END, f"❌ {error_msg}\n")
            print(f"Search error: {e}")
    
    def run(self):
        """Start appen"""
        self.window.mainloop()

if __name__ == "__main__":
    print("Starter SARA Søge Test App...")
    app = SaraSearchTestApp()
    app.run()