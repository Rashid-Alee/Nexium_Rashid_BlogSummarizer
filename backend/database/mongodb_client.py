import os
from typing import Dict, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

class MongoDBClient:
    """
    Professional MongoDB client with connection pooling and error handling
    Manages flexible blog content documents
    """
    
    def __init__(self):
        """Initialize MongoDB client with environment variables"""
        try:
            self.uri = os.getenv("MONGODB_URI")
            self.database_name = os.getenv("MONGODB_DATABASE", "nexium_blog_db")
            
            if not self.uri:
                raise ValueError("Missing MONGODB_URI environment variable")
            
            # Create client with connection pooling for better performance
            self.client = MongoClient(
                self.uri,
                maxPoolSize=10,          # Max 10 connections
                minPoolSize=1,           # Min 1 connection
                maxIdleTimeMS=30000,     # Close idle connections after 30s
                serverSelectionTimeoutMS=5000,  # 5s timeout for server selection
                connectTimeoutMS=10000,  # 10s timeout for initial connection
                socketTimeoutMS=20000    # 20s timeout for socket operations
            )
            
            # Get database and collection
            self.db = self.client[self.database_name]
            self.blog_contents = self.db.blog_contents
            
            # Create indexes for better performance
            self._create_indexes()
            
            logger.info("✅ MongoDB client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MongoDB: {e}")
            raise

    def _create_indexes(self):
        """Create database indexes for better query performance"""
        try:
            # Create unique index on URL to prevent duplicates
            self.blog_contents.create_index("url", unique=True)
            
            # Create index on scraped_at for time-based queries
            self.blog_contents.create_index("metadata.scraped_at")
            
            # Create text index for full-text search capability
            self.blog_contents.create_index([
                ("title", "text"), 
                ("full_content", "text")
            ])
            
            logger.info("✅ MongoDB indexes created successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Index creation warning: {e}")

    async def save_blog_content(self, content_data: Dict) -> Dict:
        """
        Save full blog content to MongoDB
        
        Args:
            content_data (Dict): Complete blog data including full text
            
        Returns:
            Dict: Success/failure result with details
        """
        try:
            # Prepare document structure for MongoDB
            document = {
                "url": content_data.get("url"),
                "title": content_data.get("title"),
                "full_content": content_data.get("content"),  # Full article text
                "metadata": {
                    "author": content_data.get("metadata", {}).get("author"),
                    "published_date": content_data.get("metadata", {}).get("published_date"),
                    "scraped_at": datetime.utcnow(),
                    "content_length": len(content_data.get("content", "")),
                    "word_count": content_data.get("word_count", 0),
                    "paragraph_count": content_data.get("paragraph_count", 0),
                    "char_count": content_data.get("char_count", 0)
                },
                "scraping_stats": {
                    "response_time": content_data.get("response_time"),
                    "status_code": 200,
                    "method_used": "advanced_extraction",
                    "scraper_version": "2.0"
                },
                "processing_info": {
                    "summary_generated": bool(content_data.get("ai_summary")),
                    "translation_completed": bool(content_data.get("ai_summary_urdu")),
                    "saved_to_supabase": False  # Will be updated after Supabase save
                },
                "ai_analysis": {
                    "summary": content_data.get("ai_summary"),
                    "summary_urdu": content_data.get("ai_summary_urdu"),
                    "summary_stats": content_data.get("summary_stats", {}),
                    "translation_stats": content_data.get("translation_stats", {})
                }
            }
            
            logger.info(f"💾 Saving blog content for URL: {document.get('url', 'Unknown')}")
            
            # Use upsert to update existing documents or create new ones
            result = self.blog_contents.replace_one(
                {"url": document["url"]},  # Filter by URL
                document,                  # Replacement document
                upsert=True               # Create if doesn't exist
            )
            
            # Determine what action was taken
            if result.upserted_id:
                action = "created"
                record_id = str(result.upserted_id)
            elif result.modified_count > 0:
                action = "updated"
                # Get the existing document ID
                existing = self.blog_contents.find_one({"url": document["url"]})
                record_id = str(existing["_id"]) if existing else "unknown"
            else:
                action = "no_change"
                record_id = None
            
            logger.info(f"✅ Blog content {action}: {record_id}")
            
            return {
                "success": True,
                "action": action,
                "record_id": record_id,
                "url": document["url"],
                "message": f"Blog content {action} in MongoDB"
            }
            
        except DuplicateKeyError:
            logger.warning(f"⚠️ Duplicate URL detected: {content_data.get('url')}")
            return {
                "success": False,
                "error": "Duplicate URL",
                "url": content_data.get("url"),
                "message": "URL already exists in MongoDB"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to save blog content: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": content_data.get("url", "Unknown"),
                "message": f"Failed to save to MongoDB: {e}"
            }

    async def get_blog_content_by_url(self, url: str) -> Optional[Dict]:
        """
        Retrieve full blog content by URL
        
        Args:
            url (str): Blog URL to search for
            
        Returns:
            Optional[Dict]: Blog content if found, None otherwise
        """
        try:
            document = self.blog_contents.find_one({"url": url})
            
            if document:
                # Convert ObjectId to string for JSON serialization
                document["_id"] = str(document["_id"])
                logger.info(f"✅ Found blog content for URL: {url}")
                return document
            else:
                logger.info(f"ℹ️ No blog content found for URL: {url}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error retrieving blog content: {e}")
            return None

    async def update_processing_status(self, url: str, status_updates: Dict) -> Dict:
        """
        Update processing status for a blog document
        
        Args:
            url (str): Blog URL to update
            status_updates (Dict): Status fields to update
            
        Returns:
            Dict: Update result
        """
        try:
            result = self.blog_contents.update_one(
                {"url": url},
                {"$set": {f"processing_info.{k}": v for k, v in status_updates.items()}}
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Updated processing status for URL: {url}")
                return {"success": True, "modified": True}
            else:
                logger.warning(f"⚠️ No document updated for URL: {url}")
                return {"success": True, "modified": False}
                
        except Exception as e:
            logger.error(f"❌ Error updating processing status: {e}")
            return {"success": False, "error": str(e)}

    async def get_recent_blogs(self, limit: int = 10) -> List[Dict]:
        """
        Get recently scraped blogs
        
        Args:
            limit (int): Number of blogs to retrieve
            
        Returns:
            List[Dict]: List of recent blog documents
        """
        try:
            cursor = self.blog_contents.find().sort("metadata.scraped_at", -1).limit(limit)
            blogs = list(cursor)
            
            # Convert ObjectIds to strings for JSON serialization
            for blog in blogs:
                blog["_id"] = str(blog["_id"])
            
            logger.info(f"✅ Retrieved {len(blogs)} recent blogs")
            return blogs
            
        except Exception as e:
            logger.error(f"❌ Error retrieving recent blogs: {e}")
            return []

    def test_connection(self) -> Dict:
        """
        Test MongoDB connection and database access
        
        Returns:
            Dict: Connection test results
        """
        try:
            # Test connection
            self.client.admin.command('ping')
            
            # Test database access
            collection_count = len(self.db.list_collection_names())
            document_count = self.blog_contents.count_documents({})
            
            return {
                "success": True,
                "message": "MongoDB connection successful",
                "database": self.database_name,
                "collections": collection_count,
                "blog_documents": document_count
            }
            
        except ConnectionFailure as e:
            return {
                "success": False,
                "message": f"MongoDB connection failed: {e}",
                "database": self.database_name
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"MongoDB error: {e}",
                "database": self.database_name
            }

    async def check_url_exists(self, url: str) -> bool:
        """
        Quick check if URL already exists in database
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if URL exists, False otherwise
        """
        try:
            count = self.blog_contents.count_documents({"url": url})
            return count > 0
        except Exception as e:
            logger.error(f"❌ Error checking URL existence: {e}")
            return False

# Create global instance for easy importing
mongodb_client = MongoDBClient()