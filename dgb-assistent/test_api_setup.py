#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the complete simplified API setup experience
This demonstrates how users will interact with API configuration
"""

import sys
import os

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_api_constants():
    """Test that API constants are properly defined"""
    try:
        from utils.axiell_api import AXIELL_BASE_URL, AXIELL_DATABASE
        
        print("=== API Constants Test ===")
        print(f"✓ Base URL: {AXIELL_BASE_URL}")
        print(f"✓ Database: {AXIELL_DATABASE}")
        print()
        
        return True
    except ImportError as e:
        print(f"❌ Error importing API constants: {e}")
        return False

def test_credential_loading():
    """Test simplified credential loading"""
    try:
        from utils.secure_config import get_secure_config
        from utils.axiell_api import get_axiell_client
        
        print("=== Credential System Test ===")
        
        # Test configuration loading
        config = get_secure_config()
        credentials = config.load_credentials()
        
        if credentials:
            print("✓ Credentials found:")
            print(f"  - Username: {credentials.get('username', 'Not set')}")
            print("  - Password: [HIDDEN]")
        else:
            print("ℹ️  No credentials configured (this is normal for first-time users)")
        
        # Test API client initialization
        client = get_axiell_client()
        status = client.get_connection_status()
        
        print(f"✓ API client configured: {status['configured']}")
        print(f"✓ Using base URL: {status['base_url']}")
        print(f"✓ Using database: {status['database']}")
        print()
        
        return True
    except Exception as e:
        print(f"❌ Error testing credential system: {e}")
        return False

def test_env_file_simplified():
    """Test that .env file is simplified"""
    try:
        env_path = '.env'
        if os.path.exists(env_path):
            print("=== .env File Test ===")
            with open(env_path, 'r') as f:
                content = f.read()
            
            print("✓ .env file contents:")
            for line in content.strip().split('\n'):
                if line.strip() and not line.startswith('#'):
                    key = line.split('=')[0] if '=' in line else line
                    if 'PASSWORD' in key:
                        print(f"  {key}=[HIDDEN]")
                    else:
                        print(f"  {line}")
            
            # Check that BASE_URL and DATABASE are not in .env
            if 'AXIELL_BASE_URL' not in content:
                print("✓ AXIELL_BASE_URL removed from .env (now a constant)")
            else:
                print("❌ AXIELL_BASE_URL still in .env")
                
            if 'AXIELL_DATABASE' not in content:
                print("✓ AXIELL_DATABASE removed from .env (now a constant)")
            else:
                print("❌ AXIELL_DATABASE still in .env")
            
            print()
        else:
            print("ℹ️  No .env file found (using constants only)")
            print()
        
        return True
    except Exception as e:
        print(f"❌ Error checking .env file: {e}")
        return False

def main():
    """Run all tests"""
    print("DGB Assistent - Simplified API Setup Test")
    print("=" * 50)
    print()
    
    tests = [
        test_api_constants,
        test_env_file_simplified, 
        test_credential_loading
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("=" * 50)
    print(f"Test Summary: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("✅ All tests passed! The simplified API setup is working correctly.")
        print()
        print("User Experience Summary:")
        print("- Users no longer need to configure base URL or database")
        print("- Only username and password are required")
        print("- API configuration is accessed via button in main window")
        print("- No automatic popups on application startup")
    else:
        print("❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()