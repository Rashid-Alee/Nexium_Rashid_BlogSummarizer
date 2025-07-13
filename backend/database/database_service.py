"""
Database Service Layer
Smart coordinator that orchestrates operations between Supabase and MongoDB
"""

import asyncio
from typing import Dict, Tuple
import logging
from .supabase_client import supabase_client
from .mongodb_client import mongodb_client

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    High-level database service that coordinates between Supabase and MongoDB
    This is the main interface your blog scraper will use
    """
    
    def __init__(self):
        self.supabase = supabase_client
        self.mongodb = mongodb_client

    async def save_blog_analysis(self, analysis_data: Dict) -> Dict:
        """
        Save complete blog analysis to both databases
        This is the main method your scraper will call
        
        Args:
            analysis_data (Dict): Complete analysis including summary and full content
            
        Returns:
            Dict: Combined save results from both databases
        """
        try:
            url = analysis_data.get("url")
            logger.info(f"🚀 Starting database save process for URL: {url}")
            
            # Save to both databases concurrently for better performance
            logger.info("💾 Saving to both databases simultaneously...")
            
            # Create tasks for both database operations
            supabase_task = self.supabase.save_summary(analysis_data)
            mongodb_task = self.mongodb.save_blog_content(analysis_data)
            
            # Wait for both operations to complete
            supabase_result, mongodb_result = await asyncio.gather(
                supabase_task, 
                mongodb_task,
                return_exceptions=True
            )
            
            # Handle results and exceptions
            results = {
                "url": url,
                "supabase": supabase_result if not isinstance(supabase_result, Exception) else {
                    "success": False, 
                    "error": str(supabase_result)
                },
                "mongodb": mongodb_result if not isinstance(mongodb_result, Exception) else {
                    "success": False, 
                    "error": str(mongodb_result)
                },
                "overall_success": False
            }
            
            # Determine overall success
            supabase_success = results["supabase"].get("success", False)
            mongodb_success = results["mongodb"].get("success", False)
            
            if supabase_success and mongodb_success:
                results["overall_success"] = True
                results["message"] = "✅ Successfully saved to both databases"
                logger.info(f"✅ Complete save success for URL: {url}")
                
                # Update MongoDB to indicate Supabase save was successful
                await self.mongodb.update_processing_status(url, {"saved_to_supabase": True})
                
            elif supabase_success or mongodb_success:
                results["overall_success"] = False
                results["message"] = "⚠️ Partially saved (one database failed)"
                logger.warning(f"⚠️ Partial save for URL: {url}")
                
                # Provide specific guidance on what failed
                if not supabase_success:
                    results["message"] += " - Summary save failed"
                if not mongodb_success:
                    results["message"] += " - Content save failed"
                
            else:
                results["message"] = "❌ Failed to save to both databases"
                logger.error(f"❌ Complete save failure for URL: {url}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Database service error: {e}")
            return {
                "url": analysis_data.get("url", "Unknown"),
                "overall_success": False,
                "error": str(e),
                "message": f"❌ Service error: {e}"
            }

    async def get_blog_by_url(self, url: str) -> Dict:
        """
        Retrieve blog data from both databases
        
        Args:
            url (str): Blog URL to retrieve
            
        Returns:
            Dict: Combined data from both databases
        """
        try:
            logger.info(f"🔍 Retrieving blog data for URL: {url}")
            
            # Get data from both databases concurrently
            summary_task = self.supabase.get_summary_by_url(url)
            content_task = self.mongodb.get_blog_content_by_url(url)
            
            summary_data, content_data = await asyncio.gather(
                summary_task, 
                content_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(summary_data, Exception):
                logger.error(f"❌ Error getting summary: {summary_data}")
                summary_data = None
                
            if isinstance(content_data, Exception):
                logger.error(f"❌ Error getting content: {content_data}")
                content_data = None
            
            return {
                "url": url,
                "found": bool(summary_data or content_data),
                "summary": summary_data,
                "content": content_data,
                "complete": bool(summary_data and content_data),
                "message": "✅ Data retrieved successfully" if (summary_data or content_data) else "ℹ️ No data found"
            }
            
        except Exception as e:
            logger.error(f"❌ Error retrieving blog data: {e}")
            return {
                "url": url,
                "found": False,
                "error": str(e),
                "message": f"❌ Retrieval error: {e}"
            }

    async def check_url_exists(self, url: str) -> Dict:
        """
        Check if URL exists in either database (fast check before scraping)
        
        Args:
            url (str): URL to check
            
        Returns:
            Dict: Existence status in both databases
        """
        try:
            # Check both databases concurrently
            supabase_task = self.supabase.check_url_exists(url)
            mongodb_task = self.mongodb.check_url_exists(url)
            
            supabase_exists, mongodb_exists = await asyncio.gather(
                supabase_task,
                mongodb_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(supabase_exists, Exception):
                supabase_exists = False
            if isinstance(mongodb_exists, Exception):
                mongodb_exists = False
            
            return {
                "url": url,
                "exists_in_supabase": supabase_exists,
                "exists_in_mongodb": mongodb_exists,
                "exists_anywhere": supabase_exists or mongodb_exists,
                "complete_record": supabase_exists and mongodb_exists
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking URL existence: {e}")
            return {
                "url": url,
                "exists_anywhere": False,
                "error": str(e)
            }

    async def get_recent_activity(self, limit: int = 10) -> Dict:
        """
        Get recent activity from both databases
        
        Args:
            limit (int): Number of recent items to retrieve
            
        Returns:
            Dict: Recent summaries and content from both databases
        """
        try:
            # Get recent data from both databases
            summaries_task = self.supabase.get_recent_summaries(limit)
            blogs_task = self.mongodb.get_recent_blogs(limit)
            
            recent_summaries, recent_blogs = await asyncio.gather(
                summaries_task,
                blogs_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(recent_summaries, Exception):
                recent_summaries = []
            if isinstance(recent_blogs, Exception):
                recent_blogs = []
            
            return {
                "summaries": recent_summaries,
                "blogs": recent_blogs,
                "count": {
                    "summaries": len(recent_summaries),
                    "blogs": len(recent_blogs)
                },
                "message": f"✅ Retrieved recent activity"
            }
            
        except Exception as e:
            logger.error(f"❌ Error retrieving recent activity: {e}")
            return {
                "summaries": [],
                "blogs": [],
                "error": str(e)
            }

    async def test_all_connections(self) -> Dict:
        """
        Test connections to both databases
        
        Returns:
            Dict: Connection test results for both databases
        """
        try:
            logger.info("🧪 Testing all database connections...")
            
            # Test both connections
            supabase_test = self.supabase.test_connection()
            mongodb_test = self.mongodb.test_connection()
            
            overall_status = supabase_test.get("success", False) and mongodb_test.get("success", False)
            
            return {
                "overall_success": overall_status,
                "supabase": supabase_test,
                "mongodb": mongodb_test,
                "message": "✅ All databases connected" if overall_status else "❌ Some database connections failed"
            }
            
        except Exception as e:
            return {
                "overall_success": False,
                "error": str(e),
                "message": f"❌ Connection test failed: {e}"
            }

    async def get_database_statistics(self) -> Dict:
        """
        Get statistics from both databases
        
        Returns:
            Dict: Combined statistics from both databases
        """
        try:
            # Get stats from both databases
            recent_summaries = await self.supabase.get_recent_summaries(1000)  # Get all for count
            recent_blogs = await self.mongodb.get_recent_blogs(1000)  # Get all for count
            
            return {
                "supabase_summaries": len(recent_summaries),
                "mongodb_documents": len(recent_blogs),
                "total_processed": max(len(recent_summaries), len(recent_blogs)),
                "data_consistency": len(recent_summaries) == len(recent_blogs),
                "message": "✅ Database statistics retrieved"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting database statistics: {e}")
            return {
                "error": str(e),
                "message": f"❌ Statistics error: {e}"
            }

# Create global instance for easy importing
db_service = DatabaseService()