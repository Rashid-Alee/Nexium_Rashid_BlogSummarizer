"""
Supabase PostgreSQL Client
Professional client for managing blog summaries in structured format
"""

import os
from typing import Dict, List, Optional
from supabase import create_client, Client
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseClient:
    """
    Professional Supabase client with error handling and best practices
    Manages structured blog summary data in PostgreSQL
    """
    
    def __init__(self):
        """Initialize Supabase client with environment variables"""
        try:
            self.url = os.getenv("SUPABASE_URL")
            self.key = os.getenv("SUPABASE_KEY")
            
            if not self.url or not self.key:
                raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
            
            self.client: Client = create_client(self.url, self.key)
            logger.info("✅ Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase: {e}")
            raise

    async def save_summary(self, summary_data: Dict) -> Dict:
        """
        Save blog summary to Supabase with comprehensive error handling
        
        Args:
            summary_data (Dict): Contains url, title, summary, etc.
            
        Returns:
            Dict: Success/failure result with details
        """
        try:
            # Prepare data for insertion
            insert_data = {
                "url": summary_data.get("url"),
                "title": summary_data.get("title"),
                "title_urdu": summary_data.get("title_urdu"),
                "summary": summary_data.get("ai_summary"),  # Note: mapping from ai_summary
                "summary_urdu": summary_data.get("ai_summary_urdu"),
                "word_count": summary_data.get("word_count", 0)
            }
            
            # Remove None values to keep data clean
            insert_data = {k: v for k, v in insert_data.items() if v is not None}
            
            logger.info(f"💾 Saving summary for URL: {insert_data.get('url', 'Unknown')}")
            
            # Insert or update (upsert) based on URL
            result = self.client.table('blog_summaries').upsert(
                insert_data,
                on_conflict='url'  # Update if URL already exists
            ).execute()
            
            if result.data:
                logger.info(f"✅ Summary saved successfully: ID {result.data[0].get('id')}")
                return {
                    "success": True,
                    "action": "saved",
                    "record_id": result.data[0].get('id'),
                    "url": insert_data.get('url'),
                    "message": "Summary saved to Supabase"
                }
            else:
                logger.warning("⚠️ No data returned from Supabase")
                return {
                    "success": False, 
                    "error": "No data returned",
                    "url": insert_data.get('url')
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to save summary: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": summary_data.get("url", "Unknown"),
                "message": f"Failed to save summary: {e}"
            }

    async def get_summary_by_url(self, url: str) -> Optional[Dict]:
        """
        Retrieve existing summary by URL
        
        Args:
            url (str): Blog URL to search for
            
        Returns:
            Optional[Dict]: Summary data if found, None otherwise
        """
        try:
            result = self.client.table('blog_summaries').select('*').eq('url', url).execute()
            
            if result.data:
                logger.info(f"✅ Found existing summary for URL: {url}")
                return result.data[0]
            else:
                logger.info(f"ℹ️ No existing summary found for URL: {url}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error retrieving summary: {e}")
            return None

    async def get_recent_summaries(self, limit: int = 10) -> List[Dict]:
        """
        Get recently created summaries
        
        Args:
            limit (int): Number of summaries to retrieve
            
        Returns:
            List[Dict]: List of recent summaries
        """
        try:
            result = self.client.table('blog_summaries').select('*')\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            logger.info(f"✅ Retrieved {len(result.data)} recent summaries")
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Error retrieving recent summaries: {e}")
            return []

    def test_connection(self) -> Dict:
        """
        Test Supabase connection and permissions
        
        Returns:
            Dict: Connection test results
        """
        try:
            # Try to select from blog_summaries table
            result = self.client.table('blog_summaries').select('count').execute()
            
            return {
                "success": True,
                "message": "Supabase connection successful",
                "table_accessible": True,
                "total_records": len(result.data) if result.data else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Supabase connection failed: {e}",
                "table_accessible": False
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
            result = self.client.table('blog_summaries').select('id').eq('url', url).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"❌ Error checking URL existence: {e}")
            return False

# Create global instance for easy importing
supabase_client = SupabaseClient()