import requests
from bs4 import BeautifulSoup
import re

def scrape_blog(url):
    
    print(f"🌐 Advanced scraping: {url}")
    
    try:
        # Step 1: Get the webpage with better headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Failed to access webpage. Status: {response.status_code}"
            }
        
        print("✅ Webpage downloaded successfully!")
        
        # Step 2: Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Step 3: Clean unwanted elements FIRST
        remove_unwanted_elements(soup)
        
        # Step 4: Extract title using multiple strategies
        title = extract_title_advanced(soup)
        print(f"📰 Title: {title}")
        
        # Step 5: Extract ALL content using multiple strategies
        content = extract_content_advanced(soup)
        
        # Step 6: Extract metadata
        metadata = extract_metadata(soup)
        
        # Step 7: Calculate statistics
        word_count = len(content.split())
        char_count = len(content)
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        
        print(f"✅ Extraction complete!")
        print(f"   📊 Words: {word_count}")
        print(f"   📊 Characters: {char_count}")
        print(f"   📊 Paragraphs: {paragraph_count}")
        
        return {
            "success": True,
            "title": title,
            "content": content,
            "word_count": word_count,
            "char_count": char_count,
            "paragraph_count": paragraph_count,
            "url": url,
            "metadata": metadata
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            "success": False,
            "error": f"Error occurred: {str(e)}"
        }

def remove_unwanted_elements(soup):
    """Remove elements we don't want in our content"""
    
    # Remove scripts, styles, and other non-content
    unwanted_tags = [
        'script', 'style', 'nav', 'footer', 'header', 'aside',
        'iframe', 'noscript', 'form', 'button', 'input'
    ]
    
    for tag in unwanted_tags:
        for element in soup.find_all(tag):
            element.decompose()
    
    # Remove common unwanted classes and IDs
    unwanted_selectors = [
        '.advertisement', '.ads', '.social-share', '.comments',
        '.sidebar', '.menu', '.navigation', '.popup', '.modal',
        '.cookie-notice', '.newsletter', '.related-posts',
        '#comments', '#sidebar', '#footer', '#header'
    ]
    
    for selector in unwanted_selectors:
        for element in soup.select(selector):
            element.decompose()
    
    print("🧹 Cleaned unwanted elements")

def extract_title_advanced(soup):
    """Extract title using multiple advanced strategies"""
    
    title_strategies = [
        # Strategy 1: Common blog title patterns
        lambda s: s.select_one('h1.post-title, h1.entry-title, h1.article-title'),
        lambda s: s.select_one('.post-header h1, .entry-header h1, .article-header h1'),
        
        # Strategy 2: Semantic HTML
        lambda s: s.select_one('article h1, main h1'),
        
        # Strategy 3: Schema.org structured data
        lambda s: s.select_one('[itemProp="headline"], [itemProp="name"]'),
        
        # Strategy 4: OpenGraph meta tags
        lambda s: s.select_one('meta[property="og:title"]'),
        
        # Strategy 5: First h1 tag
        lambda s: s.select_one('h1'),
        
        # Strategy 6: Page title
        lambda s: s.select_one('title')
    ]
    
    for strategy in title_strategies:
        try:
            element = strategy(soup)
            if element:
                if element.name == 'meta':
                    title = element.get('content', '')
                else:
                    title = element.get_text().strip()
                
                if title and len(title) > 3 and len(title) < 200:
                    print(f"📰 Found title using strategy: {title[:50]}...")
                    return clean_text(title)
        except:
            continue
    
    return "No title found"

def extract_content_advanced(soup):
    """Extract ALL content using multiple advanced strategies"""
    
    content_strategies = [
        # Strategy 1: Semantic article content
        extract_from_article,
        
        # Strategy 2: Common blog content patterns
        extract_from_content_classes,
        
        # Strategy 3: Main content area
        extract_from_main,
        
        # Strategy 4: Structured data
        extract_from_structured_data,
        
        # Strategy 5: All paragraphs (fallback)
        extract_all_paragraphs
    ]
    
    for strategy_func in content_strategies:
        try:
            content = strategy_func(soup)
            if content and len(content) > 300:  
                print(f"✅ Content extracted using: {strategy_func.__name__}")
                return clean_text(content)
        except Exception as e:
            print(f"⚠️  Strategy {strategy_func.__name__} failed: {e}")
            continue
    
    return "Could not extract meaningful content from this page"

