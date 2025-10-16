"""
Group Image Processor - DGB Assistent
Grupperer billeder og navngiver dem systematisk (a, b, c, osv.)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
try:
    from tkinter import simpledialog
except ImportError:
    import tkinter.simpledialog as simpledialog
import os
from pathlib import Path
import io
import gc
import json
import zipfile
import tempfile
from PIL import Image, ImageTk
import threading
from typing import List, Dict, Optional
from .museum_organizer import MuseumOrganizer
# Import SARA batch upload
try:
    from utils.sara_browser_uploader import SaraBatchUploader
    SARA_UPLOAD_AVAILABLE = True
except ImportError:
    try:
        from ...utils.sara_browser_uploader import SaraBatchUploader
        SARA_UPLOAD_AVAILABLE = True
    except ImportError:
        # Fallback for PyInstaller or direct execution
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
        try:
            from sara_browser_uploader import SaraBatchUploader
            SARA_UPLOAD_AVAILABLE = True
        except ImportError:
            # SARA upload not available
            SARA_UPLOAD_AVAILABLE = False


class GroupImageProcessor:
    """Group-based image processing tool"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.selected_files = []
        self.image_groups = []
        self.processed_files = []
        self.processing = False
        self.museum_organizer = MuseumOrganizer()
        
    def show(self):
        """Show the group image processor window"""
        if self.window is None or not self.window.winfo_exists():
            self.create_window()
        else:
            self.window.lift()
            self.window.focus_force()
    
    def create_window(self):
        """Create the main window"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Gruppe Billedbehandler - DGB Assistent")
        self.window.geometry("1000x700")
        self.window.configure(bg='#f8fafc')
        
        # Colors matching DGB Assistent theme
        self.colors = {
            'bg_primary': '#f8fafc',
            'bg_secondary': '#ffffff',
            'accent': '#3b82f6',
            'accent_hover': '#2563eb',
            'text_primary': '#0f172a',
            'text_secondary': '#475569',
            'border': '#e2e8f0',
            'success': '#10b981',
            'warning': '#f59e0b'
        }
        
        self.create_interface()
        
    def create_interface(self):
        """Create the user interface"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="👥 Gruppe Billedbehandler", 
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.colors['text_primary'],
                              bg=self.colors['bg_primary'])
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = tk.Label(main_frame,
                             text="Gruppér billeder og navngiv dem systematisk (a, b, c, osv.)",
                             font=('Segoe UI', 11),
                             fg=self.colors['text_secondary'],
                             bg=self.colors['bg_primary'])
        desc_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Tab 1: File selection and grouping
        self.setup_tab = ttk.Frame(notebook)
        notebook.add(self.setup_tab, text="1. Opsætning")
        self.create_setup_tab()
        
        # Tab 2: Settings and processing
        self.process_tab = ttk.Frame(notebook)
        notebook.add(self.process_tab, text="2. Behandling")
        self.create_process_tab()
        
        # Tab 3: Results
        self.results_tab = ttk.Frame(notebook)
        notebook.add(self.results_tab, text="3. Resultater")
        self.create_results_tab()
        
    def create_setup_tab(self):
        """Create the setup tab"""
        # File selection
        file_frame = ttk.LabelFrame(self.setup_tab, text="Vælg Billeder", padding=15)
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        select_btn = tk.Button(file_frame,
                              text="📁 Vælg Billeder",
                              font=('Segoe UI', 11, 'bold'),
                              bg=self.colors['accent'],
                              fg='white',
                              relief=tk.FLAT,
                              padx=20, pady=10,
                              cursor='hand2',
                              command=self.select_files)
        select_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_count_label = ttk.Label(file_frame, text="Ingen filer valgt")
        self.file_count_label.pack(side=tk.LEFT)
        
        # Main container for image area and groups
        main_container = ttk.Frame(self.setup_tab)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left side: Image thumbnails
        images_frame = ttk.LabelFrame(main_container, text="Valgte Billeder", padding=10)
        images_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Canvas for image thumbnails with drag support
        canvas_frame = ttk.Frame(images_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_canvas = tk.Canvas(canvas_frame, bg='white', height=300)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.setup_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.setup_canvas.xview)
        
        self.setup_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.setup_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Bind mousewheel for images canvas
        self.setup_canvas.bind("<MouseWheel>", self.on_images_mousewheel)
        
        # Right side: Groups area
        self.groups_container = ttk.LabelFrame(main_container, text="Grupper", padding=10)
        self.groups_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(10, 0))
        self.groups_container.configure(width=300)
        
        # Group management buttons
        group_btn_frame = ttk.Frame(self.groups_container)
        group_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        add_group_btn = tk.Button(group_btn_frame,
                                 text="➕ Ny Gruppe",
                                 font=('Segoe UI', 10),
                                 bg=self.colors['success'],
                                 fg='white',
                                 relief=tk.FLAT,
                                 padx=15, pady=8,
                                 cursor='hand2',
                                 command=self.add_new_group)
        add_group_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_groups_btn = tk.Button(group_btn_frame,
                                    text="🗑️ Ryd Grupper",
                                    font=('Segoe UI', 10),
                                    bg=self.colors['warning'],
                                    fg='white',
                                    relief=tk.FLAT,
                                    padx=15, pady=8,
                                    cursor='hand2',
                                    command=self.clear_groups)
        clear_groups_btn.pack(side=tk.LEFT)
        
        # Scrollable groups display
        groups_canvas_frame = ttk.Frame(self.groups_container)
        groups_canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.groups_canvas = tk.Canvas(groups_canvas_frame, bg='white', width=280)
        groups_v_scrollbar = ttk.Scrollbar(groups_canvas_frame, orient="vertical", command=self.groups_canvas.yview)
        
        self.groups_scrollable_frame = tk.Frame(self.groups_canvas, bg='white')
        
        self.groups_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.groups_canvas.configure(scrollregion=self.groups_canvas.bbox("all"))
        )
        
        self.groups_canvas.create_window((0, 0), window=self.groups_scrollable_frame, anchor="nw")
        self.groups_canvas.configure(yscrollcommand=groups_v_scrollbar.set)
        
        self.groups_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        groups_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mousewheel for groups canvas  
        self.groups_canvas.bind("<MouseWheel>", self.on_groups_mousewheel)
        
    def create_process_tab(self):
        """Create the processing tab"""
        # Settings
        settings_frame = ttk.LabelFrame(self.process_tab, text="Behandlingsindstillinger", padding=15)
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Small image size setting
        size_frame = ttk.Frame(settings_frame)
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(size_frame, text="Lille billede størrelse (KB):").pack(side=tk.LEFT)
        
        self.small_size_var = tk.IntVar(value=300)
        size_spinbox = ttk.Spinbox(size_frame, 
                                  from_=50, to=2000, 
                                  textvariable=self.small_size_var,
                                  width=10)
        size_spinbox.pack(side=tk.RIGHT)
        
        # AAB prefix option
        self.use_aab_var = tk.BooleanVar(value=False)
        aab_check = ttk.Checkbutton(settings_frame,
                                   text="Brug 'AAB' præfiks i filnavne",
                                   variable=self.use_aab_var)
        aab_check.pack(anchor=tk.W, pady=(0, 10))
        
        # Auto-organize option
        self.auto_organize_var = tk.BooleanVar(value=False)
        organize_check = ttk.Checkbutton(settings_frame,
                                        text="Auto-organisér til museum mapper (kun lokalt)",
                                        variable=self.auto_organize_var)
        organize_check.pack(anchor=tk.W)
        
        # Processing area
        process_frame = ttk.LabelFrame(self.process_tab, text="Start Behandling", padding=15)
        process_frame.pack(fill=tk.BOTH, expand=True)
        
        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(process_frame, 
                                           variable=self.progress_var,
                                           length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(process_frame, text="Klar til behandling")
        self.status_label.pack(pady=(0, 20))
        
        # Start button
        self.start_btn = tk.Button(process_frame,
                                  text="🚀 Start Behandling",
                                  font=('Segoe UI', 12, 'bold'),
                                  bg=self.colors['success'],
                                  fg='white',
                                  relief=tk.FLAT,
                                  padx=30, pady=15,
                                  cursor='hand2',
                                  command=self.start_processing,
                                  state=tk.DISABLED)
        self.start_btn.pack()
        
    def create_results_tab(self):
        """Create the results tab"""
        # Results summary
        self.results_summary_frame = ttk.LabelFrame(self.results_tab, text="Resultat Oversigt", padding=15)
        self.results_summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Download options
        download_frame = ttk.LabelFrame(self.results_tab, text="Download Muligheder", padding=15)
        download_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.download_zip_btn = tk.Button(download_frame,
                                         text="📦 Download ZIP",
                                         font=('Segoe UI', 11, 'bold'),
                                         bg=self.colors['accent'],
                                         fg='white',
                                         relief=tk.FLAT,
                                         padx=20, pady=10,
                                         cursor='hand2',
                                         command=self.download_zip,
                                         state=tk.DISABLED)
        self.download_zip_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_sara_btn = tk.Button(download_frame,
                                            text="Gem i SARA",
                                            font=('Segoe UI', 11, 'bold'),
                                            bg=self.colors['success'],
                                            fg='white',
                                            relief=tk.FLAT,
                                            padx=20, pady=10,
                                            cursor='hand2',
                                            command=self.upload_to_sara,
                                            state=tk.DISABLED)
        self.save_sara_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.organize_btn = tk.Button(download_frame,
                                     text="🗂️ Organiser til Museum",
                                     font=('Segoe UI', 11, 'bold'),
                                     bg=self.colors['warning'],
                                     fg='white',
                                     relief=tk.FLAT,
                                     padx=20, pady=10,
                                     cursor='hand2',
                                     command=self.organize_to_museum,
                                     state=tk.DISABLED)
        self.organize_btn.pack(side=tk.LEFT)
        
    def select_files(self):
        """Select image files to process"""
        file_types = [
            ('Billedfiler', '*.jpg *.jpeg *.png *.bmp *.tiff *.webp'),
            ('JPEG filer', '*.jpg *.jpeg'),
            ('PNG filer', '*.png'),
            ('Alle filer', '*.*')
        ]
        
        # Bring window to front before showing dialog
        if self.window:
            self.window.lift()
            self.window.attributes('-topmost', True)
            self.window.update()
            self.window.attributes('-topmost', False)
        
        files = filedialog.askopenfilenames(
            title="Vælg billeder til gruppering",
            filetypes=file_types,
            parent=self.window
        )
        
        if files:
            self.selected_files = list(files)
            count = len(files)
            self.file_count_label.config(text=f"{count} filer valgt")
            self.load_image_thumbnails()
            
            # Reset groups when new files are selected
            self.image_groups.clear()
            self.update_groups_display()
            
            # Warn if too many files
            if count > 50:
                messagebox.showwarning("For mange filer", 
                                     f"Du har valgt {count} filer. For bedste ydeevne anbefales maks 50 filer ad gangen.",
                                     parent=self.window)
    
    def on_images_mousewheel(self, event):
        """Handle mouse wheel scrolling for images canvas"""
        self.setup_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_groups_mousewheel(self, event):
        """Handle mouse wheel scrolling for groups canvas"""
        self.groups_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def load_image_thumbnails(self):
        """Load thumbnails for selected images"""
        # Clear canvas
        self.setup_canvas.delete("all")
        
        # Clear previous image references
        self.setup_canvas.image_refs = []
        self.image_widgets = {}  # Track image widgets for selection
        
        # Create thumbnails in a grid
        col_width = 120
        row_height = 150
        cols_per_row = 4  # Reduced for better layout
        
        for i, file_path in enumerate(self.selected_files):
            try:
                # Create thumbnail
                img = Image.open(file_path)
                img.thumbnail((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Calculate position
                col = i % cols_per_row
                row = i // cols_per_row
                x_pos = col * col_width + 10
                y_pos = row * row_height + 10
                
                # Create image frame
                image_frame = self.setup_canvas.create_rectangle(x_pos, y_pos, x_pos + col_width - 10, y_pos + row_height - 10, 
                                                               outline='#e0e0e0', fill='white', width=1)
                
                # Create image on canvas
                image_id = self.setup_canvas.create_image(x_pos + 50, y_pos + 50, image=photo)
                text_id = self.setup_canvas.create_text(x_pos + 50, y_pos + 120, 
                                                       text=f"{i+1}: {os.path.basename(file_path)[:12]}...",
                                                       width=100, font=('Segoe UI', 8),
                                                       fill='#333')
                
                # Keep references
                self.setup_canvas.image_refs.append(photo)
                self.image_widgets[i] = {
                    'frame': image_frame,
                    'image': image_id, 
                    'text': text_id,
                    'selected': False,
                    'x': x_pos,
                    'y': y_pos
                }
                
                # Bind click events for selection
                for item_id in [image_frame, image_id, text_id]:
                    self.setup_canvas.tag_bind(item_id, "<Button-1>", 
                                              lambda e, idx=i: self.toggle_image_selection(idx))
                
            except Exception as e:
                print(f"Fejl ved indlæsning af thumbnail for {file_path}: {e}")
        
        # Update scroll region
        self.setup_canvas.configure(scrollregion=self.setup_canvas.bbox("all"))
    
    def toggle_image_selection(self, image_index: int):
        """Toggle image selection for grouping"""
        if image_index not in self.image_widgets:
            return
            
        widget_info = self.image_widgets[image_index]
        is_selected = widget_info['selected']
        
        # Toggle selection state
        widget_info['selected'] = not is_selected
        
        # Update visual appearance
        if widget_info['selected']:
            # Selected: blue border
            self.setup_canvas.itemconfig(widget_info['frame'], outline='#3b82f6', width=3)
            self.setup_canvas.itemconfig(widget_info['text'], fill='#3b82f6')
        else:
            # Unselected: gray border  
            self.setup_canvas.itemconfig(widget_info['frame'], outline='#e0e0e0', width=1)
            self.setup_canvas.itemconfig(widget_info['text'], fill='#333')
    
    def add_new_group(self):
        """Add a new group"""
        try:
            group_name = simpledialog.askstring("Ny Gruppe", "Indtast gruppenavn:", parent=self.window)
            if group_name and group_name.strip():
                new_group = {
                    'name': group_name.strip(),
                    'images': []
                }
                self.image_groups.append(new_group)
                self.update_groups_display()
                self.check_ready_for_processing()
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke oprette gruppe: {str(e)}", parent=self.window)
    
    def clear_groups(self):
        """Clear all groups"""
        if messagebox.askyesno("Bekræft", "Er du sikker på at du vil rydde alle grupper?", parent=self.window):
            self.image_groups.clear()
            self.update_groups_display()
            self.check_ready_for_processing()
    
    def update_groups_display(self):
        """Update the display of groups"""
        # Clear existing group displays
        for widget in self.groups_scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.image_groups:
            # Show instructions when no groups
            instructions = tk.Label(self.groups_scrollable_frame,
                                   text="Opret grupper og træk billeder hertil\n\n"
                                        "1. Klik 'Ny Gruppe'\n"
                                        "2. Vælg billeder (klik for at markere)\n"
                                        "3. Klik 'Tilføj til Gruppe'",
                                   font=('Segoe UI', 9),
                                   fg='#666',
                                   bg='white',
                                   justify=tk.CENTER)
            instructions.pack(pady=20)
            return
        
        # Display each group
        for group_idx, group in enumerate(self.image_groups):
            self.create_group_widget(group_idx, group)
        
        # Update scroll region
        self.groups_scrollable_frame.update_idletasks()
        self.groups_canvas.configure(scrollregion=self.groups_canvas.bbox("all"))
        
        # Update processing readiness
        self.check_ready_for_processing()
    
    def create_group_widget(self, group_idx: int, group: dict):
        """Create a widget for displaying and managing a group"""
        group_frame = tk.Frame(self.groups_scrollable_frame, bg='white', relief=tk.SOLID, bd=1)
        group_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Group header
        header_frame = tk.Frame(group_frame, bg='#f0f9ff')
        header_frame.pack(fill=tk.X, padx=2, pady=2)
        
        # Group name
        name_label = tk.Label(header_frame,
                             text=f"📁 {group['name']}",
                             font=('Segoe UI', 10, 'bold'),
                             bg='#f0f9ff',
                             fg='#1e40af')
        name_label.pack(side=tk.LEFT, padx=8, pady=5)
        
        # Group controls
        controls_frame = tk.Frame(header_frame, bg='#f0f9ff')
        controls_frame.pack(side=tk.RIGHT, padx=5)
        
        # Add selected images button
        add_btn = tk.Button(controls_frame,
                           text="+ Tilføj Valgte",
                           font=('Segoe UI', 8),
                           bg='#10b981',
                           fg='white',
                           relief=tk.FLAT,
                           padx=8, pady=3,
                           cursor='hand2',
                           command=lambda idx=group_idx: self.add_selected_to_group(idx))
        add_btn.pack(side=tk.LEFT, padx=2)
        
        # Remove group button
        remove_btn = tk.Button(controls_frame,
                              text="🗑️",
                              font=('Segoe UI', 8),
                              bg='#ef4444',
                              fg='white',
                              relief=tk.FLAT,
                              padx=6, pady=3,
                              cursor='hand2',
                              command=lambda idx=group_idx: self.remove_group(idx))
        remove_btn.pack(side=tk.LEFT, padx=2)
        
        # Group content
        content_frame = tk.Frame(group_frame, bg='white')
        content_frame.pack(fill=tk.X, padx=5, pady=5)
        
        if group['images']:
            # Show images in group
            for i, img_idx in enumerate(group['images']):
                if img_idx < len(self.selected_files):
                    filename = os.path.basename(self.selected_files[img_idx])
                    img_label = tk.Label(content_frame,
                                        text=f"  • {filename[:20]}..." if len(filename) > 20 else f"  • {filename}",
                                        font=('Segoe UI', 8),
                                        bg='white',
                                        fg='#333',
                                        anchor=tk.W)
                    img_label.pack(fill=tk.X)
            
            # Show count
            count_label = tk.Label(content_frame,
                                  text=f"Antal billeder: {len(group['images'])}",
                                  font=('Segoe UI', 8, 'italic'),
                                  bg='white',
                                  fg='#666')
            count_label.pack(pady=(5, 0))
        else:
            # Empty group message
            empty_label = tk.Label(content_frame,
                                  text="Ingen billeder i denne gruppe",
                                  font=('Segoe UI', 8, 'italic'),
                                  bg='white',
                                  fg='#999')
            empty_label.pack(pady=10)
    
    def add_selected_to_group(self, group_idx: int):
        """Add selected images to specified group"""
        if group_idx >= len(self.image_groups):
            return
            
        # Get selected image indices
        selected_indices = [idx for idx, widget in self.image_widgets.items() 
                           if widget['selected']]
        
        if not selected_indices:
            messagebox.showwarning("Ingen valgt", "Vælg først nogle billeder ved at klikke på dem.", 
                                 parent=self.window)
            return
        
        # Add to group (avoid duplicates)
        group = self.image_groups[group_idx]
        for idx in selected_indices:
            if idx not in group['images']:
                group['images'].append(idx)
        
        # Clear selections
        for idx in selected_indices:
            if idx in self.image_widgets:
                self.image_widgets[idx]['selected'] = False
                widget_info = self.image_widgets[idx]
                self.setup_canvas.itemconfig(widget_info['frame'], outline='#e0e0e0', width=1)
                self.setup_canvas.itemconfig(widget_info['text'], fill='#333')
        
        # Update display
        self.update_groups_display()
        
        # Show success message
        count = len(selected_indices)
        messagebox.showinfo("Tilføjet til Gruppe", 
                           f"{count} billede{'r' if count > 1 else ''} tilføjet til '{group['name']}'",
                           parent=self.window)
    
    def remove_group(self, group_idx: int):
        """Remove a group"""
        if group_idx < len(self.image_groups):
            group_name = self.image_groups[group_idx]['name']
            if messagebox.askyesno("Bekræft Sletning", 
                                 f"Slet gruppe '{group_name}'?",
                                 parent=self.window):
                del self.image_groups[group_idx]
                self.update_groups_display()
    
    def check_ready_for_processing(self):
        """Check if ready for processing and enable/disable start button"""
        ready = (len(self.selected_files) > 0 and 
                len(self.image_groups) > 0 and
                all(group['name'].strip() for group in self.image_groups) and
                not self.processing)
        
        self.start_btn.config(state=tk.NORMAL if ready else tk.DISABLED)
    
    def start_processing(self):
        """Start processing images in groups"""
        if self.processing or not self.image_groups:
            return
            
        self.processing = True
        self.start_btn.config(state=tk.DISABLED, text="⏳ Behandler...")
        
        # Reset progress
        self.progress_var.set(0)
        self.processed_files.clear()
        
        # Start processing in background thread
        thread = threading.Thread(target=self.process_groups, daemon=True)
        thread.start()
    
    def process_groups(self):
        """Process images in groups (runs in background thread)"""
        try:
            small_max_size_kb = self.small_size_var.get()
            use_aab_prefix = self.use_aab_var.get()
            
            total_images = sum(len(group['images']) for group in self.image_groups)
            processed_count = 0
            
            if total_images == 0:
                self.window.after(0, lambda: self.processing_error("Ingen billeder i grupperne"))
                return
            
            for group in self.image_groups:
                group_name = group['name'].strip()
                image_indices = group['images']
                
                if not image_indices:  # Skip empty groups
                    continue
                
                # Generate letter suffixes (a, b, c, ...)
                letters = [chr(97 + i) for i in range(len(image_indices))]
                
                for i, (image_index, letter) in enumerate(zip(image_indices, letters)):
                    if image_index < len(self.selected_files):
                        file_path = self.selected_files[image_index]
                        
                        # Update status (use proper lambda closure)
                        def update_status(gname=group_name, ltr=letter):
                            self.status_label.config(text=f"Behandler: {gname} {ltr}")
                        self.window.after(0, update_status)
                        
                        try:
                            # Process image
                            result = self.process_group_image(file_path, group_name, letter, 
                                                            small_max_size_kb, use_aab_prefix)
                            if result:
                                self.processed_files.append(result)
                        except Exception as e:
                            print(f"Fejl ved behandling af {file_path}: {e}")
                        
                        processed_count += 1
                        progress = (processed_count / total_images) * 100
                        
                        # Update progress (use proper lambda closure)
                        def update_progress(p=progress):
                            self.progress_var.set(p)
                        self.window.after(0, update_progress)
            
            # Processing complete
            self.window.after(0, lambda: self.processing_complete(len(self.processed_files), total_images))
            
        except Exception as e:
            self.window.after(0, lambda: self.processing_error(str(e)))
    
    def process_group_image(self, file_path: str, group_name: str, letter: str, 
                           small_max_size_kb: int, use_aab_prefix: bool) -> Dict:
        """Process a single image for a group"""
        try:
            # Read image
            with open(file_path, 'rb') as f:
                image_data = f.read()
            
            # Generate filename
            if use_aab_prefix:
                filename = f"AAB {group_name} {letter}.jpg"
            else:
                filename = f"{group_name} {letter}.jpg"
            
            # Create small version (compressed)
            small_image = self.create_thumbnail(image_data, small_max_size_kb)
            
            # Create large version (original quality)
            large_image = self.resize_image(image_data)
            
            return {
                'small': {
                    'filename': filename,
                    'data': small_image
                },
                'large': {
                    'filename': filename,
                    'data': large_image
                },
                'original_path': file_path,
                'group_name': group_name,
                'letter': letter
            }
            
        except Exception as e:
            print(f"Fejl ved behandling af {file_path}: {e}")
            return None
    
    def create_thumbnail(self, image_data: bytes, max_size_kb: int = 300) -> bytes:
        """Create compressed image (same as simple resizer)"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Resize very large images first
            if max(image.size) > 2000:
                ratio = 2000 / max(image.size)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to RGB
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            temp_image = image.copy()
            quality = 85
            
            for attempt in range(8):
                output = io.BytesIO()
                temp_image.save(output, format='JPEG', quality=quality, optimize=True)
                size_kb = len(output.getvalue()) / 1024
                
                if size_kb <= max_size_kb:
                    result = output.getvalue()
                    del output, temp_image, image
                    gc.collect()
                    return result
                else:
                    quality -= 8
                    
                if quality <= 50 and max(temp_image.size) > 800:
                    ratio = 0.8
                    new_size = (int(temp_image.width * ratio), int(temp_image.height * ratio))
                    temp_image = temp_image.resize(new_size, Image.Resampling.LANCZOS)
                    quality = 75
            
            # Final save
            output = io.BytesIO()
            temp_image.save(output, format='JPEG', quality=max(30, quality), optimize=True)
            result = output.getvalue()
            
            del output, temp_image, image
            gc.collect()
            
            return result
            
        except Exception as e:
            print(f"Fejl i create_thumbnail: {e}")
            gc.collect()
            raise
    
    def resize_image(self, image_data: bytes) -> bytes:
        """Convert to high quality JPEG (no resizing)"""
        image = Image.open(io.BytesIO(image_data))
        
        # Return original if already optimal JPEG
        if image.format == 'JPEG' and image.mode == 'RGB':
            return image_data
        
        # Convert to RGB if needed
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save with maximum quality
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=100, optimize=False)
        output.seek(0)
        return output.getvalue()
    
    def processing_complete(self, success_count: int, total_count: int):
        """Called when processing is complete"""
        self.processing = False
        self.start_btn.config(state=tk.NORMAL, text="🚀 Start Behandling")
        
        if success_count > 0:
            self.status_label.config(text=f"Færdig! {success_count}/{total_count} billeder behandlet")
            self.show_results_summary()
            self.download_zip_btn.config(state=tk.NORMAL)
            self.save_sara_btn.config(state=tk.NORMAL)
            self.organize_btn.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="Ingen billeder kunne behandles")
    
    def processing_error(self, error_message: str):
        """Called when processing encounters an error"""
        self.processing = False
        self.start_btn.config(state=tk.NORMAL, text="🚀 Start Behandling")
        self.status_label.config(text=f"Fejl: {error_message}")
        messagebox.showerror("Behandlingsfejl", f"Der opstod en fejl: {error_message}")
    
    def show_results_summary(self):
        """Show processing results summary"""
        # Clear previous results
        for widget in self.results_summary_frame.winfo_children():
            widget.destroy()
        
        # Results text
        total_files = len(self.processed_files)
        groups_count = len(set(f['group_name'] for f in self.processed_files))
        
        summary_text = (f"📊 Resultat: {total_files} billeder behandlet\n"
                       f"👥 Antal grupper: {groups_count}\n" 
                       f"📁 Hver fil gemt i to versioner: lille og stor\n"
                       f"✅ Klar til download")
        
        summary_label = tk.Label(self.results_summary_frame,
                                text=summary_text,
                                font=('Segoe UI', 11),
                                fg=self.colors['text_primary'],
                                bg=self.colors['bg_primary'],
                                justify=tk.LEFT)
        summary_label.pack(anchor=tk.W)
    
    def download_zip(self):
        """Create and download ZIP file with all processed images"""
        if not self.processed_files:
            return
        
        # Bring window to front before showing dialog
        if self.window:
            self.window.lift()
            self.window.attributes('-topmost', True)
            self.window.update()
            self.window.attributes('-topmost', False)
        
        # Select save location
        zip_path = filedialog.asksaveasfilename(
            title="Gem ZIP fil",
            defaultextension=".zip",
            filetypes=[("ZIP filer", "*.zip"), ("Alle filer", "*.*")],
            parent=self.window
        )
        
        if not zip_path:
            return
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # First pass: count duplicates for each filename
                filename_counts = {}
                for file_pair in self.processed_files:
                    base_filename = file_pair['small']['filename']
                    filename_counts[base_filename] = filename_counts.get(base_filename, 0) + 1
                
                # Second pass: assign unique names with suffixes for duplicates
                filename_counters = {}
                for file_pair in self.processed_files:
                    base_filename = file_pair['small']['filename']
                    name, ext = os.path.splitext(base_filename)
                    
                    # If there are multiple files with this name, add suffix
                    if filename_counts[base_filename] > 1:
                        if base_filename not in filename_counters:
                            filename_counters[base_filename] = 0
                        
                        suffix = chr(ord('a') + filename_counters[base_filename])
                        small_filename = f"{name} {suffix}{ext}"
                        large_filename = f"{name} {suffix}{ext}"
                        filename_counters[base_filename] += 1
                    else:
                        # Single file, no suffix needed
                        small_filename = base_filename
                        large_filename = base_filename
                    
                    # Add small version
                    zip_file.writestr(f"small/{small_filename}", file_pair['small']['data'])
                    
                    # Add large version
                    zip_file.writestr(f"large/{large_filename}", file_pair['large']['data'])
            
            messagebox.showinfo("ZIP Oprettet", f"ZIP fil gemt som:\n{zip_path}")
            
        except Exception as e:
            messagebox.showerror("ZIP Fejl", f"Fejl ved oprettelse af ZIP: {str(e)}")
    
    def upload_to_sara(self):
        """Upload compressed images to SARA using batch upload system"""
        if not self.processed_files:
            messagebox.showwarning("Ingen billeder", "Der er ingen behandlede billeder at uploade.")
            return
        
        if not SARA_UPLOAD_AVAILABLE:
            messagebox.showerror("Fejl", "SARA upload er ikke tilgængelig. Kontakt support.")
            return
        
        # Create temporary files from processed images (small versions)
        temp_files = []
        
        try:
            for file_pair in self.processed_files:
                # Use the small/compressed version
                filename = file_pair['small']['filename']
                image_data = file_pair['small']['data']
                
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1])
                temp_file.write(image_data)
                temp_file.close()
                
                temp_files.append(temp_file.name)
            
            # Use the batch upload system with temporary files
            uploader = SaraBatchUploader()
            success = uploader.batch_upload_image_files(temp_files)
            
            if success:
                self.show_success_message("SARA upload færdig! CSV fil er gemt på skrivebordet.")
            
        except Exception as e:
            messagebox.showerror("Fejl", f"SARA upload fejlede: {e}")
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    def show_success_message(self, message):
        """Show success message"""
        messagebox.showinfo("Success", message, parent=self.window)

    
    def organize_to_museum(self):
        """Organiser processede billeder til museum mappestruktur (kun store versioner)"""
        if not self.processed_files:
            return
        
        try:
            # Kun store versioner til museum
            large_files = []
            invalid_files = []
            
            for file_pair in self.processed_files:
                filename = file_pair['large']['filename']
                valid, message = self.museum_organizer.validate_filename(filename)
                
                if valid:
                    large_files.append({
                        'filename': filename,
                        'data': file_pair['large']['data']
                    })
                else:
                    invalid_files.append(f"{filename}: {message}")
            
            # Vis invalid filer hvis nogen
            if invalid_files:
                invalid_msg = "\n".join(invalid_files[:5])
                if len(invalid_files) > 5:
                    invalid_msg += f"\n... og {len(invalid_files) - 5} flere"
                
                messagebox.showwarning("Ugyldige Filnavne", 
                                     f"Følgende filer kan ikke organiseres:\n\n{invalid_msg}\n\n"
                                     f"Kun gyldige filer vil blive organiseret.")
            
            if not large_files:
                messagebox.showerror("Ingen Gyldige Filer", 
                                   "Ingen filer har gyldige sagnumre til organisering.")
                return
            
            # Bekræft organisering
            response = messagebox.askyesno(
                "Bekræft Museum Organisering",
                f"Organisér {len(large_files)} store billeder til museum mappestruktur?\n\n"
                f"Kun de store/ukomprimerete versioner organiseres.\n"
                f"Filerne vil blive kopieret til:\n"
                f"{self.museum_organizer.base_path}\n\n"
                f"Eksisterende mapper med beskrivelser vil blive fundet automatisk."
            )
            
            if not response:
                return
            
            # Organisér filerne - nu med smart scanning
            results = self.museum_organizer.organize_files(large_files, ask_before_create=True)
            
            # Vis resultater
            success_count = len(results['success'])
            error_count = len(results['errors'])
            
            result_msg = f"Museum Organisering Fuldført!\n\n"
            result_msg += f"✅ Store billeder organiseret: {success_count}\n"
            
            if error_count > 0:
                result_msg += f"❌ Fejl: {error_count} filer\n"
            
            if results['created_folders']:
                result_msg += f"\n📁 {len(results['created_folders'])} mapper oprettet\n"
            
            # Vis detaljer hvis fejl
            if results['errors']:
                result_msg += f"\nFejl detaljer:\n"
                for error in results['errors'][:3]:
                    result_msg += f"• {error}\n"
                if len(results['errors']) > 3:
                    result_msg += f"... og {len(results['errors']) - 3} flere fejl"
            
            if success_count > 0:
                messagebox.showinfo("Museum Organisering", result_msg)
            else:
                messagebox.showerror("Museum Organisering Fejl", result_msg)
            
        except Exception as e:
            messagebox.showerror("Organisering Fejl", 
                               f"Uventet fejl ved museum organisering:\n{str(e)}")


# Import for dialog
try:
    import tkinter.simpledialog as simpledialog
    tk.simpledialog = simpledialog
except ImportError:
    pass


def main():
    """Run the group image processor as standalone application"""
    app = GroupImageProcessor()
    app.show()
    
    if app.window and hasattr(app.window, 'mainloop'):
        app.window.mainloop()


if __name__ == "__main__":
    main()
