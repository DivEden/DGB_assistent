"""
SARA Batch Upload System

Implements batch upload functionality:
1. Upload images to SARA media server
2. Generate CSV for import via SARA web interface
"""

import os
import json
import base64
import csv
import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path


class SaraBatchUploader:
    """SARA batch upload system for bulk image uploads"""
    
    def __init__(self):
        self.api_base_url = "https://sara-api.adlibhosting.com/SARA-011-DGB/wwwopac.ashx"
        self.database = "collection"
        
        # License options in Danish
        self.license_options = [
            "Public Domain - PD",
            "Creative Commons - CC BY-ND",
            "Creative Commons - CC BY-NC", 
            "Creative Commons - CC BY-SA",
            "Creative Commons - CC BY",
            "No Known Copyrights - NKC"
        ]
        
        # Setup credentials storage
        self.credentials_file = self._get_credentials_path()
    
    def _get_credentials_path(self) -> str:
        """Get secure path for storing SARA credentials"""
        try:
            # Use Windows AppData for secure storage
            appdata = os.path.expandvars('%APPDATA%')
            sara_dir = os.path.join(appdata, 'DGB-Assistant', 'sara')
            
            # Create directory if it doesn't exist
            os.makedirs(sara_dir, exist_ok=True)
            
            return os.path.join(sara_dir, 'credentials.json')
        except Exception as e:
            print(f"Could not setup credentials path: {e}")
            # Fallback to local directory
            return "sara_credentials.json"
    
    def save_credentials(self, username: str, password: str) -> bool:
        """Save SARA credentials securely"""
        try:
            # Encode credentials for basic security
            data = {
                'username': base64.b64encode(username.encode()).decode(),
                'password': base64.b64encode(password.encode()).decode()
            }
            
            with open(self.credentials_file, 'w') as f:
                json.dump(data, f)
            
            print("SARA credentials saved securely")
            return True
            
        except Exception as e:
            print(f"Could not save credentials: {e}")
            return False
    
    def load_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """Load stored SARA credentials"""
        try:
            if not os.path.exists(self.credentials_file):
                return None, None
                
            with open(self.credentials_file, 'r') as f:
                data = json.load(f)
                
            username = base64.b64decode(data['username']).decode()
            password = base64.b64decode(data['password']).decode()
            
            print("SARA credentials loaded from storage")
            return username, password
            
        except Exception as e:
            print(f"Could not load credentials: {e}")
            return None, None
    
    def test_credentials(self, username: str, password: str) -> bool:
        """Test if SARA credentials work"""
        try:
            params = {
                "database": self.database,
                "search": "priref=1",  # Simple test search
                "limit": "1",
                "output": "JSON"
            }
            
            response = requests.get(
                self.api_base_url, 
                params=params, 
                auth=(username, password), 
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Credential test failed: {e}")
            return False


    def upload_image_to_sara(self, image_path: str, object_number: str) -> Optional[str]:
        """Upload single image to SARA media server"""
        try:
            username, password = self.load_credentials()
            if not username or not password:
                return None
            
            # Read image file
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Generate filename for SARA
            filename = f"{object_number}_{Path(image_path).name}"
            
            # Upload using writecontent API
            params = {
                "command": "writecontent",
                "server": "sarafiles",  # May need adjustment
                "value": filename
            }
            
            response = requests.post(
                self.api_base_url,
                params=params,
                files={'file': (filename, image_data, 'image/jpeg')},
                auth=(username, password),
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Uploaded: {filename}")
                return filename  # Return server filename
            else:
                print(f"❌ Upload failed for {filename}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Upload error for {image_path}: {e}")
            return None
    
    def scan_images_for_upload(self, directory: str) -> List[Dict[str, Any]]:
        """Scan directory for images with object numbers"""
        images = []
        
        for file_path in Path(directory).glob("*"):
            if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.tiff', '.tif']:
                # Extract object number from filename
                filename = file_path.stem
                
                # Look for pattern like 0054x0007 or 0054X0007
                import re
                pattern = r'(\d{4}[xX]\d{3,4})'
                match = re.search(pattern, filename)
                
                if match:
                    object_number = match.group(1).upper()
                    images.append({
                        'file_path': str(file_path),
                        'filename': file_path.name,
                        'object_number': object_number,
                        'original_name': file_path.name
                    })
        
        return images
    
    def show_batch_upload_dialog(self, images: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Show Danish dialog for batch upload settings"""
        if not images:
            messagebox.showinfo("Ingen billeder", "Ingen billeder med objektnumre fundet.")
            return None
        
        # Create dialog window
        dialog = tk.Toplevel()
        dialog.title("SARA Batch Upload")
        dialog.geometry("500x400")
        dialog.transient()
        dialog.grab_set()
        
        # Configure grid
        dialog.grid_rowconfigure(2, weight=1)
        dialog.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = ttk.Frame(dialog, padding="10")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(
            header_frame, 
            text=f"Fundet {len(images)} billeder klar til SARA upload",
            font=("Segoe UI", 12, "bold")
        ).pack()
        
        # Settings frame
        settings_frame = ttk.LabelFrame(dialog, text="Indstillinger", padding="10")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # License dropdown
        ttk.Label(settings_frame, text="Licenstype:").grid(row=0, column=0, sticky=tk.W, pady=2)
        license_var = tk.StringVar(value="Public Domain - PD")
        license_combo = ttk.Combobox(
            settings_frame, 
            textvariable=license_var,
            values=self.license_options,
            state="readonly",
            width=30
        )
        license_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Public visibility checkbox
        visibility_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            settings_frame,
            text="Vis offentligt (anbefalet)",
            variable=visibility_var
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Image list
        list_frame = ttk.LabelFrame(dialog, text="Billeder til upload", padding="10")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview for images
        columns = ("Objektnummer", "Filnavn")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)
        
        # Add images to tree
        for img in images:
            tree.insert("", tk.END, values=(img['object_number'], img['filename']))
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Buttons
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        result = {"cancelled": True}
        
        def on_upload():
            result.update({
                "cancelled": False,
                "license": license_var.get(),
                "public": visibility_var.get(),
                "images": images
            })
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="Upload til SARA", command=on_upload).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Annuller", command=on_cancel).pack(side=tk.RIGHT, padx=5)
        
        # Wait for dialog
        dialog.wait_window()
        
        return None if result["cancelled"] else result
    
    def generate_sara_csv(self, upload_results: List[Dict[str, Any]], license: str, public: bool) -> str:
        """Generate CSV file in SARA format"""
        try:
            # Create CSV content
            csv_data = []
            
            # Group by object number (like in your example)
            objects = {}
            for result in upload_results:
                obj_num = result['object_number']
                if obj_num not in objects:
                    objects[obj_num] = {
                        'references': [],
                        'original_names': [],
                        'visibility': [],
                        'licenses': []
                    }
                
                objects[obj_num]['references'].append(result['sara_filename'])
                objects[obj_num]['original_names'].append(result['original_name'])
                objects[obj_num]['visibility'].append('x' if public else '')
                objects[obj_num]['licenses'].append(license)
            
            # Create CSV rows
            for obj_num, data in objects.items():
                csv_data.append({
                    'objektnummer': obj_num,
                    'mediefil.reference': '\n'.join(data['references']),
                    'mediefil.originalt_filnavn': '\n'.join(data['original_names']),
                    'mediefil.vis_offentligt': '\n'.join(data['visibility']),
                    'mediefil.licenstype': '\n'.join(data['licenses'])
                })
            
            # Save CSV file
            desktop = Path.home() / "Desktop"
            csv_file = desktop / f"sara_import_{len(objects)}_objekter.csv"
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                if csv_data:
                    writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                    writer.writeheader()
                    writer.writerows(csv_data)
            
            return str(csv_file)
            
        except Exception as e:
            print(f"CSV generation error: {e}")
            return None
    
    def batch_upload_image_files(self, file_paths: List[str]) -> bool:
        """Upload specific image files to SARA (for processed images)"""
        try:
            # Convert file paths to image objects
            images = []
            for file_path in file_paths:
                filename = Path(file_path).name
                stem = Path(file_path).stem
                
                # Extract object number from filename
                import re
                match = re.search(r'(\d{4}x\d{4})', stem, re.IGNORECASE)
                if match:
                    object_number = match.group(1).lower()
                    images.append({
                        'file_path': file_path,
                        'filename': filename,
                        'original_name': filename,
                        'object_number': object_number
                    })
                else:
                    print(f"No object number found in {filename}")
            
            if not images:
                messagebox.showinfo(
                    "Ingen billeder", 
                    "Ingen billeder med objektnumre fundet.\n\n"
                    "Billeder skal have objektnummer i filnavnet (fx: 0054x0007.jpg)"
                )
                return False
            
            return self._perform_batch_upload(images)
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Batch upload fejlede: {e}")
            return False

    def batch_upload_images(self, directory: str) -> bool:
        """Main function for batch uploading images to SARA"""
        try:
            # Scan for images
            images = self.scan_images_for_upload(directory)
            
            if not images:
                messagebox.showinfo(
                    "Ingen billeder", 
                    "Ingen billeder med objektnumre fundet i mappen.\n\n"
                    "Billeder skal have objektnummer i filnavnet (fx: 0054x0007.jpg)"
                )
                return False
            
            return self._perform_batch_upload(images)
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Batch upload fejlede: {e}")
            return False
    
    def _perform_batch_upload(self, images: List[Dict]) -> bool:
        """Perform the actual batch upload with progress tracking"""
        try:
            # Show settings dialog
            settings = self.show_batch_upload_dialog(images)
            if not settings:
                return False
            
            # Upload images with progress
            upload_results = []
            total = len(images)
            
            # Create progress window
            progress_window = tk.Toplevel()
            progress_window.title("Uploader til SARA...")
            progress_window.geometry("400x150")
            progress_window.transient()
            progress_window.grab_set()
            
            progress_frame = ttk.Frame(progress_window, padding="20")
            progress_frame.pack(fill=tk.BOTH, expand=True)
            
            status_label = ttk.Label(progress_frame, text="Starter upload...")
            status_label.pack(pady=5)
            
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(
                progress_frame,
                variable=progress_var,
                maximum=total,
                length=350
            )
            progress_bar.pack(pady=10)
            
            result_label = ttk.Label(progress_frame, text="")
            result_label.pack(pady=5)
            
            # Update progress function
            def update_progress(current, filename, success_count, fail_count):
                progress_var.set(current)
                status_label.config(text=f"Uploader: {filename}")
                result_label.config(text=f"✅ Uploaded: {success_count} | ❌ Fejlede: {fail_count}")
                progress_window.update()
            
            success_count = 0
            fail_count = 0
            
            # Upload each image
            for i, img in enumerate(images):
                update_progress(i, img['filename'], success_count, fail_count)
                
                sara_filename = self.upload_image_to_sara(img['file_path'], img['object_number'])
                
                if sara_filename:
                    upload_results.append({
                        'object_number': img['object_number'],
                        'sara_filename': sara_filename,
                        'original_name': img['original_name'],
                        'success': True
                    })
                    success_count += 1
                else:
                    fail_count += 1
            
            # Final progress update
            update_progress(total, "Færdig!", success_count, fail_count)
            
            progress_window.destroy()
            
            # Generate CSV if any uploads succeeded
            if upload_results:
                csv_file = self.generate_sara_csv(
                    upload_results, 
                    settings['license'], 
                    settings['public']
                )
                
                if csv_file:
                    messagebox.showinfo(
                        "Upload Færdig!",
                        f"✅ {success_count} billeder uploaded til SARA\n"
                        f"❌ {fail_count} fejlede\n\n"
                        f"CSV fil gemt på skrivebordet:\n{Path(csv_file).name}\n\n"
                        f"Importer denne fil via SARA's 'Import Data' funktion."
                    )
                    return True
            
            messagebox.showerror(
                "Upload Fejlede",
                "Ingen billeder blev uploaded succesfuldt.\n"
                "Tjek din internetforbindelse og SARA credentials."
            )
            return False
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Batch upload fejlede: {e}")
            return False


# Convenience function for easy integration
def show_sara_batch_upload(directory: str = None):
    """Show SARA batch upload dialog for a directory"""
    if not directory:
        directory = filedialog.askdirectory(
            title="Vælg mappe med billeder til SARA upload"
        )
        if not directory:
            return
    
    uploader = SaraBatchUploader()
    return uploader.batch_upload_images(directory)


# Maintain compatibility with existing code
SaraSmartUploader = SaraBatchUploader