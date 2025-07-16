
import requests
from bs4 import BeautifulSoup
import re
from summarizer import create_summary
from translator import StaticUrduTranslator  

def scrape_blog(url):
    """
    Scrape blog content, generate AI summary, and translate to Urdu
    """
    
    try:
        # Initialize translator
        translator = StaticUrduTranslator()
        
        # Setup request headers to avoid bot detection
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
        
        # Parse HTML and clean unwanted elements
        soup = BeautifulSoup(response.text, 'html.parser')
        remove_unwanted_elements(soup)
        
        # Extract main content
        title = extract_title_advanced(soup)
        content = extract_content_advanced(soup)
        metadata = extract_metadata(soup)
        
        # Calculate basic stats
        word_count = len(content.split())
        char_count = len(content)
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        
        # Generate AI summary if content is long enough
        ai_summary = ""
        ai_summary_urdu = ""
        summary_stats = {}
        translation_stats = {}
        
        if word_count > 50:
            try:
                # Step 1: Create clean English summary first
                summary_result = create_summary(content, num_sentences=3)
                ai_summary = summary_result['summary']
                
                summary_stats = {
                    'original_sentences': summary_result['original_sentences'],
                    'summary_sentences': summary_result['summary_sentences'],
                    'important_words_found': summary_result['important_words_found'],
                    'compression_ratio': f"{summary_result['summary_sentences']}/{summary_result['original_sentences']}"
                }
                
                # Step 2: Translate ONLY the clean English summary to Urdu
                ai_summary_urdu, translation_stats = translator.translate_text(ai_summary)
                
            except Exception as e:
                ai_summary = "Summary generation failed, but content extracted successfully."
                ai_summary_urdu = "خلاصہ بنانے میں خرابی، لیکن مواد کامیابی سے نکالا گیا۔"
                summary_stats = {"error": str(e)}
                translation_stats = {"error": str(e)}
        
        else:
            ai_summary = "Content too short for meaningful summarization."
            ai_summary_urdu = "مواد خلاصہ بنانے کے لیے بہت مختصر ہے۔"
            summary_stats = {"note": "Content under 50 words"}
            translation_stats = {"note": "Content too short"}
        
        # Also translate the title if available
        title_urdu = ""
        if title and title != "No title found":
            title_urdu, _ = translator.translate_text(title)
        
        # Return complete result with translation
        return {
            "success": True,
            "title": title,
            "title_urdu": title_urdu,
            "content": content,
            "ai_summary": ai_summary,
            "ai_summary_urdu": ai_summary_urdu,
            "summary_stats": summary_stats,
            "translation_stats": translation_stats,
            "word_count": word_count,
            "char_count": char_count,
            "paragraph_count": paragraph_count,
            "url": url,
            "metadata": metadata,
            "dictionary_info": translator.get_dictionary_size()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error occurred: {str(e)}"
        }

# Keep all existing helper functions unchanged
def remove_unwanted_elements(soup):
    """Remove scripts, ads, and navigation elements"""
    unwanted_tags = [
        'script', 'style', 'nav', 'footer', 'header', 'aside',
        'iframe', 'noscript', 'form', 'button', 'input'
    ]
    
    for tag in unwanted_tags:
        for element in soup.find_all(tag):
            element.decompose()
    
    unwanted_selectors = [
        '.advertisement', '.ads', '.social-share', '.comments',
        '.sidebar', '.menu', '.navigation', '.popup', '.modal',
        '.cookie-notice', '.newsletter', '.related-posts',
        '#comments', '#sidebar', '#footer', '#header'
    ]
    
    for selector in unwanted_selectors:
        for element in soup.select(selector):
            element.decompose()

def extract_title_advanced(soup):
    """Extract page title using multiple strategies"""
    # Try h1 tags first
    h1_tags = soup.find_all('h1')
    if h1_tags:
        for h1 in h1_tags:
            title = h1.get_text().strip()
            if len(title) > 10 and len(title) < 200:
                return title
    
    # Try title-specific classes
    title_selectors = [
        '.post-title', '.entry-title', '.article-title',
        '.title', '.headline', '.post-header h1',
        'h1.title', 'h1.post-title'
    ]
    
    for selector in title_selectors:
        element = soup.select_one(selector)
        if element:
            title = element.get_text().strip()
            if len(title) > 10:
                return title
    
    # Fallback to HTML title tag
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.get_text().strip()
    
    return "No title found"

def extract_content_advanced(soup):
    """Extract main content using multiple strategies"""
    
    # List of extraction strategies in order of preference
    strategies = [
        extract_from_article,
        extract_from_content_classes,
        extract_from_main,
        extract_all_paragraphs
    ]
    
    for strategy_func in strategies:
        try:
            content = strategy_func(soup)
            if content and len(content.strip()) > 200:
                return clean_text(content)
        except Exception as e:
            continue
    
    return "Could not extract meaningful content from this page"

def extract_from_article(soup):
    """Try extracting from <article> tags"""
    articles = soup.find_all('article')
    if articles:
        article = max(articles, key=lambda x: len(x.get_text()))
        return article.get_text()
    return ""

def extract_from_content_classes(soup):
    """Try content-specific CSS classes"""
    content_selectors = [
        '.post-content', '.entry-content', '.article-content',
        '.content', '.post-body', '.article-body',
        '.post-text', '.entry-text', '.main-content',
        '.blog-content', '.story-content', '.text-content'
    ]
    
    for selector in content_selectors:
        elements = soup.select(selector)
        if elements:
            element = max(elements, key=lambda x: len(x.get_text()))
            content = element.get_text()
            if len(content) > 300:
                return content
    return ""

def extract_from_main(soup):
    """Try main content containers"""
    main_selectors = ['main', '.main', '#main', '.container .content']
    
    for selector in main_selectors:
        element = soup.select_one(selector)
        if element:
            content = element.get_text()
            if len(content) > 300:
                return content
    return ""

def extract_all_paragraphs(soup):
    """Fallback: combine all paragraphs"""
    paragraphs = soup.find_all('p')
    if paragraphs:
        content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        return content
    return ""

def extract_metadata(soup):
    """Extract author, date, and description"""
    metadata = {}
    
    # Try to find author
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
    
    # Try to find publication date
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
    
    # Extract description from meta tag
    meta_desc = soup.select_one('meta[name="description"]')
    if meta_desc:
        metadata['description'] = meta_desc.get('content', '')
    
    return metadata

def clean_text(text):
    """Clean and normalize extracted text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-\'""]', ' ', text)
    
    # Remove extra spaces again
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()
