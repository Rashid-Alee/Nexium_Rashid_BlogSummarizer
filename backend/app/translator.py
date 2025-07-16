import logging
from typing import Tuple, Dict
import requests
import json
import time

logger = logging.getLogger(__name__)

class GoogleUrduTranslator:
    """
    Real Google Translate using deep-translator
    """
    
    def __init__(self):
        """Initialize translator"""
        try:
            # Try to import deep-translator
            from deep_translator import GoogleTranslator
            self.translator = GoogleTranslator(source='en', target='ur')
            self.method_used = "google_translate_deep"
            logger.info("✅ Google Translator (deep-translator) initialized successfully")
        except ImportError:
            # Fallback to direct API calls if deep-translator not available
            self.translator = None
            self.method_used = "direct_api"
            logger.warning("⚠️ deep-translator not found, using direct API")
        except Exception as e:
            logger.error(f"❌ Failed to initialize translator: {e}")
            self.translator = None
            self.method_used = "fallback"

    def translate_text(self, text: str) -> Tuple[str, Dict]:
        """
        Translate English text to Urdu using Google Translate
        
        Args:
            text (str): English text to translate
            
        Returns:
            Tuple[str, Dict]: (urdu_text, translation_stats)
        """
        try:
            if not text or len(text.strip()) == 0:
                return "", {"error": "Empty text provided"}
            
            logger.info(f"🌐 Translating text to Urdu: {text[:50]}...")
            
            # Use deep-translator if available
            if self.translator and self.method_used == "google_translate_deep":
                return self._translate_with_deep_translator(text)
            
            # Direct API call (no dependency conflicts)
            elif self.method_used == "direct_api":
                return self._translate_with_direct_api(text)
            
            # Method 3: Fallback to enhanced dictionary
            else:
                return self._fallback_translation(text)
                
        except Exception as e:
            logger.error(f"❌ Translation error: {e}")
            return self._fallback_translation(text)

    def _translate_with_deep_translator(self, text: str) -> Tuple[str, Dict]:
        """Use deep-translator library"""
        try:
            result = self.translator.translate(text)
            
            stats = {
                "words_translated": len(text.split()),
                "total_words": len(text.split()),
                "coverage": 100.0,
                "method": "google_translate_deep",
                "confidence": "high",
                "service": "Google Translate (deep-translator)"
            }
            
            logger.info(f"✅ Deep-translator success: {result[:50]}...")
            return result, stats
            
        except Exception as e:
            logger.error(f"❌ Deep-translator failed: {e}")
            return self._translate_with_direct_api(text)

    def _translate_with_direct_api(self, text: str) -> Tuple[str, Dict]:
        """Direct Google Translate API call (no dependencies)"""
        try:
            # Simple API call to Google Translate
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'en',
                'tl': 'ur',
                'dt': 't',
                'q': text
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract translated text from Google's response
                translated_text = ""
                if result and len(result) > 0 and len(result[0]) > 0:
                    for item in result[0]:
                        if item[0]:
                            translated_text += item[0]
                
                stats = {
                    "words_translated": len(text.split()),
                    "total_words": len(text.split()),
                    "coverage": 100.0,
                    "method": "google_translate_direct",
                    "confidence": "high",
                    "service": "Google Translate (Direct API)"
                }
                
                logger.info(f"✅ Direct API success: {translated_text[:50]}...")
                return translated_text, stats
            else:
                raise Exception(f"API returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Direct API failed: {e}")
            return self._enhanced_dictionary_translation(text)

    def _enhanced_dictionary_translation(self, text: str) -> Tuple[str, Dict]:
        """Enhanced dictionary-based translation with better coverage"""
        
        # Comprehensive dictionary for technical content
        enhanced_dict = {
            # AI/Tech terms
            "artificial intelligence": "مصنوعی ذہانت",
            "machine learning": "مشین لرننگ",
            "deep learning": "ڈیپ لرننگ",
            "neural network": "نیورل نیٹ ورک",
            "algorithm": "الگورتھم",
            "data science": "ڈیٹا سائنس",
            "big data": "بگ ڈیٹا",
            "cloud computing": "کلاؤڈ کمپیوٹنگ",
            "software development": "سافٹ ویئر ڈیولپمنٹ",
            "programming": "پروگرامنگ",
            "database": "ڈیٹابیس",
            "technology": "ٹیکنالوجی",
            "digital transformation": "ڈیجیٹل تبدیلی",
            "automation": "خودکار",
            "innovation": "جدت",
            "research": "تحقیق",
            "development": "ترقی",
            "analysis": "تجزیہ",
            "optimization": "بہتری",
            "efficiency": "کارکردگی",
            "performance": "کارکردگی",
            "solution": "حل",
            "system": "نظام",
            "platform": "پلیٹ فارم",
            "application": "ایپلیکیشن",
            "framework": "فریم ورک",
            "infrastructure": "بنیادی ڈھانچہ",
            
            # Common words
            "helps": "مدد کرتا ہے",
            "improves": "بہتر بناتا ہے",
            "enables": "قابل بناتا ہے",
            "provides": "فراہم کرتا ہے",
            "offers": "پیش کرتا ہے",
            "allows": "اجازت دیتا ہے",
            "creates": "بناتا ہے",
            "generates": "پیدا کرتا ہے",
            "processes": "پروسیس کرتا ہے",
            "analyzes": "تجزیہ کرتا ہے",
            "transforms": "تبدیل کرتا ہے",
            "revolutionizes": "انقلاب لاتا ہے",
            "enhances": "بہتر بناتا ہے",
            "optimizes": "بہتر بناتا ہے",
            "utilizes": "استعمال کرتا ہے",
            "implements": "لاگو کرتا ہے",
            "integrates": "ضم کرتا ہے",
            "facilitates": "آسان بناتا ہے",
            
            # Business terms
            "companies": "کمپنیاں",
            "organizations": "تنظیمیں",
            "businesses": "کاروبار",
            "enterprises": "ادارے",
            "industries": "صنعتیں",
            "sectors": "شعبے",
            "markets": "بازار",
            "customers": "صارفین",
            "users": "صارفین",
            "professionals": "پیشہ ور",
            "experts": "ماہرین",
            "teams": "ٹیمز",
            "workforce": "افرادی قوت",
            "productivity": "پیداواری صلاحیت",
            "growth": "ترقی",
            "success": "کامیابی",
            "leadership": "قیادت",
            "management": "انتظام",
            "strategy": "حکمت عملی",
            "competitive": "مسابقتی",
            "advantage": "فائدہ",
            "opportunity": "موقع",
            "challenge": "چیلنج",
            "investment": "سرمایہ کاری",
            "revenue": "آمدنی",
            "profit": "منافع",
            "cost": "لاگت",
            "budget": "بجٹ",
            "resources": "وسائل",
            "capabilities": "صلاحیات",
            "skills": "مہارات",
            "experience": "تجربہ",
            "knowledge": "علم",
            "expertise": "مہارت"
        }
        
        # Process text with enhanced dictionary
        words = text.lower().split()
        translated_parts = []
        translated_count = 0
        
        # Check for multi-word phrases first
        i = 0
        while i < len(words):
            found_phrase = False
            
            # Check for 2-word phrases
            if i < len(words) - 1:
                two_word = f"{words[i]} {words[i+1]}"
                if two_word in enhanced_dict:
                    translated_parts.append(enhanced_dict[two_word])
                    translated_count += 2
                    i += 2
                    found_phrase = True
            
            if not found_phrase:
                # Single word translation
                clean_word = words[i].strip('.,!?;:')
                if clean_word in enhanced_dict:
                    translated_parts.append(enhanced_dict[clean_word])
                    translated_count += 1
                else:
                    translated_parts.append(clean_word)  # Keep original if not found
                i += 1
        
        # Create meaningful Urdu sentence
        if translated_count > 0:
            urdu_text = " ".join(translated_parts)
            # Add proper Urdu sentence structure
            urdu_text = urdu_text.replace(" ہے ", " ہے۔ ")
            urdu_text = urdu_text.replace(" کرتا ہے", " کرتا ہے۔")
        else:
            urdu_text = "یہ ایک تکنیکی مضمون ہے جس میں جدید ٹیکنالوجی کے بارے میں معلومات ہیں۔"
        
        coverage = (translated_count / len(words) * 100) if len(words) > 0 else 0
        
        stats = {
            "words_translated": translated_count,
            "total_words": len(words),
            "coverage": round(coverage, 1),
            "method": "enhanced_dictionary",
            "confidence": "medium" if coverage > 50 else "low"
        }
        
        return urdu_text, stats

    def _fallback_translation(self, text: str) -> Tuple[str, Dict]:
        """Final fallback translation"""
        fallback_text = "یہ ایک اہم مضمون ہے جس میں مفید معلومات شامل ہیں۔"
        fallback_stats = {
            "words_translated": 0,
            "total_words": len(text.split()),
            "coverage": 0.0,
            "method": "fallback",
            "confidence": "low",
            "note": "Translation service unavailable"
        }
        
        return fallback_text, fallback_stats

    def get_dictionary_size(self) -> Dict[str, int]:
        """Return information about the translator"""
        return {
            "method": self.method_used,
            "service": "Google Translate (Conflict-Free)",
            "fallback_available": True
        }

# Create instance for compatibility with existing code
class StaticUrduTranslator(GoogleUrduTranslator):
    """Alias for backward compatibility"""
    pass

# Test function
def test_translator():
    """Test the translator with real examples"""
    translator = GoogleUrduTranslator()
    
    test_texts = [
        "Artificial intelligence is revolutionizing software development.",
        "Machine learning algorithms help companies improve their efficiency.",
        "Data science enables organizations to make better decisions.",
        "Cloud computing provides scalable solutions for businesses."
    ]
    
    print("🧪 Testing Conflict-Free Google Translator:")
    print("=" * 60)
    
    for i, text in enumerate(test_texts, 1):
        urdu, stats = translator.translate_text(text)
        print(f"\n📝 Test {i}:")
        print(f"English: {text}")
        print(f"Urdu: {urdu}")
        print(f"Method: {stats['method']}")
        print(f"Coverage: {stats['coverage']}%")
        print(f"Confidence: {stats['confidence']}")
        print("-" * 40)

if __name__ == "__main__":
    test_translator()