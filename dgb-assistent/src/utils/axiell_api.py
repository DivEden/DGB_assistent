"""
Axiell WebAPI Client for DGB Assistent
Handles authentication and communication with Axiell collection management system
"""

import os
import requests
import json
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin
import base64

# Axiell WebAPI Configuration Constants - CORRECT API FROM PROVIDER
AXIELL_BASE_URL = "https://sara-api.adlibhosting.com/SARA-011-DGB/"
AXIELL_DATABASE = "collection"  # Confirmed database name from API provider


class AxiellAPIClient:
    """Client for Axiell WebAPI integration"""
    
    def __init__(self):
        """Initialize the Axiell API client with credentials from secure config"""
        from .secure_config import get_secure_config
        
        # Load credentials securely
        secure_config = get_secure_config()
        credentials = secure_config.load_credentials()
        
        if credentials:
            self.username = credentials['username']
            self.password = credentials['password']  
        else:
            self.username = None
            self.password = None
        
        # Use constants for base URL and database
        self.base_url = AXIELL_BASE_URL
        self.database = AXIELL_DATABASE
        
        self.session = None
        self.authenticated = False
        self.secure_config = secure_config
        
        # Don't raise error here - let the app handle missing credentials gracefully
    
    def authenticate(self) -> bool:
        """
        Authenticate with Axiell WebAPI (demo server may not require auth)
        Returns True if successful, False otherwise
        """
        try:
            self.session = requests.Session()
            
            # For demo server, try without authentication first
            if "webapi.axiell.com" in self.base_url:
                print("Using Axiell demo server - no authentication required")
                self.session.headers.update({
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                })
            else:
                # For production servers, authentication is required
                if not all([self.username, self.password]):
                    print("Production server requires credentials. Please configure API access first.")
                    return False
                
                print(f"Authenticating to production server with user: {self.username}")
                
                # Create basic auth header for production
                credentials = f"{self.username}:{self.password}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()
                
                self.session.headers.update({
                    'Authorization': f'Basic {encoded_credentials}',
                    'Content-Type': 'application/xml',  # Axiell often prefers XML
                    'Accept': 'application/json, application/xml'
                })
            
            # Test connection with a simple Axiell WebAPI request
            test_url = urljoin(self.base_url, 'wwwopac.ashx')
            test_params = {'database': self.database, 'limit': 1}
            response = self.session.get(test_url, params=test_params, timeout=10)
            
            if response.status_code == 200:
                self.authenticated = True
                print("✅ Connection to Axiell WebAPI successful")
                return True
            else:
                print(f"Connection failed: {response.status_code} - {response.text[:200]}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during connection: {e}")
            return False
    
    def setup_credentials(self, parent=None) -> bool:
        """Setup credentials through GUI"""
        return self.secure_config.setup_credentials_gui(parent)
    
    def search_objects(self, object_number: str) -> List[Dict]:
        """
        Search for objects by objektnummer using Axiell WebAPI
        
        Args:
            object_number: The objektnummer to search for (e.g., "0054x0007")
            
        Returns:
            List of matching objects from Axiell
        """
        if not self.authenticated:
            if not self.authenticate():
                raise Exception("Failed to authenticate with Axiell API")
        
        try:
            # Use the correct Axiell WebAPI endpoint from documentation
            search_url = urljoin(self.base_url, 'wwwopac.ashx')
            
            # Use confirmed database name from API provider
            # Database is confirmed to be 'collection'
            
            # Search parameters based on API provider examples
            # Primary field is 'IN' for inventory numbers as shown in examples
            search_statements = [
                f"IN='{object_number}'",                     # Primary field from API examples
                f"objektnummer='{object_number}'",           # Standard Danish field name
                f"priref='{object_number}'",                 # Primary reference (if numeric)
                f"genstandsnummer='{object_number}'",        # Object number variant
                f"katalognummer='{object_number}'",          # Catalog number
                f"inventarnummer='{object_number}'",         # Full inventory number
                f"object_number='{object_number}'",          # English field name
                f"genstand.objektnummer='{object_number}'",  # Genstand (object) sub-field
                f"internt_objektkatalog='{object_number}'"   # Internal object catalog
            ]
            
            results = []
            
            # Use confirmed database from API provider
            databases_to_try = [self.database]  # Only 'collection' database
            
            for database in databases_to_try:
                for search_statement in search_statements:
                    params = {
                        'database': database,
                        'search': search_statement,
                        'xmltype': 'grouped',
                        'limit': 100,
                        'output': 'json'
                    }
                    
                    response = self.session.get(search_url, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            # Check if we got results
                            if data.get('adlibJSON', {}).get('recordList', {}).get('record'):
                                records = data['adlibJSON']['recordList']['record']
                                # Ensure records is always a list
                                if isinstance(records, dict):
                                    records = [records]
                                print(f"✅ Found {len(records)} result(s) in database '{database}' using field '{search_statement}'")
                                results.extend(records)
                                return results  # Return immediately when we find results
                        except json.JSONDecodeError:
                            continue  # Try next search statement
                    elif response.status_code != 500:  # Don't spam with 500 errors
                        continue  # Try next combination
                        
                if results:  # If we found results, stop trying other databases
                    break
                        
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching Axiell API: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error in search: {e}")
            return []
    
    def get_object_details(self, object_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific object
        
        Args:
            object_id: The unique identifier of the object in Axiell
            
        Returns:
            Dictionary with object details or None if not found
        """
        if not self.authenticated:
            if not self.authenticate():
                raise Exception("Failed to authenticate with Axiell API")
        
        try:
            # Construct detail URL
            detail_url = urljoin(self.base_url, f'objects/{self.database}/{object_id}')
            
            response = self.session.get(detail_url, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching object details: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error fetching details: {e}")
            return None
    
    def validate_object_number(self, object_number: str) -> Tuple[bool, str]:
        """
        Validate if an objektnummer exists in Axiell
        
        Args:
            object_number: The objektnummer to validate (e.g., "0054x0007")
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            results = self.search_objects(object_number)
            
            if results:
                return True, f"Found {len(results)} object(s) for objektnummer {object_number}"
            else:
                return False, f"No objects found for objektnummer {object_number}"
                
        except Exception as e:
            return False, f"Error validating objektnummer: {e}"
    
    def get_connection_status(self) -> Dict[str, str]:
        """
        Get current connection status information
        
        Returns:
            Dictionary with connection status details
        """
        status = {
            'configured': bool(self.username and self.password),
            'authenticated': self.authenticated,
            'base_url': self.base_url,
            'database': self.database,
            'username': self.username or 'Not configured'
        }
        return status


def load_environment():
    """
    Load environment variables from .env file
    This should be called at application startup
    """
    try:
        # Try to load python-dotenv if available
        from dotenv import load_dotenv
        load_dotenv()
        return True
    except ImportError:
        # If python-dotenv is not installed, try to load manually
        env_file = '.env'
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
            return True
        return False
    except Exception as e:
        print(f"Error loading environment: {e}")
        return False


# Global instance - initialize when needed
_axiell_client = None

def get_axiell_client() -> AxiellAPIClient:
    """Get the global Axiell API client instance"""
    global _axiell_client
    
    if _axiell_client is None:
        # Load environment first
        load_environment()
        _axiell_client = AxiellAPIClient()
    
    return _axiell_client