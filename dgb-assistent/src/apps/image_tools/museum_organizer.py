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
    
    def extract_genstand_info(self, filename: str) -> Optional[tuple]:
        """
        Udtræk genstands-info fra filnavn med ';' format
        Returns: (genstands_nummer, registrerings_år) eller None
        Eksempel: '00073;15' -> ('00073', 1915)
        """
        # Søg efter mønster som 00073;15 eller 00073;2015
        match = re.search(r'(\d+);(\d{2,4})', filename)
        if not match:
            return None
        
        genstands_nr = match.group(1).zfill(5)  # Pad til 5 cifre
        year_suffix = match.group(2)
        
        # Konverter år-suffiks til fuldt år
        if len(year_suffix) == 2:
            # To-cifret år: 15 -> 1915, 99 -> 1999
            year_int = int(year_suffix)
            if year_int >= 10:  # 1910'erne og frem
                full_year = 1900 + year_int
            else:
                # 00-09 -> 2000-2009
                full_year = 2000 + year_int
        else:
            # Fire-cifret år: 2015 -> 2015
            full_year = int(year_suffix)
        
        return (genstands_nr, full_year)
    
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
    
    def get_genstand_folder_path(self, genstands_nr: str, registration_year: int) -> str:
        """
        Generer den fulde sti til genstands mappen baseret på registreringsår
        """
        # Bestem årti-mappe
        decade = (registration_year // 10) * 10
        decade_folder = f"Genstande registreret i {decade}'erne"
        
        # Byg fuld sti til år-mappen (vi returnerer parent, da år-mappen kan have forskellige navne)
        decade_path = os.path.join(self.base_path, decade_folder)
        
        return decade_path
    
    def find_existing_year_folder(self, decade_path: str, year: int) -> Optional[str]:
        """
        Scan for eksisterende år-mappe med forskellige navneformater
        """
        try:
            if not os.path.exists(decade_path):
                return None
            
            year_str = str(year)
            
            # Scan for forskellige år-mappe formater
            for item in os.listdir(decade_path):
                item_path = os.path.join(decade_path, item)
                if not os.path.isdir(item_path):
                    continue
                
                # Format 1: "1917" (bare år)
                if item == year_str:
                    return item_path
                
                # Format 2: "0401 Genstande registreret i 2001"
                if f"Genstande registreret i {year}" in item:
                    return item_path
                
                # Format 3: "0386 Genstande registreret i 1986"
                if item.endswith(f"registreret i {year}"):
                    return item_path
            
            return None
            
        except Exception as e:
            print(f"Fejl ved scanning efter år {year}: {e}")
            return None
    
    def find_existing_case_folder(self, case_number: str) -> Optional[str]:
        """
        Scan for eksisterende sag mapper med alternative navne
        Returns: fuld sti til eksisterende mappe eller None
        """
        try:
            # Få parent mappen (ten-range mappe)
            standard_path = self.get_case_folder_path(case_number)
            parent_path = os.path.dirname(standard_path)
            
            if not os.path.exists(parent_path):
                return None
            
            # Scan for forskellige navngivningsformater
            for item in os.listdir(parent_path):
                item_path = os.path.join(parent_path, item)
                if not os.path.isdir(item_path):
                    continue
                
                # Format 1: "Sag 0030, beskrivelse..."
                if item.startswith(f"Sag {case_number},"):
                    return item_path
                
                # Format 2: "0030x" (bare nummeret med x)
                if item == f"{case_number}x":
                    return item_path
                
                # Format 3: Præcist match (sikkerhedscheck)
                if item == f"Sag {case_number}":
                    return item_path
            
            return None
            
        except Exception as e:
            print(f"Fejl ved scanning efter sag {case_number}: {e}")
            return None
    
    def verify_and_create_path_for_genstand(self, genstands_nr: str, registration_year: int, ask_user: bool = True) -> Tuple[bool, str]:
        """
        Verificer eller opret sti for genstands-nummer
        Returns: (success, target_path)
        """
        try:
            # Få årti-mappe sti
            decade_path = self.get_genstand_folder_path(genstands_nr, registration_year)
            
            # Tjek om årti-mappen findes
            if not os.path.exists(decade_path):
                if ask_user:
                    response = messagebox.askyesno(
                        "Opret Årti Mappe?",
                        f"Årti-mappen findes ikke:\n\n{decade_path}\n\n"
                        f"Skal mappen oprettes?"
                    )
                    if not response:
                        return False, f"Bruger afviste oprettelse af årti-mappe"
                
                os.makedirs(decade_path, exist_ok=True)
            
            # Find eller opret år-mappe
            existing_year_folder = self.find_existing_year_folder(decade_path, registration_year)
            
            if existing_year_folder:
                return True, existing_year_folder
            
            # År-mappe findes ikke - opret standard format
            year_folder_name = str(registration_year)
            year_folder_path = os.path.join(decade_path, year_folder_name)
            
            if ask_user:
                response = messagebox.askyesno(
                    "Opret År Mappe?",
                    f"År-mappen for {registration_year} findes ikke:\n\n"
                    f"{year_folder_path}\n\n"
                    f"Skal mappen oprettes?"
                )
                
                if not response:
                    return False, f"Bruger afviste oprettelse af år-mappe for {registration_year}"
            
            os.makedirs(year_folder_path, exist_ok=True)
            return True, year_folder_path
            
        except Exception as e:
            return False, f"Fejl ved håndtering af genstand {genstands_nr};{registration_year}: {str(e)}"

    def verify_and_create_path(self, case_number: str, ask_user: bool = True) -> Tuple[bool, str]:
        """
        Verificer om stien findes, og spørg brugeren om den skal oprettes hvis ikke
        Returns: (success, message)
        """
        try:
            target_path = self.get_case_folder_path(case_number)
            
            if os.path.exists(target_path):
                return True, f"Mappe findes: {target_path}"
            
            # Standard mappe findes ikke - scan for alternative navne
            existing_path = self.find_existing_case_folder(case_number)
            if existing_path:
                return True, f"Fandt eksisterende mappe: {existing_path}"
            
            # Ingen variation fundet - spørg om oprettelse
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
            
            # Tjek om det er genstands-nummer (med ';')
            genstand_info = self.extract_genstand_info(filename)
            if genstand_info:
                genstands_nr, registration_year = genstand_info
                
                try:
                    # Håndter genstands-nummer
                    success, target_folder = self.verify_and_create_path_for_genstand(
                        genstands_nr, registration_year, ask_before_create)
                    
                    if not success:
                        results['errors'].append(target_folder)  # target_folder er fejlbesked her
                        continue
                    
                    target_file_path = os.path.join(target_folder, filename)
                    
                except Exception as e:
                    results['errors'].append(f"Fejl ved organisering af genstand {filename}: {str(e)}")
                    continue
            
            else:
                # Traditionelt sagnummer system
                case_number = self.extract_case_number(filename)
                if not case_number:
                    results['skipped'].append(f"Kunne ikke finde sagnummer eller genstands-nummer i: {filename}")
                    continue
                
                try:
                    # Verificer/opret mappe
                    success, message = self.verify_and_create_path(case_number, ask_before_create)
                    if not success:
                        results['errors'].append(message)
                        continue
                    
                    # Få target sti - brug eksisterende hvis fundet, ellers den beregnede
                    existing_folder = self.find_existing_case_folder(case_number)
                    target_folder = existing_folder if existing_folder else self.get_case_folder_path(case_number)
                    target_file_path = os.path.join(target_folder, filename)
                
                except Exception as e:
                    results['errors'].append(f"Fejl ved organisering af sag {filename}: {str(e)}")
                    continue
            
            # Kopiér eller flyt filen (fælles for begge typer)
            try:
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
                results['errors'].append(f"Fejl ved fil-operation for {filename}: {str(e)}")
        
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
        
        # Tjek først for genstands-nummer
        genstand_info = self.extract_genstand_info(filename)
        if genstand_info:
            genstands_nr, registration_year = genstand_info
            
            # Validér registreringsår
            if registration_year < 1900 or registration_year > 2030:
                return False, f"Registreringsår {registration_year} er uden for gyldigt interval (1900-2030)"
            
            return True, f"Gyldigt genstands-nummer: {genstands_nr};{registration_year}"
        
        # Ellers tjek for traditionelt sagnummer
        case_number = self.extract_case_number(filename)
        
        if not case_number:
            return False, "Hverken sagnummer eller genstands-nummer fundet i filnavnet"
        
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
        "9999x1111.jpg",
        "00073;15.jpg",      # Genstand fra 1915
        "00073;2015.jpg",    # Genstand fra 2015
        "12345;85.jpg",      # Genstand fra 1985
        "AAB 00073;15.jpg"   # AAB præfiks med genstands-nummer
    ]
    
    print("Testing Museum Organizer:")
    print("-" * 40)
    
    for filename in test_files:
        case_number = organizer.extract_case_number(filename)
        genstand_info = organizer.extract_genstand_info(filename)
        valid, message = organizer.validate_filename(filename)
        
        print(f"Fil: {filename}")
        
        if genstand_info:
            genstands_nr, reg_year = genstand_info
            print(f"  Genstands-nr: {genstands_nr}, År: {reg_year}")
            try:
                decade_path = organizer.get_genstand_folder_path(genstands_nr, reg_year)
                print(f"  Årti-mappe: {decade_path}")
            except Exception as e:
                print(f"  Fejl: {e}")
        elif case_number:
            print(f"  Sagnummer: {case_number}")
            try:
                path = organizer.get_case_folder_path(case_number)
                print(f"  Målmappe: {path}")
            except Exception as e:
                print(f"  Fejl: {e}")
        
        print(f"  Validering: {message}")
        print()


if __name__ == "__main__":
    test_organizer()