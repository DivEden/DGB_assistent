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

# Axiell WebAPI Configuration Constants
AXIELL_BASE_URL = "https://sara.slks.dk/"
AXIELL_DATABASE = "objects"


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
        Authenticate with Axiell WebAPI
        Returns True if successful, False otherwise
        """
        # Check if credentials are available
        if not all([self.username, self.password]):
            print("No credentials available. Please configure API access first.")
            return False
            
        try:
            self.session = requests.Session()
            
            # Create basic auth header
            credentials = f"{self.username}:{self.password}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            self.session.headers.update({
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
            
            # Test authentication with a simple request
            test_url = urljoin(self.base_url, 'version')
            response = self.session.get(test_url, timeout=10)
            
            if response.status_code == 200:
                self.authenticated = True
                return True
            else:
                print(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Connection error during authentication: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during authentication: {e}")
            return False
    
    def setup_credentials(self, parent=None) -> bool:
        """Setup credentials through GUI"""
        return self.secure_config.setup_credentials_gui(parent)
    
    def search_objects(self, case_number: str) -> List[Dict]:
        """
        Search for objects by case number
        
        Args:
            case_number: The case number to search for (e.g., "1234x5678")
            
        Returns:
            List of matching objects from Axiell
        """
        if not self.authenticated:
            if not self.authenticate():
                raise Exception("Failed to authenticate with Axiell API")
        
        try:
            # Construct search URL - adjust endpoint based on your Axiell setup
            search_url = urljoin(self.base_url, f'search/{self.database}/objects')
            
            # Search parameters - adjust field names based on your database schema
            params = {
                'q': case_number,  # Simple text search
                'limit': 100,
                'format': 'json'
            }
            
            response = self.session.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('results', [])
            
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
    
    def validate_case_number(self, case_number: str) -> Tuple[bool, str]:
        """
        Validate if a case number exists in Axiell
        
        Args:
            case_number: The case number to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            results = self.search_objects(case_number)
            
            if results:
                return True, f"Found {len(results)} object(s) for case {case_number}"
            else:
                return False, f"No objects found for case {case_number}"
                
        except Exception as e:
            return False, f"Error validating case number: {e}"
    
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