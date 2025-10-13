"""
Test Axiell API forbindelse
Kør denne fil for at teste om dine API-oplysninger virker
"""

import os
import sys
sys.path.insert(0, 'src')

def test_connection():
    print("🔧 Tester Axiell API forbindelse...")
    print("=" * 40)
    
    try:
        # Load environment manually
        env_file = '.env'
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        # Check credentials
        username = os.getenv('AXIELL_USERNAME')
        password = os.getenv('AXIELL_PASSWORD')
        base_url = os.getenv('AXIELL_BASE_URL')
        database = os.getenv('AXIELL_DATABASE')
        
        print(f"Username: {username}")
        print(f"Password: {'*' * len(password) if password else 'MANGLER!'}")
        print(f"URL: {base_url}")
        print(f"Database: {database}")
        print()
        
        if not all([username, password, base_url]):
            print("❌ Manglende oplysninger i .env filen!")
            return
        
        # Test connection
        from utils.axiell_api import get_axiell_client
        client = get_axiell_client()
        
        print("🔐 Forsøger at forbinde...")
        success = client.authenticate()
        
        if success:
            print("✅ SUCCES! Forbindelse til Axiell API virker!")
            
            # Test search
            print("🔍 Tester søgning...")
            results = client.search_objects("test")
            print(f"✅ Søgning virker - fandt {len(results)} resultater")
            
        else:
            print("❌ FEJL! Kunne ikke forbinde til Axiell API")
            print("Tjek dine oplysninger i .env filen")
            
    except Exception as e:
        print(f"❌ Fejl: {e}")

if __name__ == "__main__":
    test_connection()
    input("\nTryk Enter for at lukke...")