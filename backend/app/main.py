# backend/app/main.py
# Minimal FastAPI server - avoiding documentation issues

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scraper import scrape_blog
import json

# Create FastAPI app WITHOUT auto-documentation
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# Enable CORS for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple home route
@app.get("/")
async def root():
    return {
        "message": "Blog Scraper API is running!",
        "project": "Assignment 2 - Blog Summarizer",
        "status": "Active",
        "endpoints": {
            "health": "/health",
            "scrape": "/scrape (POST)",
            "test": "/test"
        }
    }

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "blog-scraper"}

# Main scraping endpoint
@app.post("/scrape")
async def scrape_url(request: dict):
    """
    Scrape a blog from URL
    Send: {"url": "https://example.com"}
    """
    try:
        # Get URL from request
        url = request.get("url")
        
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        print(f"📡 Scraping: {url}")
        
        # Call scraper
        result = scrape_blog(url)
        
        print(f"✅ Scraping result: {result.get('success', False)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in scrape endpoint: {str(e)}")
        return {
            "success": False,
            "error": f"Server error: {str(e)}"
        }

# Simple test endpoint
@app.get("/test")
async def test():
    """Test the scraper with a reliable URL"""
    try:
        test_url = "https://httpbin.org/html"
        result = scrape_blog(test_url)
        
        return {
            "test_url": test_url,
            "scraper_result": result,
            "api_status": "working"
        }
    except Exception as e:
        return {
            "error": str(e),
            "api_status": "error"
        }

# Manual endpoint to test frontend connection
@app.get("/ping")
async def ping():
    return {"message": "pong", "timestamp": "2025-07-10"}

# Run with: uvicorn main:app --reload