# test_supabase.py - Save this in your backend/ folder
# This script tests your Supabase connection

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_supabase_connection():
    """Test connection to Supabase and understand how it works"""
    
    print("🧪 Testing Supabase Connection...")
    print("=" * 50)
    
    # Step 1: Check if environment variables are loaded
    print("📋 Step 1: Checking Environment Variables")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url:
        print("❌ SUPABASE_URL not found in .env file")
        return False
    
    if not supabase_key:
        print("❌ SUPABASE_KEY not found in .env file")
        return False
    
    print(f"✅ SUPABASE_URL: {supabase_url}")
    print(f"✅ SUPABASE_KEY: {supabase_key[:20]}..." + "*" * 20)
    
    # Step 2: Try to import Supabase client
    print("\n📦 Step 2: Testing Supabase Package Import")
    
    try:
        from supabase import create_client, Client
        print("✅ Supabase package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Supabase: {e}")
        print("💡 Solution: Run 'pip install supabase' in your backend folder")
        return False
    
    # Step 3: Create Supabase client
    print("\n🔗 Step 3: Creating Supabase Client")
    
    try:
        supabase_client: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return False
    
    # Step 4: Test basic connection (try to access auth)
    print("\n🌐 Step 4: Testing Connection to Supabase")
    
    try:
        # Try a simple operation to test connectivity
        response = supabase_client.auth.get_session()
        print("✅ Successfully connected to Supabase!")
        print("🎉 Your database is ready to use!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("💡 Check your internet connection and credentials")
        return False

def show_next_steps():
    """Show what to do next"""
    print("\n" + "=" * 50)
    print("🎯 NEXT STEPS:")
    print("1. ✅ Supabase connection working!")
    print("2. 📊 Next: Create your first database table")
    print("3. 🍃 After that: Set up MongoDB")
    print("4. 🔗 Finally: Connect both databases to your blog summarizer")
    print("\n🎓 WHAT YOU'VE LEARNED:")
    print("- How to store credentials securely in .env files")
    print("- How to connect Python applications to cloud databases")
    print("- How to test database connections before writing complex code")

if __name__ == "__main__":
    # Run the test
    success = test_supabase_connection()
    
    if success:
        show_next_steps()
    else:
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check your .env file has the correct Supabase credentials")
        print("2. Make sure you're in the backend/ folder when running this")
        print("3. Install Supabase: pip install supabase")
        print("4. Check your internet connection")