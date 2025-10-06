"""
Simple Image Resizer - DGB Assistent
Komprimerer billeder til en bestemt KB størrelse
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
import io
import gc
from PIL import Image, ImageTk
import threading
from typing import List, Dict
from .museum_organizer import MuseumOrganizer


class SimpleImageResizer:
    """Simple image compression tool"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.processed_images = []
        self.processing = False
        self.museum_organizer = MuseumOrganizer()
        
    def show(self):
        """Show the simple image resizer window"""
        if self.window is None or not self.window.winfo_exists():
            self.create_window()
        else:
            self.window.lift()
            self.window.focus_force()
    
    def create_window(self):
        """Create the main window"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Simpel Billedkomprimering - DGB Assistent")
        self.window.geometry("800x600")
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
                              text="🖼️ Simpel Billedkomprimering", 
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.colors['text_primary'],
                              bg=self.colors['bg_primary'])
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = tk.Label(main_frame,
                             text="Komprimér dine billeder til en bestemt filstørrelse i KB",
                             font=('Segoe UI', 11),
                             fg=self.colors['text_secondary'],
                             bg=self.colors['bg_primary'])
        desc_label.pack(pady=(0, 20))
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Indstillinger", padding=15)
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Target size setting
        size_frame = ttk.Frame(settings_frame)
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(size_frame, text="Mål filstørrelse (KB):").pack(side=tk.LEFT)
        
        self.target_size_var = tk.IntVar(value=300)
        size_spinbox = ttk.Spinbox(size_frame, 
                                  from_=50, to=2000, 
                                  textvariable=self.target_size_var,
                                  width=10)
        size_spinbox.pack(side=tk.RIGHT)
        
        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="Vælg Billeder", padding=15)
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
        
        # Progress area
        self.progress_frame = ttk.LabelFrame(main_frame, text="Fremskridt", padding=15)
        self.progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, 
                                           variable=self.progress_var,
                                           length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(self.progress_frame, text="Klar til at behandle billeder")
        self.status_label.pack()
        
        # Results area (initially hidden)
        self.results_frame = ttk.LabelFrame(main_frame, text="Resultater", padding=15)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.process_btn = tk.Button(button_frame,
                                    text="🔄 Start Komprimering",
                                    font=('Segoe UI', 11, 'bold'),
                                    bg=self.colors['success'],
                                    fg='white',
                                    relief=tk.FLAT,
                                    padx=20, pady=10,
                                    cursor='hand2',
                                    command=self.start_processing,
                                    state=tk.DISABLED)
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_btn = tk.Button(button_frame,
                                 text="💾 Gem Billeder",
                                 font=('Segoe UI', 11, 'bold'),
                                 bg=self.colors['accent'],
                                 fg='white',
                                 relief=tk.FLAT,
                                 padx=20, pady=10,
                                 cursor='hand2',
                                 command=self.save_images,
                                 state=tk.DISABLED)
        self.save_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        self.organize_btn = tk.Button(button_frame,
                                     text="🗂️ Organiser til Museum",
                                     font=('Segoe UI', 11, 'bold'),
                                     bg=self.colors['success'],
                                     fg='white',
                                     relief=tk.FLAT,
                                     padx=20, pady=10,
                                     cursor='hand2',
                                     command=self.organize_to_museum,
                                     state=tk.DISABLED)
        self.organize_btn.pack(side=tk.RIGHT)
        
    def select_files(self):
        """Select image files to process"""
        file_types = [
            ('Billedfiler', '*.jpg *.jpeg *.png *.bmp *.tiff *.webp'),
            ('JPEG filer', '*.jpg *.jpeg'),
            ('PNG filer', '*.png'),
            ('Alle filer', '*.*')
        ]
        
        files = filedialog.askopenfilenames(
            title="Vælg billeder til komprimering",
            filetypes=file_types
        )
        
        if files:
            self.selected_files = list(files)
            count = len(files)
            self.file_count_label.config(text=f"{count} filer valgt")
            self.process_btn.config(state=tk.NORMAL)
            
            # Warn if too many files
            if count > 20:
                messagebox.showwarning("For mange filer", 
                                     f"Du har valgt {count} filer. For bedste ydeevne anbefales maks 20 filer ad gangen.")
        
    def start_processing(self):
        """Start processing images in a separate thread"""
        if self.processing or not hasattr(self, 'selected_files'):
            return
            
        self.processing = True
        self.process_btn.config(state=tk.DISABLED, text="⏳ Behandler...")
        self.save_btn.config(state=tk.DISABLED)
        self.organize_btn.config(state=tk.DISABLED)
        
        # Reset progress
        self.progress_var.set(0)
        self.processed_images.clear()
        
        # Start processing in background thread
        thread = threading.Thread(target=self.process_images, daemon=True)
        thread.start()
        
    def process_images(self):
        """Process images (runs in background thread)"""
        total_files = len(self.selected_files)
        target_size_kb = self.target_size_var.get()
        
        try:
            for i, file_path in enumerate(self.selected_files):
                # Update status on main thread
                self.window.after(0, lambda i=i, f=file_path: 
                    self.status_label.config(text=f"Behandler: {os.path.basename(f)} ({i+1}/{total_files})"))
                
                try:
                    # Process single image
                    result = self.process_single_image(file_path, target_size_kb)
                    if result:
                        self.processed_images.append(result)
                except Exception as e:
                    print(f"Fejl ved behandling af {file_path}: {e}")
                
                # Update progress
                progress = ((i + 1) / total_files) * 100
                self.window.after(0, lambda p=progress: self.progress_var.set(p))
                
                # Memory cleanup
                if (i + 1) % 5 == 0:
                    gc.collect()
            
            # Processing complete
            success_count = len(self.processed_images)
            self.window.after(0, lambda: self.processing_complete(success_count, total_files))
            
        except Exception as e:
            self.window.after(0, lambda: self.processing_error(str(e)))
    
    def process_single_image(self, file_path: str, target_size_kb: int) -> Dict:
        """Process a single image"""
        try:
            # Read image
            with open(file_path, 'rb') as f:
                image_data = f.read()
            
            # Skip if file too large (>50MB)
            if len(image_data) > 50 * 1024 * 1024:
                return None
                
            # Compress image
            compressed_data = self.create_thumbnail(image_data, target_size_kb)
            
            # Generate output filename
            input_path = Path(file_path)
            output_filename = f"{input_path.stem}_compressed.jpg"
            
            return {
                'original_path': file_path,
                'original_name': input_path.name,
                'output_filename': output_filename,
                'data': compressed_data,
                'original_size_kb': len(image_data) // 1024,
                'compressed_size_kb': len(compressed_data) // 1024
            }
            
        except Exception as e:
            print(f"Fejl ved behandling af {file_path}: {e}")
            return None
    
    def create_thumbnail(self, image_data: bytes, max_size_kb: int = 300) -> bytes:
        """Create compressed image with size limit in KB"""
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
            
            # Compress to target size
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
                    
                # Resize if quality gets too low
                if quality <= 50 and max(temp_image.size) > 800:
                    ratio = 0.8
                    new_size = (int(temp_image.width * ratio), int(temp_image.height * ratio))
                    temp_image = temp_image.resize(new_size, Image.Resampling.LANCZOS)
                    quality = 75
            
            # Final save with low quality
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
    
    def processing_complete(self, success_count: int, total_count: int):
        """Called when processing is complete"""
        self.processing = False
        self.process_btn.config(state=tk.NORMAL, text="🔄 Start Komprimering")
        
        if success_count > 0:
            self.save_btn.config(state=tk.NORMAL)
            self.organize_btn.config(state=tk.NORMAL)
            self.status_label.config(text=f"Færdig! {success_count}/{total_count} billeder behandlet succesfuldt")
            self.show_results()
        else:
            self.status_label.config(text="Ingen billeder kunne behandles")
            
    def processing_error(self, error_message: str):
        """Called when processing encounters an error"""
        self.processing = False
        self.process_btn.config(state=tk.NORMAL, text="🔄 Start Komprimering")
        self.status_label.config(text=f"Fejl: {error_message}")
        messagebox.showerror("Behandlingsfejl", f"Der opstod en fejl: {error_message}")
    
    def show_results(self):
        """Show processing results"""
        # Show results frame
        self.results_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Results summary
        total_original_kb = sum(img['original_size_kb'] for img in self.processed_images)
        total_compressed_kb = sum(img['compressed_size_kb'] for img in self.processed_images)
        compression_ratio = (1 - total_compressed_kb / total_original_kb) * 100 if total_original_kb > 0 else 0
        
        summary_text = (f"📊 Resultat: {len(self.processed_images)} billeder behandlet\n"
                       f"📁 Original størrelse: {total_original_kb:,} KB\n" 
                       f"📁 Komprimeret størrelse: {total_compressed_kb:,} KB\n"
                       f"📉 Besparelse: {compression_ratio:.1f}%")
        
        summary_label = tk.Label(self.results_frame,
                                text=summary_text,
                                font=('Segoe UI', 10),
                                fg=self.colors['text_primary'],
                                bg=self.colors['bg_primary'],
                                justify=tk.LEFT)
        summary_label.pack(anchor=tk.W)
    
    def save_images(self):
        """Save processed images to selected directory"""
        if not self.processed_images:
            return
            
        # Select output directory
        output_dir = filedialog.askdirectory(title="Vælg mappe til gemte billeder")
        if not output_dir:
            return
        
        try:
            saved_count = 0
            for img_data in self.processed_images:
                output_path = os.path.join(output_dir, img_data['output_filename'])
                
                with open(output_path, 'wb') as f:
                    f.write(img_data['data'])
                saved_count += 1
            
            messagebox.showinfo("Gem Fuldført", 
                              f"{saved_count} billeder gemt succesfuldt i:\n{output_dir}")
            
        except Exception as e:
            messagebox.showerror("Gem Fejl", f"Fejl ved gemning af billeder: {str(e)}")
    
    def organize_to_museum(self):
        """Organiser processede billeder til museum mappestruktur"""
        if not self.processed_images:
            return
        
        try:
            # Valider at filerne kan organiseres
            valid_files = []
            invalid_files = []
            
            for img_data in self.processed_images:
                filename = img_data['output_filename']
                valid, message = self.museum_organizer.validate_filename(filename)
                
                if valid:
                    valid_files.append({
                        'filename': filename,
                        'data': img_data['data']
                    })
                else:
                    invalid_files.append(f"{filename}: {message}")
            
            # Vis invalid filer hvis nogen
            if invalid_files:
                invalid_msg = "\n".join(invalid_files[:5])  # Vis max 5
                if len(invalid_files) > 5:
                    invalid_msg += f"\n... og {len(invalid_files) - 5} flere"
                
                messagebox.showwarning("Ugyldige Filnavne", 
                                     f"Følgende filer kan ikke organiseres:\n\n{invalid_msg}\n\n"
                                     f"Kun gyldige filer vil blive organiseret.")
            
            if not valid_files:
                messagebox.showerror("Ingen Gyldige Filer", 
                                   "Ingen filer har gyldige sagnumre til organisering.")
                return
            
            # Bekræft organisering
            response = messagebox.askyesno(
                "Bekræft Museum Organisering",
                f"Organisér {len(valid_files)} gyldige billeder til museum mappestruktur?\n\n"
                f"Filerne vil blive kopieret til:\n"
                f"{self.museum_organizer.base_path}\n\n"
                f"Mapper vil blive oprettet automatisk hvis de ikke findes."
            )
            
            if not response:
                return
            
            # Organisér filerne
            results = self.museum_organizer.organize_files(valid_files, ask_before_create=True)
            
            # Vis resultater
            success_count = len(results['success'])
            error_count = len(results['errors'])
            skipped_count = len(results['skipped'])
            
            result_msg = f"Museum Organisering Fuldført!\n\n"
            result_msg += f"✅ Succes: {success_count} filer organiseret\n"
            
            if error_count > 0:
                result_msg += f"❌ Fejl: {error_count} filer\n"
            
            if skipped_count > 0:
                result_msg += f"⏭️ Sprunget over: {skipped_count} filer\n"
            
            if results['created_folders']:
                result_msg += f"\n📁 {len(results['created_folders'])} mapper oprettet\n"
            
            # Vis detaljer hvis fejl
            if results['errors']:
                result_msg += f"\nFejl detaljer:\n"
                for error in results['errors'][:3]:  # Vis max 3 fejl
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
    """Run the simple image resizer as standalone application"""
    app = SimpleImageResizer()
    app.show()
    
    if app.window and hasattr(app.window, 'mainloop'):
        app.window.mainloop()


if __name__ == "__main__":
    main()