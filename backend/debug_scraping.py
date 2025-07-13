# debug_scraping.py - Debug why blog summaries aren't being generated
# Save this in your backend/ folder and run it

import requests
import json
import sys
import os

# Add path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

def test_scraper_directly():
    """Test the scraper module directly without API"""
    print("🔧 TESTING SCRAPER MODULE DIRECTLY")
    print("=" * 50)
    
    try:
        # Import scraper directly
        from app.scraper import scrape_blog
        
        # Test with a simple URL
        test_url = "https://httpbin.org/html"
        print(f"📡 Testing scraper with: {test_url}")
        
        result = scrape_blog(test_url)
        
        print(f"\n📋 SCRAPER RESULT:")
        print(f"Success: {result.get('success')}")
        
        if result.get('success'):
            print(f"✅ Scraping worked!")
            print(f"   📝 Title: {result.get('title', 'No title')}")
            print(f"   📄 Content length: {len(result.get('content', ''))}")
            print(f"   📊 Word count: {result.get('word_count', 0)}")
            print(f"   🤖 AI Summary: {result.get('ai_summary', 'No summary')[:100]}...")
            print(f"   🌐 Urdu Summary: {result.get('ai_summary_urdu', 'No Urdu')[:100]}...")
        else:
            print(f"❌ Scraping failed: {result.get('error')}")
            
        return result
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error testing scraper: {e}")
        return None

def test_api_endpoint():
    """Test the API endpoint to see what's being returned"""
    print("\n🌐 TESTING API ENDPOINT")
    print("=" * 50)
    
    # Test URLs (from simple to complex)
    test_urls = [
        "https://httpbin.org/html",  # Simple test page
        "https://en.wikipedia.org/wiki/Python_(programming_language)",  # Rich content
        "https://www.bbc.com/news"  # Real news site
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📡 Test {i}: {url}")
        
        try:
            payload = {"url": url}
            
            response = requests.post(
                "http://localhost:8000/scrape", 
                json=payload,
                timeout=60  # Longer timeout for debugging
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ API Response received")
                print(f"   Success: {data.get('success')}")
                print(f"   Cached: {data.get('cached', False)}")
                
                if data.get('success'):
                    scrape_data = data.get('data', {})
                    print(f"   📝 Title: {scrape_data.get('title', 'No title')}")
                    print(f"   📊 Word count: {scrape_data.get('word_count', 0)}")
                    
                    # Check AI summary specifically
                    ai_summary = scrape_data.get('ai_summary')
                    if ai_summary:
                        print(f"   🤖 AI Summary (first 100 chars): {ai_summary[:100]}...")
                    else:
                        print(f"   ❌ NO AI SUMMARY GENERATED!")
                        
                    # Check Urdu translation
                    urdu_summary = scrape_data.get('ai_summary_urdu')
                    if urdu_summary:
                        print(f"   🌐 Urdu Summary: {urdu_summary[:100]}...")
                    else:
                        print(f"   ❌ NO URDU TRANSLATION!")
                        
                    # Check database status
                    db_status = data.get('database', {})
                    print(f"   💾 Database saved: {db_status.get('overall_success', 'Unknown')}")
                    
                else:
                    print(f"   ❌ API processing failed: {data.get('error', 'Unknown')}")
                    
            else:
                print(f"❌ API request failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to API. Make sure it's running on http://localhost:8000")
            break
        except Exception as e:
            print(f"❌ Error testing API: {e}")

def check_summarizer_module():
    """Check if the summarizer module is working"""
    print("\n🤖 TESTING SUMMARIZER MODULE")
    print("=" * 50)
    
    try:
        from app.summarizer import create_summary
        
        # Test with sample text
        test_text = """
        This is a test article about artificial intelligence. AI is transforming many industries today.
        Machine learning algorithms are becoming more sophisticated. Deep learning neural networks can
        process vast amounts of data. Natural language processing helps computers understand human language.
        Computer vision enables machines to interpret visual information. Robotics combines AI with physical
        systems to automate tasks. The future of AI looks very promising with many exciting developments ahead.
        """
        
        print("🧪 Testing summarizer with sample text...")
        result = create_summary(test_text, num_sentences=3)
        
        print(f"✅ Summarizer working!")
        print(f"   📄 Original sentences: {result.get('original_sentences')}")
        print(f"   📝 Summary sentences: {result.get('summary_sentences')}")
        print(f"   🤖 Summary: {result.get('summary')}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import summarizer: {e}")
        return False
    except Exception as e:
        print(f"❌ Summarizer error: {e}")
        return False

def check_translator_module():
    """Check if the translator module is working"""
    print("\n🌐 TESTING TRANSLATOR MODULE")
    print("=" * 50)
    
    try:
        from app.translator import StaticUrduTranslator
        
        translator = StaticUrduTranslator()
        
        test_text = "AI is transforming the world with machine learning and deep learning technologies."
        
        print("🧪 Testing translator with sample text...")
        urdu_text, stats = translator.translate_text(test_text)
        
        print(f"✅ Translator working!")
        print(f"   📝 Original: {test_text}")
        print(f"   🌐 Urdu: {urdu_text}")
        print(f"   📊 Method: {stats.get('method', 'Unknown')}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import translator: {e}")
        return False
    except Exception as e:
        print(f"❌ Translator error: {e}")
        return False

def main():
    """Run comprehensive debugging"""
    print("🐛 BLOG SUMMARY DEBUGGING")
    print("=" * 70)
    print("Let's find out why summaries aren't being generated!")
    print()
    
    # Test 1: Check individual modules
    summarizer_ok = check_summarizer_module()
    translator_ok = check_translator_module()
    
    # Test 2: Test scraper directly
    if summarizer_ok and translator_ok:
        scraper_result = test_scraper_directly()
    else:
        print("\n⚠️ Skipping scraper test due to module issues")
        scraper_result = None
    
    # Test 3: Test via API
    print("\n" + "="*50)
    print("Make sure your API is running: python -m app.main")
    input("Press Enter when API is running...")
    
    test_api_endpoint()
    
    # Summary
    print("\n" + "="*70)
    print("🎯 DEBUGGING SUMMARY:")
    print(f"📊 Summarizer module: {'✅' if summarizer_ok else '❌'}")
    print(f"🌐 Translator module: {'✅' if translator_ok else '❌'}")
    print(f"📡 Scraper module: {'✅' if scraper_result and scraper_result.get('success') else '❌'}")
    
    print("\n💡 NEXT STEPS:")
    if not summarizer_ok:
        print("1. Check your app/summarizer.py file")
    if not translator_ok:
        print("2. Check your app/translator.py file") 
    if scraper_result and not scraper_result.get('success'):
        print("3. Check your app/scraper.py file")
    print("4. Check API logs for detailed error messages")

if __name__ == "__main__":
    main()