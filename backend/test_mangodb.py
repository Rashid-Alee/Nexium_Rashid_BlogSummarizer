# test_mongodb.py - Fixed version without incompatible SSL parameters

import os
from dotenv import load_dotenv
from pymongo import MongoClient

def test_mongodb():
    """Test MongoDB connection with compatible parameters"""
    
    print("🔍 Testing MongoDB Connection...")
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Get MongoDB URI
        mongodb_uri = os.getenv('MONGODB_URI')
        
        if not mongodb_uri:
            print("❌ MONGODB_URI not found in environment")
            return
        
        print("✅ MONGODB_URI found")
        print(f"   URI starts with: {mongodb_uri[:30]}...")
        
        # Create client (let the URI handle SSL settings)
        print("📡 Connecting to MongoDB...")
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # Test ping
        print("🏓 Testing ping...")
        client.admin.command('ping')
        print("✅ MongoDB ping successful")
        
        # Get database
        print("📊 Accessing database...")
        db = client['nexium-blog-cluster']
        print(f"✅ Database access successful: nexium-blog-cluster")
        
        # Check blog_contents collection
        print("📄 Checking blog_contents collection...")
        collections = db.list_collection_names()
        
        if 'blog_contents' in collections:
            count = db.blog_contents.count_documents({})
            print(f"✅ Found {count} documents in blog_contents collection")
            
            # List some documents
            if count > 0:
                print("📝 Sample documents:")
                docs = db.blog_contents.find().limit(3)
                for i, doc in enumerate(docs, 1):
                    print(f"   {i}. URL: {doc.get('url', 'No URL')[:50]}...")
                    print(f"      Title: {doc.get('title', 'No title')[:40]}...")
            else:
                print("📝 No documents found in collection")
        else:
            print("📄 blog_contents collection not found (will be created on first save)")
        
        # Test write operation
        print("\n🧪 Testing write operation...")
        test_collection = db.test_connection
        
        test_doc = {
            "url": "https://test-connection.com",
            "title": "Connection Test Document",
            "content": "This is a test document",
            "created_at": "2025-07-13"
        }
        
        # Try to insert
        result = test_collection.insert_one(test_doc)
        print(f"✅ Write test successful: {result.inserted_id}")
        
        # Clean up test document
        test_collection.delete_one({"_id": result.inserted_id})
        print("🧹 Test document cleaned up")
        
        client.close()
        print("\n🎉 MongoDB is working perfectly!")
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        print("\n💡 This explains why your data isn't saving to MongoDB!")

if __name__ == "__main__":
    test_mongodb()