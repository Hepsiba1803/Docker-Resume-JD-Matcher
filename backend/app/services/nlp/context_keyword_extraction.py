import spacy
import string
from keybert import KeyBERT
import csv
import os
from functools import lru_cache
from sentence_transformers import SentenceTransformer
import fuzzymatching


# Absolute path to the CSV file
csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "dataset.csv"))

# Load spaCy model (smallest version)
nlp = spacy.load('en_core_web_sm')

# Lightweight model for KeyBERT - better for limited memory (Render 512MB)
@lru_cache(maxsize=1)

def get_kw_model():
    local_model_path = "local_models/all-MiniLM-L6-v2"
    model = SentenceTransformer(local_model_path)
    return KeyBERT(model)

# Load skill set from CSV into a set
def load_skill_set(csv_path):
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        skills = set(
            row[0].strip().lower() for row in reader if row and row[0].strip()
        )
    return skills

SKILL_SET = load_skill_set(csv_path)


def extract_relevant_skills_and_keywords(text, top_n=500) -> set[str]:
    """
    Extracts relevant skills and keywords from text using both a curated skills dictionary
    and KeyBERT for context-aware phrase extraction.

    Args:
        text (str): The input resume or JD text.
        top_n (int): Number of top KeyBERT phrases to extract.

    Returns:
        set[str]: Unique, relevant skills and key phrases.
    """
    text = text.lower()

    keybert_phrases = set(
        kw for kw, _ in get_kw_model().extract_keywords(
            text,
            keyphrase_ngram_range=(1, 3),
            stop_words='english',
            top_n=top_n
        )
    )

    all_keywords = set()
    missing_keywords = set()
    for kw in keybert_phrases:
        matched_skill = fuzzymatching.fuzzy_skill_match(kw, SKILL_SET)
        if matched_skill:
            all_keywords.add(matched_skill)
        else:
            missing_keywords.add(kw.lower())
    return all_keywords

def load_skill_set_to_dict(csv_path) -> dict:
    """
    Loads the skills set from a CSV file into a dictionary.

    Args:
        csv_path (str): Path to the CSV file containing skills and their categories.

    Returns:
        dict: A dictionary where keys are skills and values are their categories.
    """
    with open(csv_path, 'r', encoding="utf-8") as f_csv:
        reader = csv.DictReader(f_csv)
        dict_skill_set = {}
        for row in reader:
            skill = row['skill'].strip().lower()
            category = row['category'].strip().lower()
            dict_skill_set[skill] = category
    return dict_skill_set
