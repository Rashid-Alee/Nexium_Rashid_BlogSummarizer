"""
Enhanced FastAPI main application with database integration
Assignment 2: Blog Summarizer with Dual Database Storage
"""

import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
import time

# IMPORTANT: Add backend directory to Python path to access database module
# This allows importing from database/ folder which is at backend level
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from backend/.env (parent directory)
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Now import your modules
from scraper import scrape_blog  # This is in the same app/ folder
from database.database_service import db_service  # This is in backend/database/

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI-Powered Blog Scraper & Summarizer v2.0",
    description="Advanced blog analysis with dual database storage (Supabase + MongoDB)",
    version="2.0.0",
    docs_url=None, 
    redoc_url=None, 
    openapi_url=None
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://your-vercel-domain.vercel.app"],
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
    
    Request: {"url": "https://example.com/article"}
    Response: Complete analysis + database save status + performance metrics
    """
    start_time = time.time()
    
    try:
        # Get URL from request
        url = request.get("url")
        
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        logger.info(f"🔍 Processing request for URL: {url}")
        
        # STEP 1: Smart duplicate checking
        logger.info("🔍 Checking if URL already processed...")
        existence_check = await db_service.check_url_exists(url)
        
        if existence_check.get("complete_record"):
            # URL already fully processed - return existing data instantly
            logger.info(f"⚡ Found existing complete analysis for: {url}")
            
            retrieval_result = await db_service.get_blog_by_url(url)
            
            response_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                "success": True,
                "cached": True,
                "message": "✅ Returning existing analysis from database (instant result)",
                "data": {
                    "url": url,
                    "title": retrieval_result["summary"]["title"],
                    "title_urdu": retrieval_result["summary"]["title_urdu"],
                    "ai_summary": retrieval_result["summary"]["summary"],
                    "ai_summary_urdu": retrieval_result["summary"]["summary_urdu"],
                    "word_count": retrieval_result["summary"]["word_count"],
                    "created_at": retrieval_result["summary"]["created_at"],
                    "content_available": bool(retrieval_result["content"])
                },
                "performance": {
                    "response_time_ms": response_time,
                    "cache_hit": True,
                    "database_query_only": True
                },
                "database_status": "✅ Retrieved from cache"
            }
        
        # STEP 2: New URL - perform complete analysis
        logger.info(f"📡 New URL detected - starting complete analysis...")
        
        # Run scraping and summarization
        scrape_start = time.time()
        scrape_result = scrape_blog(url)
        scrape_time = round((time.time() - scrape_start) * 1000, 2)
        
        if not scrape_result.get("success"):
            logger.error(f"❌ Scraping failed: {scrape_result.get('error')}")
            return {
                "success": False,
                "cached": False,
                "error": scrape_result.get("error"),
                "message": "❌ Failed to scrape and analyze the article",
                "url": url
            }
        
        # STEP 3: Save to both databases concurrently
        logger.info(f"💾 Saving analysis to dual database system...")
        db_start = time.time()
        save_result = await db_service.save_blog_analysis(scrape_result)
        db_save_time = round((time.time() - db_start) * 1000, 2)
        
        # STEP 4: Prepare comprehensive response
        total_time = round((time.time() - start_time) * 1000, 2)
        
        response = {
            "success": True,
            "cached": False,
            "message": save_result["message"],
            "data": {
                "url": url,
                "title": scrape_result.get("title"),
                "title_urdu": scrape_result.get("title_urdu"),
                "ai_summary": scrape_result.get("ai_summary"),
                "ai_summary_urdu": scrape_result.get("ai_summary_urdu"),
                "word_count": scrape_result.get("word_count"),
                "summary_stats": scrape_result.get("summary_stats"),
                "translation_stats": scrape_result.get("translation_stats"),
                "metadata": scrape_result.get("metadata", {})
            },
            "database": {
                "supabase": save_result["supabase"],
                "mongodb": save_result["mongodb"],
                "overall_success": save_result["overall_success"]
            },
            "performance": {
                "total_time_ms": total_time,
                "scraping_time_ms": scrape_time,
                "database_save_time_ms": db_save_time,
                "cache_hit": False,
                "newly_processed": True
            }
        }
        
        logger.info(f"✅ Complete analysis finished for: {url} (took {total_time}ms)")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in enhanced scrape endpoint: {str(e)}")
        return {
            "success": False,
            "cached": False,
            "error": f"Server error: {str(e)}",
            "url": url if 'url' in locals() else "unknown",
            "message": "❌ Internal server error during processing"
        }

@app.get("/blog/{url:path}")
async def get_blog_analysis(url: str):
    """
    Retrieve existing blog analysis from databases
    
    Path: /blog/https://example.com/article
    Response: Combined data from Supabase + MongoDB
    """
    try:
        logger.info(f"🔍 Retrieving analysis for: {url}")
        
        result = await db_service.get_blog_by_url(url)
        
        if result["found"]:
            return {
                "success": True,
                "found": True,
                "data": {
                    "summary": result["summary"],
                    "content_available": bool(result["content"]),
                    "complete_record": result["complete"]
                },
                "message": "✅ Analysis retrieved from database"
            }
        else:
            return {
                "success": False,
                "found": False,
                "message": "❌ No analysis found for this URL",
                "suggestion": "Use /scrape endpoint to analyze this URL first"
            }
            
    except Exception as e:
        logger.error(f"❌ Error retrieving blog: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/recent")
async def get_recent_analyses(limit: int = 10):
    """
    Get recent blog analyses from databases
    
    Query params: ?limit=10
    Response: List of recent summaries with metadata
    """
    try:
        logger.info(f"📋 Retrieving {limit} recent analyses")
        
        recent_data = await db_service.get_recent_activity(limit)
        
        return {
            "success": True,
            "data": {
                "summaries": recent_data["summaries"],
                "count": recent_data["count"]["summaries"],
                "message": f"✅ Retrieved {recent_data['count']['summaries']} recent analyses"
            },
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"❌ Error retrieving recent analyses: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/stats")
async def get_database_statistics():
    """
    Get comprehensive database statistics and analytics
    
    Response: Database counts, consistency checks, performance metrics
    """
    try:
        logger.info("📊 Retrieving database statistics")
        
        stats = await db_service.get_database_statistics()
        
        return {
            "success": True,
            "statistics": stats,
            "message": "✅ Database statistics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error retrieving statistics: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/test-db")
async def test_databases():
    """
    Comprehensive database connection test for debugging
    
    Response: Detailed connection status for both databases
    """
    try:
        logger.info("🧪 Testing all database connections")
        
        result = await db_service.test_all_connections()
        
        return {
            "timestamp": "2025-07-13",
            "test_results": result,
            "recommendations": {
                "supabase": "✅ Working correctly" if result.get("supabase", {}).get("success") else "❌ Check SUPABASE_URL and SUPABASE_KEY",
                "mongodb": "✅ Working correctly" if result.get("mongodb", {}).get("success") else "❌ Check MONGODB_URI and network access"
            },
            "overall_status": "✅ All systems operational" if result.get("overall_success") else "⚠️ Issues detected"
        }
        
    except Exception as e:
        logger.error(f"❌ Database test error: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": "2025-07-13"
        }

# Legacy endpoints for backward compatibility
@app.post("/summarize")
async def summarize_text(request: dict):
    """Legacy endpoint for direct text summarization"""
    try:
        text = request.get("text")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        from summarizer import create_summary
        summary_result = create_summary(text, num_sentences=3)
        
        return {
            "success": True,
            "original_text_length": len(text),
            "summary": summary_result['summary'],
            "stats": {
                "original_sentences": summary_result['original_sentences'],
                "summary_sentences": summary_result['summary_sentences'],
                "compression_ratio": f"{summary_result['summary_sentences']}/{summary_result['original_sentences']}",
                "important_words": summary_result['important_words_found']
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Summarization error: {str(e)}"
        }

@app.get("/ping")
async def ping():
    """Simple ping endpoint for health monitoring"""
    return {
        "message": "pong", 
        "timestamp": "2025-07-13", 
        "version": "2.0.0",
        "database_integrated": True,
        "assignment": "Assignment 2 - Blog Summarizer with Database Storage"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)