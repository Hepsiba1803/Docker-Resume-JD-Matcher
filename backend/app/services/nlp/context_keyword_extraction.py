import spacy
import string
from keybert import KeyBERT
import csv
import os
import logging
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from typing import Set, Dict, Tuple, Optional
from . import fuzzymatching

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Absolute path to the CSV file
csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "dataset.csv"))

# Global variables for models (initialized lazily)
_nlp_model = None
_keybert_model = None
_skill_set = None
_skill_dict = None

def _get_nlp_model():
    """Lazy loading of spaCy model with error handling."""
    global _nlp_model
    if _nlp_model is None:
        try:
            _nlp_model = spacy.load('en_core_web_sm')
            logger.info("SpaCy model loaded successfully")
        except OSError as e:
            logger.error(f"Failed to load spaCy model: {e}")
            # Fallback to basic text processing
            _nlp_model = None
    return _nlp_model

@lru_cache(maxsize=1)
def get_kw_model():
    """Cached KeyBERT model loading with error handling."""
    global _keybert_model
    if _keybert_model is None:
        try:
            local_model_path = "local_models/all-MiniLM-L6-v2"
            
            # Check if local model exists
            if not os.path.exists(local_model_path):
                logger.warning(f"Local model not found at {local_model_path}, using default")
                model = SentenceTransformer('all-MiniLM-L6-v2')
            else:
                model = SentenceTransformer(local_model_path)
            
            _keybert_model = KeyBERT(model)
            logger.info("KeyBERT model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load KeyBERT model: {e}")
            raise RuntimeError(f"Could not initialize KeyBERT model: {e}")
    
    return _keybert_model

def load_skill_set(csv_path: str) -> Set[str]:
    """
    Load skill set from CSV into a set with proper error handling.
    
    Args:
        csv_path (str): Path to the CSV file
        
    Returns:
        Set[str]: Set of skills in lowercase
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV is malformed
    """
    global _skill_set
    
    if _skill_set is not None:
        return _skill_set
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Skills CSV file not found: {csv_path}")
    
    try:
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)  # Skip header safely
            
            if header is None:
                raise ValueError("CSV file is empty")
            
            skills = set()
            for row_num, row in enumerate(reader, start=2):  # Start from 2 (after header)
                if not row or not row[0].strip():
                    logger.warning(f"Empty skill found at row {row_num}")
                    continue
                
                skill = row[0].strip().lower()
                if skill:  # Additional check for non-empty after strip
                    skills.add(skill)
            
            if not skills:
                raise ValueError("No valid skills found in CSV")
            
            _skill_set = skills
            logger.info(f"Loaded {len(skills)} skills from CSV")
            return skills
            
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error reading CSV: {e}")
        raise ValueError(f"Could not read CSV file due to encoding issues: {e}")
    except csv.Error as e:
        logger.error(f"CSV parsing error: {e}")
        raise ValueError(f"Malformed CSV file: {e}")
    except Exception as e:
        logger.error(f"Unexpected error loading skills: {e}")
        raise

