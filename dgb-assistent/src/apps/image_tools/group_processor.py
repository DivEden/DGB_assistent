"""
Group Image Processor - DGB Assistent
Grupperer billeder og navngiver dem systematisk (a, b, c, osv.)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
import io
import gc
import json
import zipfile
from PIL import Image, ImageTk
import threading
from typing import List, Dict, Optional
from .museum_organizer import MuseumOrganizer


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
        
        # Image preview and grouping
        self.grouping_frame = ttk.LabelFrame(self.setup_tab, text="Gruppér Billeder", padding=15)
        self.grouping_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for image thumbnails and drag-drop
        canvas_frame = ttk.Frame(self.grouping_frame)
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
        
        # Group management buttons
        group_btn_frame = ttk.Frame(self.grouping_frame)
        group_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
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
        self.use_aab_var = tk.BooleanVar(value=True)
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
        
        self.save_individual_btn = tk.Button(download_frame,
                                            text="💾 Gem Individuelt",
                                            font=('Segoe UI', 11, 'bold'),
                                            bg=self.colors['success'],
                                            fg='white',
                                            relief=tk.FLAT,
                                            padx=20, pady=10,
                                            cursor='hand2',
                                            command=self.save_individual,
                                            state=tk.DISABLED)
        self.save_individual_btn.pack(side=tk.LEFT, padx=(0, 10))
        
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
        
        files = filedialog.askopenfilenames(
            title="Vælg billeder til gruppering",
            filetypes=file_types
        )
        
        if files:
            self.selected_files = list(files)
            count = len(files)
            self.file_count_label.config(text=f"{count} filer valgt")
            self.load_image_thumbnails()
            
            # Warn if too many files
            if count > 50:
                messagebox.showwarning("For mange filer", 
                                     f"Du har valgt {count} filer. For bedste ydeevne anbefales maks 50 filer ad gangen.")
    
    def load_image_thumbnails(self):
        """Load thumbnails for selected images"""
        # Clear canvas
        self.setup_canvas.delete("all")
        
        # Create thumbnails in a grid
        x, y = 10, 10
        col_width = 120
        row_height = 150
        cols_per_row = 6
        
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
                
                # Create image on canvas
                image_id = self.setup_canvas.create_image(x_pos + 50, y_pos + 50, image=photo)
                text_id = self.setup_canvas.create_text(x_pos + 50, y_pos + 120, 
                                                       text=f"{i}: {os.path.basename(file_path)[:15]}...",
                                                       width=100, font=('Segoe UI', 8))
                
                # Keep reference to prevent garbage collection
                self.setup_canvas.image_refs = getattr(self.setup_canvas, 'image_refs', [])
                self.setup_canvas.image_refs.append(photo)
                
                # Bind click events for grouping
                self.setup_canvas.tag_bind(image_id, "<Button-1>", 
                                          lambda e, idx=i: self.on_image_click(idx))
                
            except Exception as e:
                print(f"Fejl ved indlæsning af thumbnail for {file_path}: {e}")
        
        # Update scroll region
        self.setup_canvas.configure(scrollregion=self.setup_canvas.bbox("all"))
    
    def on_image_click(self, image_index: int):
        """Handle image click for grouping"""
        # Simple implementation - for now just show which image was clicked
        filename = os.path.basename(self.selected_files[image_index])
        messagebox.showinfo("Billede valgt", f"Du klikkede på billede #{image_index}: {filename}")
    
    def add_new_group(self):
        """Add a new group"""
        group_name = tk.simpledialog.askstring("Ny Gruppe", "Indtast gruppenavn:")
        if group_name:
            new_group = {
                'name': group_name.strip(),
                'images': []
            }
            self.image_groups.append(new_group)
            self.update_groups_display()
            self.check_ready_for_processing()
    
    def clear_groups(self):
        """Clear all groups"""
        if messagebox.askyesno("Bekræft", "Er du sikker på at du vil rydde alle grupper?"):
            self.image_groups.clear()
            self.update_groups_display()
            self.check_ready_for_processing()
    
    def update_groups_display(self):
        """Update the display of groups"""
        # This would update a groups display area
        # For now, just update the processing button state
        self.check_ready_for_processing()
    
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
            
            for group in self.image_groups:
                group_name = group['name'].strip()
                image_indices = group['images']
                
                # Generate letter suffixes (a, b, c, ...)
                letters = [chr(97 + i) for i in range(len(image_indices))]
                
                for i, (image_index, letter) in enumerate(zip(image_indices, letters)):
                    if image_index < len(self.selected_files):
                        file_path = self.selected_files[image_index]
                        
                        # Update status
                        self.window.after(0, lambda: self.status_label.config(
                            text=f"Behandler: {group_name} {letter}"))
                        
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
                        self.window.after(0, lambda p=progress: self.progress_var.set(p))
            
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
            self.save_individual_btn.config(state=tk.NORMAL)
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
        
        # Select save location
        zip_path = filedialog.asksaveasfilename(
            title="Gem ZIP fil",
            defaultextension=".zip",
            filetypes=[("ZIP filer", "*.zip"), ("Alle filer", "*.*")]
        )
        
        if not zip_path:
            return
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_pair in self.processed_files:
                    filename = file_pair['small']['filename']
                    
                    # Add small version
                    zip_file.writestr(f"small/{filename}", file_pair['small']['data'])
                    
                    # Add large version
                    zip_file.writestr(f"large/{filename}", file_pair['large']['data'])
            
            messagebox.showinfo("ZIP Oprettet", f"ZIP fil gemt som:\n{zip_path}")
            
        except Exception as e:
            messagebox.showerror("ZIP Fejl", f"Fejl ved oprettelse af ZIP: {str(e)}")
    
    def save_individual(self):
        """Save processed images to selected directory"""
        if not self.processed_files:
            return
        
        # Select output directory
        output_dir = filedialog.askdirectory(title="Vælg mappe til gemte billeder")
        if not output_dir:
            return
        
        try:
            # Create subdirectories
            small_dir = os.path.join(output_dir, "small")
            large_dir = os.path.join(output_dir, "large")
            os.makedirs(small_dir, exist_ok=True)
            os.makedirs(large_dir, exist_ok=True)
            
            saved_count = 0
            for file_pair in self.processed_files:
                filename = file_pair['small']['filename']
                
                # Save small version
                small_path = os.path.join(small_dir, filename)
                with open(small_path, 'wb') as f:
                    f.write(file_pair['small']['data'])
                
                # Save large version
                large_path = os.path.join(large_dir, filename)
                with open(large_path, 'wb') as f:
                    f.write(file_pair['large']['data'])
                
                saved_count += 1
            
            messagebox.showinfo("Gem Fuldført", 
                              f"{saved_count * 2} filer gemt succesfuldt i:\n{output_dir}")
            
        except Exception as e:
            messagebox.showerror("Gem Fejl", f"Fejl ved gemning af billeder: {str(e)}")
    
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
                f"Mapper vil blive oprettet automatisk hvis de ikke findes."
            )
            
            if not response:
                return
            
            # Organisér filerne
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