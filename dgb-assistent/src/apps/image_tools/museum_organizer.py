"""
Museum File Organizer - DGB Assistent
Håndterer organisering af billeder til den korrekte museum mappestruktur
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from tkinter import messagebox


class MuseumOrganizer:
    """Organiserer billeder til museum mappestruktur baseret på sagnummer"""
    
    def __init__(self):
        # Base path til museum mapper
        self.base_path = r"M:\Museumsfaglig afdeling\0 Museets Samlinger\6 Genstandsfotos"
        
        # For test/udvikling kan vi bruge en lokal mappe
        if not os.path.exists(self.base_path):
            # Fallback til lokal test mappe
            self.base_path = os.path.join(os.getcwd(), "test_museum_folders")
            print(f"Museum base path ikke fundet, bruger test mappe: {self.base_path}")
    
    def extract_case_number(self, filename: str) -> Optional[str]:
        """Udtræk sagnummer fra filnavn som '1234x4321' -> '1234'"""
        # Søg efter mønster som 1234x4321 hvor 1234 er sagnummer
        match = re.search(r'(\d{4})x\d{4}', filename)
        if match:
            return match.group(1)
        
        # Alternative mønstre
        # Søg efter AAB 1234 eller bare 1234 i starten
        match = re.search(r'(?:AAB\s+)?(\d{4})', filename)
        if match:
            return match.group(1)
        
        return None
    
    def get_case_folder_path(self, case_number: str) -> str:
        """Generer den fulde sti til sag mappen"""
        if not case_number or len(case_number) != 4:
            raise ValueError(f"Ugyldigt sagnummer: {case_number}")
        
        try:
            case_num = int(case_number)
        except ValueError:
            raise ValueError(f"Sagnummer skal være numerisk: {case_number}")
        
        # Bestem hundred range mappe
        hundred_start = (case_num // 100) * 100
        if hundred_start == 0:
            hundred_folder = "Sag 0001-0099"
        else:
            hundred_end = hundred_start + 99
            hundred_folder = f"Sag {hundred_start:04d}-{hundred_end:04d}"
        
        # Bestem ten range mappe
        ten_start = (case_num // 10) * 10
        ten_end = ten_start + 9
        ten_folder = f"Sag {ten_start:04d}-{ten_end:04d}"
        
        # Final case folder
        case_folder = f"Sag {case_number}"
        
        # Byg fuld sti
        full_path = os.path.join(
            self.base_path,
            hundred_folder,
            ten_folder,
            case_folder
        )
        
        return full_path
    
    def verify_and_create_path(self, case_number: str, ask_user: bool = True) -> Tuple[bool, str]:
        """
        Verificer om stien findes, og spørg brugeren om den skal oprettes hvis ikke
        Returns: (success, message)
        """
        try:
            target_path = self.get_case_folder_path(case_number)
            
            if os.path.exists(target_path):
                return True, f"Mappe findes: {target_path}"
            
            # Mappe findes ikke
            if ask_user:
                response = messagebox.askyesno(
                    "Opret Mappe?",
                    f"Mappen for sag {case_number} findes ikke:\n\n"
                    f"{target_path}\n\n"
                    f"Skal mappen oprettes?"
                )
                
                if response:
                    os.makedirs(target_path, exist_ok=True)
                    return True, f"Mappe oprettet: {target_path}"
                else:
                    return False, f"Bruger afviste oprettelse af mappe for sag {case_number}"
            else:
                # Auto-opret uden at spørge
                os.makedirs(target_path, exist_ok=True)
                return True, f"Mappe auto-oprettet: {target_path}"
                
        except Exception as e:
            return False, f"Fejl ved håndtering af sag {case_number}: {str(e)}"
    
    def organize_files(self, files_data: List[Dict], ask_before_create: bool = True) -> Dict:
        """
        Organisér filer til deres korrekte museum mapper
        files_data: Liste af dicts med 'filename' og 'data' eller 'source_path'
        """
        results = {
            'success': [],
            'errors': [],
            'created_folders': set(),
            'skipped': []
        }
        
        # Check base path
        if not os.path.exists(self.base_path):
            try:
                os.makedirs(self.base_path, exist_ok=True)
                results['created_folders'].add(self.base_path)
            except Exception as e:
                results['errors'].append(f"Kunne ikke oprette base mappe {self.base_path}: {str(e)}")
                return results
        
        for file_info in files_data:
            filename = file_info.get('filename', '')
            
            # Udtræk sagnummer
            case_number = self.extract_case_number(filename)
            if not case_number:
                results['skipped'].append(f"Kunne ikke finde sagnummer i: {filename}")
                continue
            
            try:
                # Verificer/opret mappe
                success, message = self.verify_and_create_path(case_number, ask_before_create)
                if not success:
                    results['errors'].append(message)
                    continue
                
                # Få target sti
                target_folder = self.get_case_folder_path(case_number)
                target_file_path = os.path.join(target_folder, filename)
                
                # Kopiér eller flyt filen
                if 'data' in file_info:
                    # Skriv data direkte til fil
                    with open(target_file_path, 'wb') as f:
                        f.write(file_info['data'])
                    results['success'].append(f"Gemt {filename} til {target_file_path}")
                    
                elif 'source_path' in file_info:
                    # Kopiér fra kilde fil
                    shutil.copy2(file_info['source_path'], target_file_path)
                    results['success'].append(f"Kopieret {filename} til {target_file_path}")
                    
                else:
                    results['errors'].append(f"Ingen data eller kilde sti for {filename}")
                
            except Exception as e:
                results['errors'].append(f"Fejl ved organisering af {filename}: {str(e)}")
        
        return results
    
    def get_existing_cases(self) -> List[str]:
        """Få liste over eksisterende sagnumre i museum systemet"""
        existing_cases = []
        
        try:
            if not os.path.exists(self.base_path):
                return existing_cases
            
            # Gennemgå hundred folders
            for hundred_folder in os.listdir(self.base_path):
                hundred_path = os.path.join(self.base_path, hundred_folder)
                if not os.path.isdir(hundred_path):
                    continue
                
                # Gennemgå ten folders
                for ten_folder in os.listdir(hundred_path):
                    ten_path = os.path.join(hundred_path, ten_folder)
                    if not os.path.isdir(ten_path):
                        continue
                    
                    # Gennemgå case folders
                    for case_folder in os.listdir(ten_path):
                        case_path = os.path.join(ten_path, case_folder)
                        if not os.path.isdir(case_path):
                            continue
                        
                        # Udtræk sagnummer fra folder navn
                        match = re.search(r'Sag (\d{4})', case_folder)
                        if match:
                            existing_cases.append(match.group(1))
        
        except Exception as e:
            print(f"Fejl ved scanning af eksisterende sager: {e}")
        
        return sorted(existing_cases)
    
    def validate_filename(self, filename: str) -> Tuple[bool, str]:
        """Validér om et filnavn kan organiseres"""
        case_number = self.extract_case_number(filename)
        
        if not case_number:
            return False, "Intet sagnummer fundet i filnavnet"
        
        try:
            case_num = int(case_number)
            if case_num < 1 or case_num > 9999:
                return False, f"Sagnummer {case_number} er uden for gyldigt interval (0001-9999)"
        except ValueError:
            return False, f"Sagnummer {case_number} er ikke numerisk"
        
        return True, f"Gyldigt sagnummer: {case_number}"


def test_organizer():
    """Test funktionen for museum organizer"""
    organizer = MuseumOrganizer()
    
    # Test filnavne
    test_files = [
        "1234x5678.jpg",
        "AAB 0156x0234 a.jpg",
        "0001x0001.jpg",
        "invalid_filename.jpg",
        "9999x1111.jpg"
    ]
    
    print("Testing Museum Organizer:")
    print("-" * 40)
    
    for filename in test_files:
        case_number = organizer.extract_case_number(filename)
        valid, message = organizer.validate_filename(filename)
        
        print(f"Fil: {filename}")
        print(f"  Sagnummer: {case_number}")
        print(f"  Validering: {message}")
        
        if case_number:
            try:
                path = organizer.get_case_folder_path(case_number)
                print(f"  Målmappe: {path}")
            except Exception as e:
                print(f"  Fejl: {e}")
        
        print()


if __name__ == "__main__":
    test_organizer()