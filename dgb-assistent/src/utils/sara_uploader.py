"""
SARA Batch Upload System - DGB Assistent
Uploads compressed images to SARA API and generates XML for import
"""

import requests
import os
import uuid
import re
from datetime import datetime
from requests.auth import HTTPBasicAuth
import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
import json

# SARA API Configuration
BASE_URL = "https://sara-api.adlibhosting.com/SARA-011-DGB/wwwopac.ashx"
USERNAME = r"adlibhosting\DGB-API-USER"
PASSWORD = "YxUyuzNLubfNKbx2"

# License type options for SARA
LICENSE_TYPES = [
    "Public Domain - PD",
    "Creative Commons - CC BY-NC-ND",
    "Creative Commons - CC BY-NC-SA",
    "Creative Commons - CC BY-ND",
    "Creative Commons - CC BY-NC",
    "Creative Commons - CC BY-SA",
    "Creative Commons - CC BY",
    "No Known Copyright - NKC",
    "Copyright - C"
]


class SaraUploadConfigDialog:
    """Dialog for configuring SARA upload options"""
    
    def __init__(self, parent=None):
        self.result = None
        self.dialog = tk.Toplevel(parent) if parent else tk.Tk()
        self.dialog.title("SARA Upload Indstillinger")
        self.dialog.geometry("500x300")
        self.dialog.configure(bg='#f8fafc')
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"500x300+{x}+{y}")
        
        self.create_interface()
        
    def create_interface(self):
        """Create the dialog interface"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame,
                              text="📋 SARA Upload Indstillinger",
                              font=('Segoe UI', 14, 'bold'),
                              bg='#f8fafc',
                              fg='#0f172a')
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_label = tk.Label(main_frame,
                             text="Vælg standardindstillinger for alle billeder i upload",
                             font=('Segoe UI', 10),
                             bg='#f8fafc',
                             fg='#475569')
        desc_label.pack(pady=(0, 20))
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Indstillinger", padding=15)
        options_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Vis offentligt option
        vis_frame = ttk.Frame(options_frame)
        vis_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(vis_frame, 
                 text="Vis offentligt:",
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        self.vis_offentligt_var = tk.BooleanVar(value=True)
        vis_check = ttk.Checkbutton(vis_frame,
                                    text="Ja, vis billederne offentligt",
                                    variable=self.vis_offentligt_var)
        vis_check.pack(side=tk.LEFT, padx=(10, 0))
        
        # License type option
        license_frame = ttk.Frame(options_frame)
        license_frame.pack(fill=tk.X)
        
        ttk.Label(license_frame,
                 text="Licenstype:",
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        self.license_var = tk.StringVar(value="Public Domain - PD")
        license_dropdown = ttk.Combobox(license_frame,
                                       textvariable=self.license_var,
                                       values=LICENSE_TYPES,
                                       state='readonly',
                                       width=40,
                                       font=('Segoe UI', 10))
        license_dropdown.pack(fill=tk.X)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        cancel_btn = tk.Button(button_frame,
                              text="Annuller",
                              font=('Segoe UI', 10),
                              bg='#94a3b8',
                              fg='white',
                              relief=tk.FLAT,
                              padx=20, pady=10,
                              cursor='hand2',
                              command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        ok_btn = tk.Button(button_frame,
                          text="OK - Start Upload",
                          font=('Segoe UI', 10, 'bold'),
                          bg='#10b981',
                          fg='white',
                          relief=tk.FLAT,
                          padx=20, pady=10,
                          cursor='hand2',
                          command=self.ok)
        ok_btn.pack(side=tk.RIGHT)
        
    def ok(self):
        """OK button clicked"""
        self.result = {
            'vis_offentligt': 'x' if self.vis_offentligt_var.get() else '',
            'licenstype': self.license_var.get()
        }
        self.dialog.destroy()
        
    def cancel(self):
        """Cancel button clicked"""
        self.result = None
        self.dialog.destroy()
        
    def show(self):
        """Show dialog and wait for result"""
        self.dialog.wait_window()
        return self.result


class SaraUploader:
    """SARA batch upload system for compressed images"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.auth = HTTPBasicAuth(USERNAME, PASSWORD)
    
    def login_to_sara(self):
        """Authenticate with the SARA API"""
        try:
            response = requests.get(
                self.base_url,
                params={'command': 'login'},
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'auth': self.auth,
                    'cookies': response.cookies
                }
        except Exception as e:
            print(f"Login error: {e}")
        
        return None
    
    def search_object_by_number(self, auth_info, object_number):
        """Search for an object by object number and get its priref and existing reproductions"""
        auth = auth_info.get('auth')
        cookies = auth_info.get('cookies')
        
        try:
            params = {
                'command': 'search',
                'database': 'collect',
                'search': f'object_number="{object_number}"',
                'output': 'json',
                'limit': 1
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                auth=auth,
                cookies=cookies,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we found the object
                if data.get('adlibJSON', {}).get('diagnostic', {}).get('hits', 0) > 0:
                    record = data['adlibJSON']['recordList']['record'][0]
                    priref = record.get('@priref')
                    
                    # Get existing reproductions
                    existing_reproductions = []
                    reproductions = record.get('Reproduction', [])
                    
                    if isinstance(reproductions, dict):
                        reproductions = [reproductions]
                    
                    for repro in reproductions:
                        ref = repro.get('reproduction.reference', {})
                        if isinstance(ref, dict):
                            ref_text = ref.get('spans', [{}])[0].get('text', '')
                        else:
                            ref_text = ref
                        
                        if ref_text:
                            # Get license type
                            license_data = repro.get('reproduction.license_type', [])
                            license_short = 'PD'
                            license_full = 'Public Domain - PD'
                            
                            if license_data:
                                if isinstance(license_data, list):
                                    for lic in license_data:
                                        if lic.get('lang') == 'neutral':
                                            license_short = lic.get('value', {}).get('spans', [{}])[0].get('text', 'PD')
                                        elif lic.get('lang') == 0 or lic.get('lang') == '0':
                                            license_full = lic.get('value', {}).get('spans', [{}])[0].get('text', 'Public Domain - PD')
                            
                            # Get publish status
                            publish = repro.get('reproduction.publish_on_website', {})
                            if isinstance(publish, dict):
                                publish_text = publish.get('spans', [{}])[0].get('text', '')
                            else:
                                publish_text = publish
                            
                            existing_reproductions.append({
                                'reference': ref_text,
                                'license_short': license_short,
                                'license_full': license_full,
                                'publish': publish_text
                            })
                    
                    return {
                        'priref': priref,
                        'object_number': object_number,
                        'existing_reproductions': existing_reproductions
                    }
            
        except Exception as e:
            print(f"Search error for {object_number}: {e}")
        
        return None
    
    def upload_single_image(self, auth_info, image_path, uuid_filename):
        """Upload a single image with specified UUID filename"""
        auth = auth_info.get('auth')
        cookies = auth_info.get('cookies')
        
        try:
            with open(image_path, 'rb') as img_file:
                file_data = img_file.read()
                
                params = {
                    'command': 'writecontent',
                    'server': 'images',
                    'value': uuid_filename
                }
                
                response = requests.post(
                    self.base_url,
                    params=params,
                    data=file_data,
                    headers={'Content-Type': 'image/jpeg'},
                    auth=auth,
                    cookies=cookies,
                    timeout=30
                )
                
                if response.status_code == 200 and 'error' not in response.text.lower():
                    return True
                else:
                    print(f"Upload failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"Error uploading {image_path}: {e}")
            return False
    
    def extract_object_number(self, filename):
        """Extract object number from filename (supports multiple formats)"""
        # Remove file extension
        stem = os.path.splitext(filename)[0]
        
        # Support multiple formats:
        # 1. Traditional: 0054x0007, 1234X4321
        # 2. Genstands format: 00073;15, 12345;2015
        # 3. AAB format: AAB 1234
        # 4. Standalone: 1234
        
        patterns = [
            (r'(\d{4}[xX]\d{3,4})', 'traditional'),      # 1234x4321
            (r'(\d+;\d{2,4})', 'genstands'),             # 00073;15
            (r'AAB\s+(\d{4})', 'aab'),                   # AAB 1234
            (r'^(\d{4})$', 'standalone')                 # 1234 (only if entire filename)
        ]
        
        for pattern, format_type in patterns:
            match = re.search(pattern, stem)
            if match:
                return match.group(1)
        
        return ""  # No valid object number found
    
    def batch_upload_images(self, image_files_or_data, output_xml_path=None, parent_window=None):
        """
        Batch upload images to SARA and generate XML for import
        
        Args:
            image_files_or_data: List of file paths OR list of dicts with 'filename' and 'data'
            output_xml_path: Optional path for XML output (defaults to desktop)
            parent_window: Parent window for dialogs
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Show configuration dialog for license and visibility settings
        config_dialog = SaraUploadConfigDialog(parent_window)
        config = config_dialog.show()
        
        if not config:
            # User cancelled
            return False
        
        # Determine if we have file paths or data
        is_file_paths = isinstance(image_files_or_data[0], str)
        
        if is_file_paths:
            total_images = len(image_files_or_data)
        else:
            total_images = len(image_files_or_data)
        
        print("=" * 70)
        print("SARA Batch Image Upload")
        print("=" * 70)
        print(f"Found {total_images} images to upload\n")
        
        # Login first
        auth_info = self.login_to_sara()
        if not auth_info:
            messagebox.showerror("SARA Fejl", "Kunne ikke logge ind på SARA API")
            return False
        
        print("✓ Login successful!")
        
        # Prepare data for CSV
        upload_records = []
        
        # Process each image
        for i in range(total_images):
            if is_file_paths:
                image_path = image_files_or_data[i]
                original_filename = os.path.basename(image_path)
            else:
                # Data provided as dict
                image_data_dict = image_files_or_data[i]
                original_filename = image_data_dict['filename']
                # Create temp file from data
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                temp_file.write(image_data_dict['data'])
                temp_file.close()
                image_path = temp_file.name
            
            print(f"\n[{i+1}/{total_images}] Processing: {original_filename}")
            
            # Generate UUID filename
            file_extension = os.path.splitext(original_filename)[1]
            uuid_filename = str(uuid.uuid4()) + file_extension
            
            print(f"  UUID: {uuid_filename}")
            
            # Upload the image
            success = self.upload_single_image(auth_info, image_path, uuid_filename)
            
            if success:
                print(f"  ✓ Upload successful")
                
                # Extract object number
                object_number = self.extract_object_number(original_filename)
                
                # Store record for CSV
                upload_records.append({
                    'original_filename': original_filename,
                    'object_number': object_number,
                    'uuid_filename': uuid_filename,
                    'upload_date': datetime.now().strftime('%Y-%m-%d')
                })
            else:
                print(f"  ✗ Upload failed")
            
            # Clean up temp file if created
            if not is_file_paths:
                try:
                    os.unlink(image_path)
                except:
                    pass
        
        # Generate XML for SARA import with merged reproductions
        if upload_records:
            print("\n" + "=" * 70)
            print(f"Successfully uploaded {len(upload_records)} images")
            print("=" * 70)
            
            # Determine XML output path
            if not output_xml_path:
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_xml_path = os.path.join(desktop, f"SARA_Import_{timestamp}.xml")
            
            # Group images by object number
            objects_dict = {}
            for record in upload_records:
                obj_num = record['object_number']
                if obj_num:
                    if obj_num not in objects_dict:
                        objects_dict[obj_num] = []
                    objects_dict[obj_num].append(record['uuid_filename'])
            
            # Map license type
            license_map = {
                "Public Domain - PD": "PD",
                "Creative Commons - CC BY-NC-ND": "CC BY-NC-ND",
                "Creative Commons - CC BY-NC-SA": "CC BY-NC-SA",
                "Creative Commons - CC BY-ND": "CC BY-ND",
                "Creative Commons - CC BY-NC": "CC BY-NC",
                "Creative Commons - CC BY-SA": "CC BY-SA",
                "Creative Commons - CC BY": "CC BY",
                "No Known Copyright - NKC": "NKC",
                "Copyright - C": "C"
            }
            license_short = license_map.get(config['licenstype'], 'PD')
            license_full = config['licenstype']
            
            print("\n" + "=" * 70)
            print("Fetching existing reproductions from SARA...")
            print("=" * 70)
            
            # For each object, fetch existing reproductions and merge
            try:
                root = ET.Element('adlibXML')
                record_list = ET.SubElement(root, 'recordList')
                
                for obj_number, new_uuid_files in objects_dict.items():
                    print(f"\nProcessing object: {obj_number}")
                    
                    # Search for the object and get existing reproductions
                    obj_info = self.search_object_by_number(auth_info, obj_number)
                    
                    if obj_info:
                        priref = obj_info['priref']
                        existing = obj_info['existing_reproductions']
                        
                        print(f"  Found priref: {priref}")
                        print(f"  Existing images: {len(existing)}")
                        print(f"  New images: {len(new_uuid_files)}")
                        
                        # Create record
                        record = ET.SubElement(record_list, 'record')
                        
                        # Add priref as element (not attribute)
                        priref_elem = ET.SubElement(record, 'priref')
                        priref_elem.text = str(priref)
                        
                        # Add object number
                        obj_num_elem = ET.SubElement(record, 'object_number')
                        obj_num_elem.set('tag', 'IN')
                        obj_num_elem.text = obj_number
                        
                        # Build complete list: existing + new
                        all_reproductions = []
                        
                        # Add existing reproductions first
                        for ex in existing:
                            all_reproductions.append({
                                'reference': ex['reference'],
                                'license_short': ex['license_short'],
                                'license_full': ex['license_full'],
                                'publish': ex['publish']
                            })
                        
                        # Add new reproductions
                        for new_uuid in new_uuid_files:
                            all_reproductions.append({
                                'reference': new_uuid,
                                'license_short': license_short,
                                'license_full': license_full,
                                'publish': config['vis_offentligt']
                            })
                        
                        print(f"  Total images in XML: {len(all_reproductions)}")
                        
                        # Add all reproductions to XML
                        for idx, repro_data in enumerate(all_reproductions, start=1):
                            reproduction = ET.SubElement(record, 'Reproduction')
                            
                            # Image reference
                            ref_elem = ET.SubElement(reproduction, 'reproduction.reference')
                            ref_elem.set('tag', 'FN')
                            ref_elem.set('occ', str(idx))
                            ref_elem.text = repro_data['reference']
                            
                            # License type
                            license_elem = ET.SubElement(reproduction, 'reproduction.license_type')
                            license_elem.set('tag', 'Fl')
                            license_elem.set('occ', str(idx))
                            
                            value_neutral = ET.SubElement(license_elem, 'value')
                            value_neutral.set('lang', 'neutral')
                            value_neutral.text = repro_data['license_short']
                            
                            value_0 = ET.SubElement(license_elem, 'value')
                            value_0.set('lang', '0')
                            value_0.text = repro_data['license_full']
                            
                            value_11 = ET.SubElement(license_elem, 'value')
                            value_11.set('lang', '11')
                            value_11.text = repro_data['license_full']
                            
                            # Publish on website
                            publish_elem = ET.SubElement(reproduction, 'reproduction.publish_on_website')
                            publish_elem.set('tag', 'mu')
                            publish_elem.set('occ', str(idx))
                            publish_elem.text = repro_data['publish']
                    else:
                        print(f"  ✗ Object not found in SARA - skipping")
                
                # Convert to string WITHOUT minidom (to avoid XML declaration issues)
                xml_string = ET.tostring(root, encoding='unicode', method='xml')
                
                # Write to file with UTF-8 encoding
                with open(output_xml_path, 'w', encoding='utf-8') as f:
                    f.write(xml_string)
                
                print(f"\n✓ XML saved to: {output_xml_path}")
                print(f"\n⚠️  VIGTIGT: XML indeholder BÅDE gamle og nye billeder")
                print(f"   Når du importerer, vil de blive merged korrekt")
                
                # Show success message
                messagebox.showinfo(
                    "SARA Upload Færdig",
                    f"Upload fuldført!\n\n"
                    f"✓ {len(upload_records)} billeder uploadet til SARA\n"
                    f"✓ XML fil gemt på skrivebordet\n\n"
                    f"Fil: {os.path.basename(output_xml_path)}\n\n"
                    f"✅ XML indeholder BÅDE eksisterende og nye billeder\n"
                    f"   De vil blive merged når du importerer!\n\n"
                    f"Indstillinger:\n"
                    f"• Licens: {config['licenstype']}\n"
                    f"• Vis offentligt: {'Ja' if config['vis_offentligt'] == 'x' else 'Nej'}\n\n"
                    f"Næste trin:\n"
                    f"1. Åbn SARA i din browser\n"
                    f"2. Importér XML filen\n"
                    f"3. Gamle billeder bevares!"
                )
                
                return True
                
            except Exception as e:
                print(f"Error creating XML: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("XML Fejl", f"Kunne ikke oprette XML fil: {e}")
                return False
        
        else:
            print("\n✗ No images were successfully uploaded")
            messagebox.showerror("Upload Fejl", "Ingen billeder blev uploadet succesfuldt")
            return False


# Convenience function for backward compatibility
def batch_upload_image_files(image_files, output_xml_path=None):
    """
    Convenience function to upload image files to SARA
    
    Args:
        image_files: List of image file paths
        output_xml_path: Optional path for XML output
    
    Returns:
        bool: True if successful
    """
    uploader = SaraUploader()
    return uploader.batch_upload_images(image_files, output_xml_path)


# Test function
if __name__ == "__main__":
    # Example usage
    test_images = [
        r"c:\Users\mfed\Desktop\test\0217x0054 a.jpg",
    ]
    
    uploader = SaraUploader()
    uploader.batch_upload_images(test_images)
