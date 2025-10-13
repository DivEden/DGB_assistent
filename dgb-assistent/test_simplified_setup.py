"""
Test script to verify the simplified credential setup
Shows how users will set up only username and password
"""

import sys
import os

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.secure_config import get_secure_config
from utils.axiell_api import get_axiell_client, AXIELL_BASE_URL, AXIELL_DATABASE

def test_simplified_setup():
    """Test the simplified credential setup"""
    print("=== DGB Assistent - Simplified Credential Setup Test ===\n")
    
    print(f"Configured server: {AXIELL_BASE_URL}")
    print(f"Configured database: {AXIELL_DATABASE}")
    print()
    
    # Clear any existing credentials for clean test
    config = get_secure_config()
    config.clear_credentials()
    
    print("Testing credential setup dialog...")
    print("This will show the simplified dialog with only username and password fields.")
    print("The server URL is now hardcoded as a constant.")
    print()
    
    # Test the setup
    success = config.setup_credentials_gui()
    
    if success:
        print("✓ Credentials saved successfully!")
        
        # Test loading credentials
        credentials = config.load_credentials()
        if credentials:
            print(f"✓ Username: {credentials['username']}")
            print("✓ Password: [HIDDEN]")
        
        # Test API client initialization
        client = get_axiell_client()
        status = client.get_connection_status()
        
        print("\n=== Connection Status ===")
        print(f"Configured: {status['configured']}")
        print(f"Base URL: {status['base_url']}")
        print(f"Database: {status['database']}")
        print(f"Username: {status['username']}")
        
    else:
        print("❌ Setup cancelled or failed")

if __name__ == "__main__":
    test_simplified_setup()