def extract_from_article(soup):
    """Extract content from article tags"""
    articles = soup.find_all('article')
    if articles:
        # Get the largest article
        article = max(articles, key=lambda x: len(x.get_text()))
        return article.get_text()
    return ""

def extract_from_content_classes(soup):
    """Extract from common content classes"""
    content_selectors = [
        '.post-content', '.entry-content', '.article-content',
        '.content', '.post-body', '.article-body',
        '.post-text', '.entry-text', '.main-content',
        '.blog-content', '.story-content', '.text-content'
    ]
    
    for selector in content_selectors:
        elements = soup.select(selector)
        if elements:
            # Get the element with most text
            element = max(elements, key=lambda x: len(x.get_text()))
            content = element.get_text()
            if len(content) > 300:
                return content
    return ""

def extract_from_main(soup):
    """Extract from main content areas"""
    main_selectors = ['main', '.main', '#main', '.container .content']
    
    for selector in main_selectors:
        element = soup.select_one(selector)
        if element:
            content = element.get_text()
            if len(content) > 300:
                return content
    return ""

def extract_from_structured_data(soup):
    """Extract from structured data"""
    # Try JSON-LD structured data
    json_scripts = soup.find_all('script', type='application/ld+json')
    for script in json_scripts:
        try:
            import json
            data = json.loads(script.string)
            if 'articleBody' in data:
                return data['articleBody']
        except:
            continue
    
    article_body = soup.select_one('[itemprop="articleBody"]')
    if article_body:
        return article_body.get_text()
    
    return ""

def extract_all_paragraphs(soup):
    """Fallback: extract all paragraph content"""
    paragraphs = soup.find_all('p')
    if paragraphs:
        content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        return content
    return ""

def extract_metadata(soup):
    """Extract additional metadata"""
    metadata = {}
    
    # Author
    author_selectors = [
        '.author', '.post-author', '.entry-author',
        '[rel="author"]', '[itemprop="author"]',
        'meta[name="author"]'
    ]
    
    for selector in author_selectors:
        element = soup.select_one(selector)
        if element:
            if element.name == 'meta':
                metadata['author'] = element.get('content', '')
            else:
                metadata['author'] = element.get_text().strip()
            break
    
    # Publication date
    date_selectors = [
        'time[datetime]', '.post-date', '.published',
        '.entry-date', '[itemprop="datePublished"]'
    ]
    
    for selector in date_selectors:
        element = soup.select_one(selector)
        if element:
            date_text = element.get('datetime') or element.get_text().strip()
            if date_text:
                metadata['publish_date'] = date_text
                break
    
    # Description
    meta_desc = soup.select_one('meta[name="description"]')
    if meta_desc:
        metadata['description'] = meta_desc.get('content', '')
    
    return metadata

def clean_text(text):
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-\'""]', ' ', text)
    
    # Remove extra spaces again
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def test_scraper():
    """Test function with better URLs"""
    
    print("🧪 Testing Advanced Blog Scraper")
    print("=" * 60)
    
    # Better test URLs that should have lots of content
    test_urls = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://httpbin.org/html",
        "https://example.com"
    ]
    
    for i, test_url in enumerate(test_urls, 1):
        print(f"\n🔸 Test {i}: {test_url}")
        print("-" * 60)
        
        result = scrape_blog(test_url)
        
        if result["success"]:
            print("🎉 SUCCESS!")
            print(f"📰 Title: {result['title'][:80]}...")
            print(f"📝 Words: {result['word_count']:,}")
            print(f"📄 Characters: {result['char_count']:,}")
            print(f"📄 Content preview: {result['content'][:200]}...")
            if result.get('metadata'):
                print(f"👤 Author: {result['metadata'].get('author', 'Not found')}")
                print(f"📅 Date: {result['metadata'].get('publish_date', 'Not found')}")
        else:
            print("❌ FAILED!")
            print(f"🔍 Error: {result['error']}")
        
        #pause between requests
        import time
        time.sleep(2)

# Run test when file is executed
if __name__ == "__main__":
    test_scraper()