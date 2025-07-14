"""
PRODUCTION-READY FastAPI Application
Assignment 2: Blog Summarizer with Dual Database Storage
Fixed for Render deployment
"""

import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
import time

# PRODUCTION FIX: Simplified path handling
# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# PRODUCTION FIX: Environment variable loading
from dotenv import load_dotenv
# Try to load .env from current directory first, then parent
if os.path.exists('.env'):
    load_dotenv('.env')
else:
    load_dotenv()

# Import your modules (ensure these files are in the same directory as main.py)
try:
    from scraper import scrape_blog
    from database.database_service import db_service
    print("✅ Successfully imported all modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    # For deployment debugging
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in directory: {os.listdir('.')}")

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app with production settings
app = FastAPI(
    title="AI-Powered Blog Scraper & Summarizer v2.0",
    description="Advanced blog analysis with dual database storage (Supabase + MongoDB)",
    version="2.0.0",
    # PRODUCTION FIX: Enable docs for debugging (disable later if needed)
    docs_url="/docs", 
    redoc_url="/redoc", 
    openapi_url="/openapi.json"
)

# PRODUCTION FIX: Dynamic CORS configuration
def get_cors_origins():
    """Get CORS origins based on environment"""
    # Get environment variable for frontend URL
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        frontend_url,  # This will be your Vercel domain
    ]
    
    # Add production domains
    if "vercel.app" in frontend_url:
        origins.append(frontend_url)
    
    return origins

# Enable CORS with dynamic origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Enhanced root endpoint with database status and features"""
    try:
        # Test database connections
        db_status = await db_service.test_all_connections()
        
        # Get database statistics
        try:
            stats = await db_service.get_database_statistics()
            total_processed = stats.get("total_processed", 0)
        except:
            total_processed = 0
        
        return {
            "message": "🚀 AI-Powered Blog Scraper API v2.0 - Assignment 2",
            "project": "Blog Summarizer with Dual Database Storage",
            "student": "Nexium Bootcamp - Assignment 2",
            "status": "🟢 Active",
            "environment": "production" if os.getenv("RENDER") else "development",
            "databases": {
                "supabase": "✅ Connected" if db_status.get("supabase", {}).get("success") else "❌ Failed",
                "mongodb": "✅ Connected" if db_status.get("mongodb", {}).get("success") else "❌ Failed",
                "overall": "✅ All systems operational" if db_status.get("overall_success") else "⚠️ Some systems down"
            },
            "features": {
                "web_scraping": "✅ Advanced content extraction",
                "ai_summarization": "✅ Multi-sentence intelligent summarization",
                "urdu_translation": "✅ English to Urdu translation",
                "database_storage": "✅ Dual database architecture",
                "data_persistence": "✅ Supabase (summaries) + MongoDB (full content)",
                "duplicate_prevention": "✅ Smart URL checking",
                "instant_retrieval": "✅ Cached results for processed URLs"
            },
            "statistics": {
                "total_articles_processed": total_processed,
                "database_architecture": "Dual (SQL + NoSQL)",
                "performance": "Concurrent database operations"
            },
            "endpoints": {
                "health": "/health - System health check",
                "scrape": "/scrape (POST) - Main blog analysis endpoint",
                "retrieve": "/blog/{url:path} (GET) - Get existing analysis",
                "recent": "/recent?limit=10 (GET) - Recent summaries",
                "statistics": "/stats (GET) - Database statistics",
                "test_db": "/test-db (GET) - Database connection test"
            },
            "assignment_requirements": {
                "blog_scraping": "✅ Complete",
                "ai_summarization": "✅ Complete", 
                "urdu_translation": "✅ Complete",
                "supabase_storage": "✅ Complete",
                "mongodb_storage": "✅ Complete",
                "vercel_deployment": "🔄 Ready for deployment"
            }
        }
    except Exception as e:
        logger.error(f"Error in root endpoint: {e}")
        return {
            "message": "API running with limited functionality",
            "error": str(e),
            "status": "⚠️ Degraded"
        }

