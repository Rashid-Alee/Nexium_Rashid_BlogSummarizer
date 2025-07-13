# debug_imports.py - Debug import and setup issues
# Save this in your backend/ folder and run it first

import sys
import os

print("🔍 DEBUGGING IMPORTS AND SETUP")
print("=" * 50)

# Check Python version
print(f"📍 Python Version: {sys.version}")
print(f"📁 Current Directory: {os.getcwd()}")

# Check if we're in the right directory
expected_files = ['test_complete_service.py', '.env', 'requirements.txt']
print(f"\n📋 Checking for required files:")
for file in expected_files:
    exists = os.path.exists(file)
    print(f"   {'✅' if exists else '❌'} {file}")

# Check database folder
print(f"\n📁 Checking database folder:")
database_exists = os.path.exists('database')
print(f"   {'✅' if database_exists else '❌'} database/ folder")

if database_exists:
    database_files = ['__init__.py', 'supabase_client.py', 'mongodb_client.py', 'database_service.py']
    for file in database_files:
        file_path = os.path.join('database', file)
        exists = os.path.exists(file_path)
        print(f"   {'✅' if exists else '❌'} database/{file}")

# Test environment variables
print(f"\n🔐 Testing Environment Variables:")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    mongodb_uri = os.getenv("MONGODB_URI")
    
    print(f"   {'✅' if supabase_url else '❌'} SUPABASE_URL: {'Set' if supabase_url else 'Missing'}")
    print(f"   {'✅' if mongodb_uri else '❌'} MONGODB_URI: {'Set' if mongodb_uri else 'Missing'}")
    
except ImportError as e:
    print(f"   ❌ Failed to load dotenv: {e}")

# Test basic imports
print(f"\n📦 Testing Package Imports:")

packages_to_test = [
    ('dotenv', 'python-dotenv'),
    ('supabase', 'supabase'),
    ('pymongo', 'pymongo'),
    ('asyncio', 'built-in')
]

for package_name, install_name in packages_to_test:
    try:
        __import__(package_name)
        print(f"   ✅ {package_name}: Available")
    except ImportError as e:
        print(f"   ❌ {package_name}: Missing - Run 'pip install {install_name}'")

# Test database folder import
print(f"\n🗄️ Testing Database Module Import:")
try:
    # Add current directory to Python path
    sys.path.insert(0, os.getcwd())
    
    # Try importing database module
    import database
    print("   ✅ database module: Imported successfully")
    
    # Try importing individual clients
    try:
        from database.supabase_client import supabase_client
        print("   ✅ supabase_client: Imported successfully")
    except Exception as e:
        print(f"   ❌ supabase_client: {e}")
    
    try:
        from database.mongodb_client import mongodb_client
        print("   ✅ mongodb_client: Imported successfully")
    except Exception as e:
        print(f"   ❌ mongodb_client: {e}")
    
    try:
        from database.database_service import db_service
        print("   ✅ database_service: Imported successfully")
    except Exception as e:
        print(f"   ❌ database_service: {e}")
        
except Exception as e:
    print(f"   ❌ database module import failed: {e}")

# Test async functionality
print(f"\n⚡ Testing Async Functionality:")
try:
    import asyncio
    
    async def test_async():
        return "✅ Async working"
    
    result = asyncio.run(test_async())
    print(f"   {result}")
    
except Exception as e:
    print(f"   ❌ Async test failed: {e}")

print(f"\n🎯 NEXT STEPS:")
print("1. Fix any ❌ issues shown above")
print("2. Make sure all required files exist")
print("3. Install missing packages with pip")
print("4. Then try running the complete test again")

print(f"\n💡 IF ALL ✅ ABOVE:")
print("The issue might be in the test_complete_service.py file itself")
print("Let's create a simpler version to test step by step")