def load_skill_set_to_dict(csv_path: str) -> Dict[str, str]:
    """
    Loads the skills set from a CSV file into a dictionary with error handling.
    
    Args:
        csv_path (str): Path to the CSV file containing skills and their categories.
        
    Returns:
        Dict[str, str]: A dictionary where keys are skills and values are their categories.
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV is malformed or missing required columns
    """
    global _skill_dict
    
    if _skill_dict is not None:
        return _skill_dict
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Skills CSV file not found: {csv_path}")
    
    try:
        with open(csv_path, 'r', encoding="utf-8") as f_csv:
            reader = csv.DictReader(f_csv)
            
            # Validate required columns
            if 'skill' not in reader.fieldnames or 'category' not in reader.fieldnames:
                raise ValueError("CSV must contain 'skill' and 'category' columns")
            
            dict_skill_set = {}
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    skill = row.get('skill', '').strip().lower()
                    category = row.get('category', '').strip().lower()
                    
                    if not skill:
                        logger.warning(f"Empty skill found at row {row_num}")
                        continue
                    
                    if not category:
                        logger.warning(f"Empty category for skill '{skill}' at row {row_num}")
                        category = 'uncategorized'
                    
                    # Handle duplicates - keep first occurrence
                    if skill in dict_skill_set:
                        logger.warning(f"Duplicate skill '{skill}' found at row {row_num}")
                    else:
                        dict_skill_set[skill] = category
                        
                except Exception as e:
                    logger.warning(f"Error processing row {row_num}: {e}")
                    continue
            
            if not dict_skill_set:
                raise ValueError("No valid skill-category pairs found in CSV")
            
            _skill_dict = dict_skill_set
            logger.info(f"Loaded {len(dict_skill_set)} skill-category pairs")
            return dict_skill_set
            
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error reading CSV: {e}")
        raise ValueError(f"Could not read CSV file due to encoding issues: {e}")
    except csv.Error as e:
        logger.error(f"CSV parsing error: {e}")
        raise ValueError(f"Malformed CSV file: {e}")
    except Exception as e:
        logger.error(f"Unexpected error loading skill dictionary: {e}")
        raise

# Initialize skill set at module level with error handling
try:
    SKILL_SET = load_skill_set(csv_path)
except Exception as e:
    logger.error(f"Failed to initialize SKILL_SET: {e}")
    SKILL_SET = set()  # Fallback to empty set