@app.get("/health")
async def health():
    """Comprehensive health check with database connectivity"""
    try:
        start_time = time.time()
        
        # Test database connections
        db_status = await db_service.test_all_connections()
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "healthy" if db_status.get("overall_success") else "degraded",
            "service": "ai-blog-scraper-v2",
            "environment": os.getenv("RENDER", "local"),
            "databases": {
                "supabase": db_status.get("supabase", {}),
                "mongodb": db_status.get("mongodb", {}),
                "overall_status": "✅ All connected" if db_status.get("overall_success") else "⚠️ Issues detected"
            },
            "response_time_ms": response_time,
            "timestamp": "2025-07-13",
            "version": "2.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-07-13"
        }

@app.post("/scrape")
async def scrape_and_save(request: dict):
    """
    🚀 MAIN ENDPOINT: Enhanced scrape with intelligent database integration
    
    Flow:
    1. Check if URL already processed (instant return)
    2. If new: Scrape → Summarize → Translate → Save to both databases
    3. Return comprehensive analysis
    """
    try:
        url = request.get("url")
        
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        logger.info(f"🔍 Processing URL: {url}")
        
        # Step 1: Check if URL already exists in databases
        start_time = time.time()
        url_exists = await db_service.check_url_exists(url)
        check_time = round((time.time() - start_time) * 1000, 2)
        
        if url_exists["complete_record"]:
            logger.info(f"⚡ Cache hit for URL: {url}")
            
            # Get existing data from databases
            existing_data = await db_service.get_blog_by_url(url)
            
            return {
                "success": True,
                "cached": True,
                "data": existing_data["summary"] if existing_data["summary"] else existing_data["content"],
                "message": "✅ Data retrieved from cache",
                "performance": {
                    "cache_check_time_ms": check_time,
                    "total_time_ms": check_time,
                    "cache_hit": True
                },
                "database": {
                    "supabase_exists": url_exists["exists_in_supabase"],
                    "mongodb_exists": url_exists["exists_in_mongodb"],
                    "complete_record": True
                }
            }
        
        # Step 2: Process new URL
        logger.info(f"🚀 New URL detected, starting full processing...")
        
        # Scrape the blog
        scraping_start = time.time()
        scraping_result = scrape_blog(url)
        scraping_time = round((time.time() - scraping_start) * 1000, 2)
        
        if not scraping_result.get("success"):
            raise HTTPException(
                status_code=400, 
                detail=f"Scraping failed: {scraping_result.get('error', 'Unknown error')}"
            )
        
        # Step 3: Save to both databases
        save_start = time.time()
        save_result = await db_service.save_blog_analysis(scraping_result)
        save_time = round((time.time() - save_start) * 1000, 2)
        
        total_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "success": True,
            "cached": False,
            "data": scraping_result,
            "message": "✅ Blog processed and saved successfully",
            "performance": {
                "cache_check_time_ms": check_time,
                "scraping_time_ms": scraping_time,
                "database_save_time_ms": save_time,
                "total_time_ms": total_time
            },
            "database": {
                "supabase": save_result.get("supabase", {}),
                "mongodb": save_result.get("mongodb", {}),
                "overall_success": save_result.get("overall_success", False)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in scrape endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Additional endpoints (keeping existing ones)...

@app.get("/recent")
async def get_recent_summaries(limit: int = 10):
    """Get recent blog summaries with pagination"""
    try:
        if limit > 50:  # Prevent excessive queries
            limit = 50
            
        recent_data = await db_service.get_recent_activity(limit)
        
        return {
            "success": True,
            "data": {
                "summaries": recent_data["summaries"],
                "count": recent_data["count"]["summaries"],
                "limit": limit
            },
            "message": f"✅ Retrieved {len(recent_data['summaries'])} recent summaries"
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting recent summaries: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/stats")
async def get_database_statistics():
    """Get comprehensive database statistics"""
    try:
        stats = await db_service.get_database_statistics()
        
        return {
            "success": True,
            "statistics": stats,
            "message": "✅ Database statistics retrieved"
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting statistics: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# PRODUCTION FIX: Proper application startup for Render
if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable (Render provides this)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)