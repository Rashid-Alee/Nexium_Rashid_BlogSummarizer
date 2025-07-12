import re
from collections import Counter

def split_into_sentences(text):
    
    # Split on sentence-ending punctuation
    sentences = re.split(r'[.!?]+', text)
    
    # Clean and filter sentences
    cleaned_sentences = []
    for sentence in sentences:
        clean_sentence = sentence.strip()
        
        # Keep sentences with 5-40 words that have meaningful content
        word_count = len(clean_sentence.split())
        if 5 <= word_count <= 40 and has_meaningful_content(clean_sentence):
            cleaned_sentences.append(clean_sentence)
    
    return cleaned_sentences

def has_meaningful_content(sentence):
    """
    Check if sentence contains actual information (not headers/promotional content)
    
    Args:
        sentence (str): Sentence to evaluate
        
    Returns:
        bool: True if sentence has meaningful content
    """
    # Must have substantive words
    substantive_words = [w for w in sentence.split() if len(w) > 3 and w.isalpha()]
    if len(substantive_words) < 3:
        return False
    
    # Avoid headings and promotional content
    return not (is_likely_heading(sentence) or is_promotional_language(sentence))

def is_likely_heading(sentence):
    """Detect if sentence is likely a heading or title"""
    if len(sentence.split()) < 6 or sentence.strip().endswith('?'):
        return True
    
    heading_patterns = [
        r'^(when|how|what|why|where).*did.*ai',
        r'^(machine learning|natural language|expert systems)',
        r'^(diagnosis|treatment|administrative).*applications',
        r'^(challenges|benefits|future).*of.*ai'
    ]
    
    return any(re.search(pattern, sentence.lower()) for pattern in heading_patterns)

def is_promotional_language(sentence):
    
    promotional_phrases = [
        'refined way', 'game changer', 'truly remarkable', 'groundbreaking',
        'revolutionary', 'cutting edge', 'leading the way', 'promises to be', 
        'offers a way', 'delivers better', 'ultimately', 'reshaping the industry'
    ]
    
    sentence_lower = sentence.lower()
    return any(phrase in sentence_lower for phrase in promotional_phrases)

def count_words(text):
    """
    Count word frequencies with filtering for meaningful words
    
    Args:
        text (str): Input text to analyze
        
    Returns:
        dict: Dictionary of word frequencies
    """
    # Extract words (3+ characters, alphabetic only)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Count frequencies and filter
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1
    
    # Keep words that appear 2-15 times (not too rare, not too common)
    filtered_counts = {word: count for word, count in word_count.items() if 2 <= count <= 15}
    
    return filtered_counts

def remove_stop_words(word_count):
    """
    Remove common words that don't add meaning
    
    Args:
        word_count (dict): Word frequency dictionary
        
    Returns:
        dict: Filtered word frequency dictionary
    """
    stop_words = {
        'the', 'and', 'are', 'was', 'were', 'been', 'have', 'has', 'had',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must',
        'this', 'that', 'these', 'those', 'with', 'from', 'they', 'them',
        'their', 'said', 'say', 'says', 'also', 'but', 'not', 'all', 'any',
        'more', 'most', 'some', 'than', 'when', 'where', 'why', 'how',
        'used', 'use', 'using', 'being', 'such', 'into', 'through', 'during'
    }
    
    # Keep only meaningful words (not stop words, length > 3)
    important_words = {}
    for word, count in word_count.items():
        if word not in stop_words and len(word) > 3:
            important_words[word] = count
    
    return important_words

def score_sentences(sentences, important_words):
    """
    Score sentences based on importance and information content
    
    Args:
        sentences (list): List of sentences to score
        important_words (dict): Dictionary of important words and their frequencies
        
    Returns:
        list: List of dictionaries with sentence scores and metadata
    """
    sentence_scores = []
    
    for i, sentence in enumerate(sentences):
        words = sentence.lower().split()
        
        # Calculate various scoring factors
        word_density_score = calculate_word_density(sentence, important_words)
        position_score = 0.3 if i < len(sentences) * 0.3 else 0  # Early sentences bonus
        technical_score = calculate_technical_score(sentence)
        info_density = calculate_information_density(sentence)
        repetition_penalty = calculate_repetition_penalty(sentence)
        length_score = 0.1 if 10 <= len(words) <= 25 else 0
        
        # Combine all scores
        total_score = (word_density_score * 2) + position_score + technical_score + info_density + length_score - repetition_penalty
        
        sentence_scores.append({
            'sentence': sentence,
            'score': total_score,
            'important_words': sum(1 for word in words if re.sub(r'[^a-zA-Z]', '', word) in important_words),
            'total_words': len(words)
        })
    
    # Sort by score (highest first)
    sentence_scores.sort(key=lambda x: x['score'], reverse=True)
    return sentence_scores