def _clean_text(text: str) -> str:
    """Clean and normalize text input with advanced preprocessing."""
    if not isinstance(text, str):
        text = str(text)
    
    # Handle common PDF extraction issues
    import re
    
    # Fix concatenated words by adding spaces before capital letters in camelCase
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # Add spaces around numbers when they're attached to letters
    text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)
    text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
    
    # Fix common word concatenations by adding spaces before common words
    common_words = ['and', 'the', 'with', 'for', 'from', 'that', 'this', 'have', 'will', 'should', 'would', 'could']
    for word in common_words:
        # Add space before these words when they appear concatenated
        pattern = r'([a-z])(' + word + r')([a-z])'
        text = re.sub(pattern, r'\1 \2 \3', text, flags=re.IGNORECASE)
    
    # Remove excessive punctuation and special characters
    text = re.sub(r'[^\w\s.-]', ' ', text)
    
    # Remove excessive dots and dashes
    text = re.sub(r'\.{2,}', ' ', text)
    text = re.sub(r'-{2,}', ' ', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove very short and very long words (likely extraction errors)
    words = text.split()
    filtered_words = []
    for word in words:
        word = word.strip('.-_')
        if 2 <= len(word) <= 30:  # Keep words between 2-30 characters
            filtered_words.append(word)
    
    text = ' '.join(filtered_words)
    
    return text.lower().strip()

def _validate_input(text: str, top_n: int) -> Tuple[str, int]:
    """Validate and clean input parameters."""
    if not text or not isinstance(text, str):
        raise ValueError("Text input must be a non-empty string")
    
    cleaned_text = _clean_text(text)
    if len(cleaned_text.strip()) < 10:
        logger.warning("Input text is very short, results may be limited")
    
    if not isinstance(top_n, int) or top_n <= 0:
        logger.warning(f"Invalid top_n value: {top_n}, using default 75")
        top_n = 75
    
    # Limit top_n to reasonable bounds to prevent memory issues
    top_n = min(max(top_n, 1), 200)
    
    return cleaned_text, top_n

@lru_cache(maxsize=100)  # Cache results for repeated queries
def extract_relevant_skills_and_keywords(text: str, top_n: int = 75) -> Set[str]:
    """
    Extracts relevant skills and keywords from text using both a curated skills dictionary
    and KeyBERT for context-aware phrase extraction.
    
    Args:
        text (str): The input resume or JD text.
        top_n (int): Number of top KeyBERT phrases to extract.
        
    Returns:
        Set[str]: Unique, relevant skills and key phrases.
        
    Raises:
        ValueError: If input validation fails
        RuntimeError: If KeyBERT processing fails
    """
    try:
        # Input validation and cleaning
        cleaned_text, validated_top_n = _validate_input(text, top_n)
        
        # Ensure we have skills loaded
        if not SKILL_SET:
            raise RuntimeError("Skills dataset not loaded. Check CSV file path and format.")
        
        # Extract keywords using KeyBERT with error handling
        try:
            kw_model = get_kw_model()
            
            # Use more conservative KeyBERT settings for better quality
            keybert_results = kw_model.extract_keywords(
                cleaned_text,
                keyphrase_ngram_range=(1, 2),  # Reduced from (1,3) to avoid long garbage phrases
                stop_words='english',
                top_n=min(validated_top_n, 50),  # Reduced top_n for better quality
                use_mmr=True,
                diversity=0.7,  # Increased diversity to avoid similar garbage phrases
                nr_candidates=20  # Limit candidates to improve quality
            )
            
            keybert_phrases = set()
            for kw, score in keybert_results:
                # Additional filtering for garbage phrases
                if (len(kw.split()) <= 3 and  # Max 3 words
                    len(kw) >= 3 and len(kw) <= 25 and  # Reasonable length
                    not re.search(r'(.)\1{3,}', kw) and  # No repeated characters (aaaa)
                    score > 0.1):  # Minimum relevance score
                    keybert_phrases.add(kw)
            
            logger.debug(f"Extracted {len(keybert_phrases)} filtered KeyBERT phrases")
            
        except Exception as e:
            logger.error(f"KeyBERT extraction failed: {e}")
            # Fallback to basic keyword extraction using spaCy if available
            nlp = _get_nlp_model()
            if nlp:
                try:
                    doc = nlp(cleaned_text)
                    keybert_phrases = set(
                        token.text.lower() for token in doc 
                        if not token.is_stop and not token.is_punct and len(token.text) > 2
                    )
                    logger.info("Fallback to spaCy extraction successful")
                except Exception as spacy_e:
                    logger.error(f"SpaCy fallback also failed: {spacy_e}")
                    keybert_phrases = set()
            else:
                keybert_phrases = set()
        
        # Match extracted phrases to known skills
        all_keywords = set()
        unmatched_keywords = set()
        
        for kw in keybert_phrases:
            try:
                matched_skill = fuzzymatching.fuzzy_skill_match(kw, SKILL_SET)
                if matched_skill:
                    all_keywords.add(matched_skill)
                else:
                    unmatched_keywords.add(kw.lower())
            except Exception as e:
                logger.warning(f"Error matching keyword '{kw}': {e}")
                continue
        
        logger.info(f"Matched {len(all_keywords)} skills, {len(unmatched_keywords)} unmatched")
        
        # If we found very few matches, include some high-confidence unmatched terms
        if len(all_keywords) < 5 and unmatched_keywords:
            # Add unmatched terms that look like technical skills
            technical_terms = {
                term for term in unmatched_keywords 
                if len(term) > 2 and any(char.isalnum() for char in term)
            }
            all_keywords.update(list(technical_terms)[:10])  # Add up to 10 technical terms
        
        return all_keywords
        
    except Exception as e:
        logger.error(f"Error in extract_relevant_skills_and_keywords: {e}")
        raise RuntimeError(f"Skill extraction failed: {e}")

# Optional utility function for cleanup (call when shutting down)
def cleanup_models():
    """Clean up loaded models to free memory."""
    global _nlp_model, _keybert_model, _skill_set, _skill_dict
    
    if _nlp_model:
        del _nlp_model
        _nlp_model = None
    
    if _keybert_model:
        del _keybert_model
        _keybert_model = None
    
    # Clear caches
    get_kw_model.cache_clear()
    extract_relevant_skills_and_keywords.cache_clear()
    
    logger.info("Models cleaned up successfully")