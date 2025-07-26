from rapidfuzz import process, fuzz

def normalize_skill(text):
    """
    Normalize text for robust skill matching.
    """
    return text.lower().strip().replace('.', '').replace('#', ' sharp').replace('+', ' plus ')


# synonym_map: maps variants and common alternate skill names to canonical skill names
synonym_map = {
    "js": "javascript",
    "javascript": "javascript",
    "nodejs": "node.js",
    "node.js": "node.js",
    "c-sharp": "c#",
    "html5": "html",
    "css3": "css",
    "py": "python",
    "python": "python",
    "golang": "go",
    "go": "golang",
    "reactjs": "react",
    "react": "react",
    "vuejs": "vue.js",
    "vue.js": "vue.js",
    
    
    # Add more variants as you discover them
}


def map_to_canonical(skill: str) -> str:
    """
    Map skill variant to canonical form using synonym_map.
    """
    norm = normalize_skill(skill)
    return synonym_map.get(norm, norm)

def fuzzy_skill_match(extracted_kw: str, skill_set: set, threshold: int = 90) -> str or None:
    """
    Fuzzy match an extracted keyword to a skill in the curated skill set.
    Applies synonym mapping before fuzzy matching.
    """
    # Map extracted keyword to canonical form first
    normalized_kw = map_to_canonical(extracted_kw)
    
    # Normalize skill set for matching
    normalized_skills = [normalize_skill(s) for s in skill_set]
    
    # Get best fuzzy match and score
    match, score, _ = process.extractOne(normalized_kw, normalized_skills, scorer=fuzz.ratio)
    if score >= threshold:
        # Return the original skill string (before normalization)
        idx = normalized_skills.index(match)
        return list(skill_set)[idx]  # assumes skill_set order stable or convert to list once outside
    return None