def calculate_word_density(sentence, important_words):
    """Calculate density of important words in sentence"""
    words = sentence.lower().split()
    important_count = sum(1 for word in words if re.sub(r'[^a-zA-Z]', '', word) in important_words)
    return important_count / len(words) if words else 0

def calculate_technical_score(sentence):
    """Score based on technical/specific content"""
    technical_terms = [
        'algorithm', 'machine learning', 'deep learning', 'neural',
        'diagnosis', 'diagnostic', 'treatment', 'clinical', 'medical',
        'patient', 'disease', 'cancer', 'imaging', 'data', 'analysis',
        'accuracy', 'precision', 'prediction', 'detection', 'research'
    ]
    
    sentence_lower = sentence.lower()
    tech_count = sum(1 for term in technical_terms if term in sentence_lower)
    words = sentence.split()
    return (tech_count / len(words)) * 2 if words else 0

def calculate_information_density(sentence):
    """Score based on information density"""
    words = sentence.split()
    informative_words = [w for w in words if len(w) > 4 and w.isalpha()]
    
    if words:
        density = len(informative_words) / len(words)
        return density * 0.5
    return 0

def calculate_repetition_penalty(sentence):
    """Penalty for overusing repetitive terms"""
    sentence_lower = sentence.lower()
    repetitive_terms = ['healthcare', 'artificial intelligence']
    total_mentions = sum(sentence_lower.count(term) for term in repetitive_terms)
    
    return min(total_mentions * 0.2, 1.0)  # Cap penalty at 1.0

def select_diverse_sentences(scored_sentences, num_sentences):
    """
    Select diverse, non-repetitive sentences for summary
    
    Args:
        scored_sentences (list): List of scored sentences
        num_sentences (int): Number of sentences to select
        
    Returns:
        list: List of selected sentences
    """
    selected = []
    used_concepts = set()
    
    for item in scored_sentences:
        if len(selected) >= num_sentences:
            break
            
        sentence = item['sentence']
        words = set(re.findall(r'\b\w{4,}\b', sentence.lower()))
        
        # Check for overlap with already selected sentences
        overlap = len(words & used_concepts)
        overlap_ratio = overlap / len(words) if words else 0
        
        # Select if low overlap (adds new information)
        if overlap_ratio < 0.4:
            selected.append(sentence)
            used_concepts.update(words)
    
    return selected

def create_summary(text, num_sentences=3):
    """
    Main function: Create AI summary using static logic
    
    Args:
        text (str): Input text to summarize
        num_sentences (int): Number of sentences in summary (default: 3)
        
    Returns:
        dict: Summary result with metadata
    """
    #Extract quality sentences
    sentences = split_into_sentences(text)
    
    if len(sentences) < 3:
        return {
            'summary': "Content too short or low quality for meaningful summarization.",
            'original_sentences': len(sentences),
            'summary_sentences': 0,
            'important_words_found': 0
        }
    
    #Analyze word importance
    word_count = count_words(text)
    important_words = remove_stop_words(word_count)
    
    #Score and rank sentences
    scored_sentences = score_sentences(sentences, important_words)
    
    #Select diverse, high-quality sentences
    selected_sentences = select_diverse_sentences(scored_sentences, num_sentences)
    
    #final summary
    final_summary = '. '.join(selected_sentences) + '.'
    
    return {
        'summary': final_summary,
        'original_sentences': len(sentences),
        'summary_sentences': len(selected_sentences),
        'important_words_found': len(important_words),
        'top_sentences': [{'sentence': s, 'score': 'enhanced'} for s in selected_sentences]
    }