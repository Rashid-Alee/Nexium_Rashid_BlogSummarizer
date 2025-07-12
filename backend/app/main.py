from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scraper import scrape_blog 

# Create FastAPI app
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# Enable CORS for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Home route
@app.get("/")
async def root():
    return {
        "message": "AI-Powered Blog Scraper API is running!",
        "project": "Assignment 2 - Blog Summarizer",
        "status": "Active",
        "features": {
            "scraping": "✅ Advanced content extraction",
            "summarization": "✅ AI-powered summarization",
            "translation": "🔄 Coming soon",
            "database": "🔄 Coming soon"
        },
        "endpoints": {
            "health": "/health",
            "scrape": "/scrape (POST)",
            "test": "/test"
        }
    }

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ai-blog-scraper"}

@app.post("/scrape")
async def scrape_url(request: dict):
    """
    Scrape a blog from URL AND create AI summary
    
    Send: {"url": "https://example.com"}
    Get: {
        "success": true,
        "title": "Blog Title",
        "content": "Full content...",
        "ai_summary": "Key points in 2-3 sentences",
        "summary_stats": {...},
        "word_count": 1500,
        ...
    }
    """
    try:
        # Get URL from request
        url = request.get("url")
        
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        print(f"📡 Scraping with AI summary: {url}")
        
        # Call scraper
        result = scrape_blog(url)
        
        if result.get("success"):
            print(f"✅ Scraping + Summarization successful!")
            print(f"   📝 Content: {result.get('word_count', 0)} words")
            print(f"   🤖 Summary: {len(result.get('ai_summary', ''))} chars")
        else:
            print(f"❌ Scraping failed: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in scrape endpoint: {str(e)}")
        return {
            "success": False,
            "error": f"Server error: {str(e)}"
        }

# Test endpoint with AI summary
@app.get("/test")
async def test():
    """Test the scraper + AI summarizer with a reliable URL"""
    try:
        test_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
        print(f"🧪 Testing AI scraper with: {test_url}")
        
        result = scrape_blog(test_url)
        
        return {
            "test_url": test_url,
            "scraper_result": result,
            "api_status": "working",
            "features_tested": [
                "✅ Content extraction",
                "✅ AI summarization", 
                "✅ API integration"
            ]
        }
    except Exception as e:
        return {
            "error": str(e),
            "api_status": "error"
        }

@app.post("/summarize")
async def summarize_text(request: dict):
    """
    Summarize provided text directly (no scraping)
    
    Send: {"text": "Long text to summarize..."}
    Get: {"summary": "Key points...", "stats": {...}}
    """
    try:
        text = request.get("text")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Import summarizer and use it directly
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

# Ping endpoint
@app.get("/ping")
async def ping():
    return {"message": "pong", "timestamp": "2025-07-10", "ai_ready": True}