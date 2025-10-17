"""
Individual Image Processor - DGB Assistent
Individuel navngivning og behandling af billeder
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
    from utils.sara_uploader import SaraUploader
    SARA_UPLOAD_AVAILABLE = True
except ImportError:
    try:
        from ...utils.sara_uploader import SaraUploader
        SARA_UPLOAD_AVAILABLE = True
    except ImportError:
        # Fallback for PyInstaller or direct execution
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
        try:
            from sara_uploader import SaraUploader
            SARA_UPLOAD_AVAILABLE = True
        except ImportError:
            # SARA upload not available
            SARA_UPLOAD_AVAILABLE = False


class IndividualImageProcessor:
    """Individual image naming and processing tool"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.selected_files = []
        self.image_names = []  # List of user-defined names for each image
        self.processed_files = []
        self.processing = False
        self.museum_organizer = MuseumOrganizer()
        
    def show(self):
        """Show the individual image processor window"""
        if self.window is None or not self.window.winfo_exists():
            self.create_window()
        else:
            self.window.lift()
            self.window.focus_force()
    
    def create_window(self):
        """Create the main window"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Individuel Billedbehandler - DGB Assistent")
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
                              text="🏷️ Individuel Billedbehandler", 
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.colors['text_primary'],
                              bg=self.colors['bg_primary'])
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = tk.Label(main_frame,
                             text="Navngiv hvert billede individuelt og behandl dem",
                             font=('Segoe UI', 11),
                             fg=self.colors['text_secondary'],
                             bg=self.colors['bg_primary'])
        desc_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Tab 1: File selection and naming
        self.setup_tab = ttk.Frame(notebook)
        notebook.add(self.setup_tab, text="1. Navngivning")
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
        
        # Image naming area
        self.naming_frame = ttk.LabelFrame(self.setup_tab, text="Navngiv Billeder", padding=15)
        self.naming_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions = tk.Label(self.naming_frame,
                               text="Indtast et navn for hvert billede. Ens navne får automatisk suffiks (a, b, c).\nFor SARA upload: brug format som 0054x0007, 00073;15 eller AAB 1234",
                               font=('Segoe UI', 10),
                               fg=self.colors['text_secondary'],
                               bg=self.colors['bg_primary'],
                               justify=tk.LEFT)
        instructions.pack(anchor=tk.W, pady=(0, 10))
        
        # Scrollable frame for image naming
        canvas_frame = ttk.Frame(self.naming_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.naming_canvas = tk.Canvas(canvas_frame, bg='white')
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.naming_canvas.yview)
        
        self.naming_scrollable_frame = tk.Frame(self.naming_canvas, bg='white')
        
        self.naming_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.naming_canvas.configure(scrollregion=self.naming_canvas.bbox("all"))
        )
        
        self.naming_canvas.create_window((0, 0), window=self.naming_scrollable_frame, anchor="nw")
        self.naming_canvas.configure(yscrollcommand=v_scrollbar.set)
        
        self.naming_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Bind mousewheel to canvas and frame
        self.naming_canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.naming_scrollable_frame.bind("<MouseWheel>", self.on_mousewheel)
        
        # Also bind to the canvas frame to ensure scrolling works
        canvas_frame.bind("<MouseWheel>", self.on_mousewheel)
        
        # Bind focus events to ensure mousewheel works when hovering
        def bind_mousewheel_recursive(widget):
            widget.bind("<Enter>", lambda e: widget.focus_set())
            widget.bind("<MouseWheel>", self.on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Apply recursive binding
        bind_mousewheel_recursive(canvas_frame)
        
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
        
        # Validation area
        validation_frame = ttk.Frame(process_frame)
        validation_frame.pack(fill=tk.X, pady=(0, 20))
        
        validate_btn = tk.Button(validation_frame,
                                text="✅ Valider Navne",
                                font=('Segoe UI', 10),
                                bg=self.colors['warning'],
                                fg='white',
                                relief=tk.FLAT,
                                padx=15, pady=8,
                                cursor='hand2',
                                command=self.validate_names)
        validate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.validation_label = ttk.Label(validation_frame, text="")
        self.validation_label.pack(side=tk.LEFT)
        
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
            title="Vælg billeder til individuel behandling",
            filetypes=file_types,
            parent=self.window
        )
        
        if files:
            self.selected_files = list(files)
            count = len(files)
            self.file_count_label.config(text=f"{count} filer valgt")
            self.create_naming_interface()
            
            # Warn if too many files
            if count > 30:
                messagebox.showwarning("For mange filer", 
                                     f"Du har valgt {count} filer. For bedste brugeroplevelse anbefales maks 30 filer ad gangen.",
                                     parent=self.window)
    
    def create_naming_interface(self):
        """Create the naming interface for each selected image"""
        # Clear previous content
        for widget in self.naming_scrollable_frame.winfo_children():
            widget.destroy()
        
        self.image_names.clear()
        self.name_entries = []  # Keep track of entry widgets
        
        # Create naming row for each image
        for i, file_path in enumerate(self.selected_files):
            self.create_image_naming_row(i, file_path)
        
        # Update scroll region
        self.naming_scrollable_frame.update_idletasks()
        self.naming_canvas.configure(scrollregion=self.naming_canvas.bbox("all"))
    
    def create_image_naming_row(self, index: int, file_path: str):
        """Create a naming row for a single image"""
        row_frame = tk.Frame(self.naming_scrollable_frame, bg='white', relief=tk.SOLID, bd=1)
        row_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Image thumbnail
        try:
            img = Image.open(file_path)
            img.thumbnail((80, 80), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            img_label = tk.Label(row_frame, image=photo, bg='white')
            img_label.image = photo  # Keep reference
            img_label.pack(side=tk.LEFT, padx=10, pady=10)
        except Exception as e:
            # Fallback if thumbnail fails
            img_label = tk.Label(row_frame, text="🖼️", font=('Segoe UI', 24), bg='white')
            img_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # File info and naming
        info_frame = tk.Frame(row_frame, bg='white')
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # File name
        filename_label = tk.Label(info_frame, 
                                 text=f"Fil {index + 1}: {os.path.basename(file_path)}", 
                                 font=('Segoe UI', 10, 'bold'),
                                 bg='white',
                                 fg=self.colors['text_primary'])
        filename_label.pack(anchor=tk.W)
        
        # Name entry
        name_frame = tk.Frame(info_frame, bg='white')
        name_frame.pack(fill=tk.X, pady=(5, 0))
        
        name_label = tk.Label(name_frame, text="Navn:", font=('Segoe UI', 9), bg='white')
        name_label.pack(side=tk.LEFT)
        
        name_var = tk.StringVar()
        name_entry = tk.Entry(name_frame, 
                             textvariable=name_var,
                             font=('Segoe UI', 10),
                             width=30)
        name_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Help button for object number format
        help_btn = tk.Button(name_frame,
                            text="?",
                            font=('Segoe UI', 8),
                            bg='#e2e8f0',
                            fg='#475569',
                            relief=tk.FLAT,
                            width=2,
                            cursor='hand2',
                            command=self.show_object_number_help)
        help_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Store reference
        self.image_names.append(name_var)
        self.name_entries.append(name_entry)
        
        # Add validation on change
        name_var.trace_add('write', lambda *args, idx=index: self.on_name_change(idx))
        
        # Bind mousewheel to all new widgets in this row
        for widget in [row_frame, img_label, info_frame, filename_label, name_frame, name_label, name_entry]:
            widget.bind("<MouseWheel>", self.on_mousewheel)
    
    def on_name_change(self, index: int):
        """Called when a name entry changes"""
        # Clear previous validation
        self.validation_label.config(text="", foreground='black')
        self.start_btn.config(state=tk.DISABLED)
    
    def show_object_number_help(self):
        """Show help dialog about object number format"""
        help_text = """OBJEKTNUMMER FORMAT TIL SARA:

Understøttede formater:
• 0054x0007 (traditionelt format)
• 1234X0123 (X kan være stort)
• 00073;15 (genstands-nummer med år)
• 12345;2015 (fuldt årstal)
• AAB 1234 (med AAB præfiks)
• 1234 (bare nummeret)

Eksempler på ugyldige formater:
• Mit billede (mangler objektnummer)
• 0054-0007 (skal bruge x eller ;)

For almindelig navngivning uden SARA upload 
kan du bruge et hvilket som helst navn."""
        
        messagebox.showinfo("Objektnummer Hjælp", help_text)
    
    def validate_object_number(self, name: str) -> bool:
        """Check if name contains valid object number format"""
        import re
        # Support multiple formats:
        # 1. Traditional: 1234x4321 or 1234X4321
        # 2. Genstands format: 00073;15 or 12345;2015
        # 3. AAB format: AAB 1234 or just 1234
        patterns = [
            r'\d{4}[xX]\d{3,4}',      # 1234x4321
            r'\d+;\d{2,4}',           # 00073;15 
            r'(?:AAB\s+)?\d{4}'       # AAB 1234 or 1234
        ]
        
        for pattern in patterns:
            if re.search(pattern, name):
                return True
        return False
    
    def validate_names(self):
        """Validate all image names"""
        if not self.image_names:
            self.validation_label.config(text="Ingen billeder at validere", foreground='red')
            return False
        
        names = [name_var.get().strip() for name_var in self.image_names]
        
        # Check for empty names
        empty_indices = [i for i, name in enumerate(names) if not name]
        if empty_indices:
            self.validation_label.config(
                text=f"Tomme navne fundet på billede(r): {', '.join(map(str, [i+1 for i in empty_indices]))}",
                foreground='red'
            )
            return False
        
        # Check for valid object numbers (for SARA upload)
        names_with_obj_nums = [name for name in names if self.validate_object_number(name)]
        names_without_obj_nums = len(names) - len(names_with_obj_nums)
        
        # Check for duplicate names (systemet håndterer automatisk med suffiks)
        duplicates = []
        seen_names = {}
        for i, name in enumerate(names):
            if name.lower() in seen_names:
                duplicates.append(f"{name} (billede {i+1} og {seen_names[name.lower()]+1})")
            else:
                seen_names[name.lower()] = i
        
        # Validation message
        messages = []
        
        if duplicates:
            duplicate_count = len(duplicates)
            messages.append(f"ℹ️ {duplicate_count} ens navne får automatisk suffiks (a, b, c)")
        else:
            messages.append("✅ Alle navne er forskellige")
        
        if names_without_obj_nums > 0:
            messages.append(f"⚠️ {names_without_obj_nums} navne mangler objektnummer (for SARA)")
        elif len(names_with_obj_nums) > 0:
            messages.append(f"✅ {len(names_with_obj_nums)} navne har objektnumre")
        
        # Show combined message
        combined_message = " | ".join(messages)
        if names_without_obj_nums > 0:
            self.validation_label.config(text=combined_message, foreground='orange')
        else:
            self.validation_label.config(text=combined_message, foreground='green')
        
        # All validation passed - ens navne er tilladt og håndteres automatisk
        self.start_btn.config(state=tk.NORMAL)
        return True
    
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.naming_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def start_processing(self):
        """Start processing images individually"""
        if self.processing or not self.validate_names():
            return
            
        self.processing = True
        self.start_btn.config(state=tk.DISABLED, text="⏳ Behandler...")
        
        # Reset progress
        self.progress_var.set(0)
        self.processed_files.clear()
        
        # Start processing in background thread
        thread = threading.Thread(target=self.process_individual_images, daemon=True)
        thread.start()
    
    def process_individual_images(self):
        """Process images individually (runs in background thread)"""
        try:
            small_max_size_kb = self.small_size_var.get()
            use_aab_prefix = self.use_aab_var.get()
            
            names = [name_var.get().strip() for name_var in self.image_names]
            total_images = len(self.selected_files)
            
            for i, (file_path, name) in enumerate(zip(self.selected_files, names)):
                # Update status
                self.window.after(0, lambda n=name: self.status_label.config(
                    text=f"Behandler: {n}"))
                
                try:
                    # Process image
                    result = self.process_individual_image(file_path, name, 
                                                         small_max_size_kb, use_aab_prefix)
                    if result:
                        self.processed_files.append(result)
                except Exception as e:
                    print(f"Fejl ved behandling af {file_path}: {e}")
                
                # Update progress
                progress = ((i + 1) / total_images) * 100
                self.window.after(0, lambda p=progress: self.progress_var.set(p))
                
                # Memory cleanup
                if (i + 1) % 5 == 0:
                    gc.collect()
            
            # Processing complete
            self.window.after(0, lambda: self.processing_complete(len(self.processed_files), total_images))
            
        except Exception as e:
            self.window.after(0, lambda: self.processing_error(str(e)))
    
    def process_individual_image(self, file_path: str, name: str, 
                               small_max_size_kb: int, use_aab_prefix: bool) -> Dict:
        """Process a single image with individual name"""
        try:
            # Read image
            with open(file_path, 'rb') as f:
                image_data = f.read()
            
            # Generate filename
            if use_aab_prefix:
                filename = f"AAB {name}.jpg"
            else:
                filename = f"{name}.jpg"
            
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
                'name': name
            }
            
        except Exception as e:
            print(f"Fejl ved behandling af {file_path}: {e}")
            return None
    
    def create_thumbnail(self, image_data: bytes, max_size_kb: int = 300) -> bytes:
        """Create compressed image (same as other processors)"""
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
        
        summary_text = (f"📊 Resultat: {total_files} billeder behandlet\n"
                       f"🏷️ Alle billeder individuelt navngivet\n" 
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
        
        # Prepare compressed images with filenames for upload
        images_to_upload = []
        
        for file_pair in self.processed_files:
            # Use the small/compressed version
            images_to_upload.append({
                'filename': file_pair['small']['filename'],
                'data': file_pair['small']['data']
            })
        
        try:
            # Use the new SARA uploader with compressed image data
            uploader = SaraUploader()
            success = uploader.batch_upload_images(images_to_upload, parent_window=self.window)
            
            # Success message is shown by uploader
            
        except Exception as e:
            messagebox.showerror("Fejl", f"SARA upload fejlede: {e}")
        



    

    
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


def main():
    """Run the individual image processor as standalone application"""
    app = IndividualImageProcessor()
    app.show()
    
    if app.window and hasattr(app.window, 'mainloop'):
        app.window.mainloop()


if __name__ == "__main__":
    main()