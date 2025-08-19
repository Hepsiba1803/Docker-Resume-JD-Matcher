import re
from typing import List, Tuple, Dict, Set
from collections import Counter

def enhanced_content_quality_score_and_suggestions(resume_text: str, max_points: int = 10) -> Tuple[int, List[str], List[str]]:
    """
    Enhanced scoring of resume content quality based on metrics, verbs, clarity, and structure.
    
    Args:
        resume_text (str): The complete resume text to analyze
        max_points (int): Maximum possible points for content quality
        
    Returns:
        tuple: (score, short_feedback, detailed_feedback)
    """
    deductions = 0
    short_feedback = []
    long_feedback = []
    
    # Track positive findings for better feedback
    positive_findings = []
    
    # IMPROVED: Base score - everyone starts with some points
    base_score = 3  # Start with 30% of max points
    
    # 1. Enhanced Quantified Achievements Detection
    metrics_score, metrics_short, metrics_long, metrics_found = analyze_quantified_achievements(resume_text)
    deductions += metrics_score
    if metrics_short:
        short_feedback.extend(metrics_short)
    if metrics_long:
        long_feedback.extend(metrics_long)
    if metrics_found:
        positive_findings.append("quantified_results")
    
    # 2. Enhanced Action Verbs Analysis
    verbs_score, verbs_short, verbs_long, strong_verbs_found = analyze_action_verbs(resume_text)
    deductions += verbs_score
    if verbs_short:
        short_feedback.extend(verbs_short)
    if verbs_long:
        long_feedback.extend(verbs_long)
    if strong_verbs_found:
        positive_findings.append("strong_verbs")
    
    # 3. Enhanced Placeholder and Template Detection
    placeholder_score, placeholder_short, placeholder_long = detect_placeholder_content(resume_text)
    deductions += placeholder_score
    if placeholder_short:
        short_feedback.extend(placeholder_short)
    if placeholder_long:
        long_feedback.extend(placeholder_long)
    
    # 4. Improved Content Clarity and Professional Language
    clarity_score, clarity_short, clarity_long = analyze_content_clarity(resume_text)
    deductions += clarity_score
    if clarity_short:
        short_feedback.extend(clarity_short)
    if clarity_long:
        long_feedback.extend(clarity_long)
    
    # 5. NEW: Bullet Point Structure Analysis
    structure_score, structure_short, structure_long, well_structured = analyze_bullet_structure(resume_text)
    deductions += structure_score
    if structure_short:
        short_feedback.extend(structure_short)
    if structure_long:
        long_feedback.extend(structure_long)
    if well_structured:
        positive_findings.append("good_structure")
    
    # 6. NEW: Professional Language and Tone Check
    tone_score, tone_short, tone_long, professional_tone = analyze_professional_tone(resume_text)
    deductions += tone_score
    if tone_short:
        short_feedback.extend(tone_short)
    if tone_long:
        long_feedback.extend(tone_long)
    if professional_tone:
        positive_findings.append("professional_tone")
    
    # Generate positive feedback if content is strong
    if len(positive_findings) >= 3 and len(short_feedback) <= 1:  # Allow minor issues
        short_feedback.insert(0, "✅ Excellent! Content is strong, metrics-driven, and professionally written.")
        long_feedback.insert(0,
            "Outstanding content quality! Your resume demonstrates measurable results, uses strong action verbs, "
            "maintains professional tone, and follows good structural practices. This combination makes it highly "
            "compelling to both ATS systems and human recruiters."
        )
    elif len(positive_findings) >= 2:
        short_feedback.insert(0, "👍 Good content quality with room for minor improvements.")
    
    # IMPROVED: Calculate final score with base + bonus system
    bonus_points = len(positive_findings)  # Bonus for good practices
    final_score = base_score + bonus_points - (deductions * 0.8)  # Reduced deduction impact
    
    # Ensure score is within bounds
    final_score = max(0, min(max_points, final_score))
    
    return round(final_score), short_feedback, long_feedback

def analyze_quantified_achievements(resume_text: str) -> Tuple[int, List[str], List[str], bool]:
    """
    Enhanced analysis of quantified achievements and metrics in resume content.
    
    Returns:
        tuple: (deduction_points, short_feedback, long_feedback, found_metrics)
    """
    # Enhanced patterns for different types of metrics
    metric_patterns = [
        # Percentages and ratios
        r'\b\d+(\.\d+)?%\b',
        r'\b\d+(\.\d+)?:\d+\b',  # ratios like 3:1
        
        # Money and financial figures  
        r'\$\d+(\.\d+)?[kmKM]?\b',
        r'\b\d+(\.\d+)?[kmKM]?\s*(dollars?|USD|revenue|budget|savings?|cost)\b',
        
        # Time-based metrics
        r'\b\d+(\.\d+)?\s*(years?|months?|weeks?|days?|hours?)\b',
        
        # Scale and volume metrics
        r'\b\d+(\.\d+)?[kmKM]?\s*(users?|customers?|clients?|people|employees?|projects?|products?)\b',
        
        # Performance metrics
        r'\b(increased?|improved?|reduced?|decreased?|grew|boosted)\s+.*?by\s+\d+(\.\d+)?%?\b',
        r'\b\d+(\.\d+)?x\s+(faster|better|more|improvement)\b',
        
        # General numbers with context
        r'\b\d{2,}(\.\d+)?[+]?\s*(items?|records?|applications?|cases?)\b'
    ]
    
    metrics_found = []
    for pattern in metric_patterns:
        matches = re.findall(pattern, resume_text, re.IGNORECASE)
        metrics_found.extend(matches)
    
    # IMPROVED: More generous scoring
    if not metrics_found:
        return 3, ["⚠️ Add specific metrics like %, $, or numbers to show concrete results."], [
            "Quantified achievements make your resume more compelling. Consider adding specific metrics like "
            "'increased sales by 25%', 'managed $50K budget', or 'reduced processing time by 3 hours'. "
            "Numbers help recruiters quickly understand the scope and impact of your work."
        ], False
    elif len(metrics_found) < 2:  # Reduced from 3
        return 1, ["💡 Good start! Add a few more specific metrics to strengthen impact."], [
            "You have some quantified results, which is great! Adding a few more specific metrics throughout "
            "your resume will make your achievements even more compelling to hiring managers."
        ], True
    else:
        return 0, [], [], True

def analyze_action_verbs(resume_text: str) -> Tuple[int, List[str], List[str], bool]:
    """
    Enhanced analysis of action verbs with categorization and variety assessment.
    
    Returns:
        tuple: (deduction_points, short_feedback, long_feedback, strong_verbs_found)
    """
    # Categorized action verbs for better analysis
    leadership_verbs = [
        "led", "managed", "supervised", "directed", "coordinated", "guided", 
        "mentored", "coached", "oversaw", "spearheaded", "championed"
    ]
    
    achievement_verbs = [
        "achieved", "accomplished", "delivered", "exceeded", "surpassed", 
        "completed", "finished", "attained", "secured", "won"
    ]
    
    creation_verbs = [
        "developed", "designed", "created", "built", "established", "founded", 
        "launched", "initiated", "pioneered", "innovated", "crafted"
    ]
    
    improvement_verbs = [
        "improved", "enhanced", "optimized", "streamlined", "upgraded", 
        "modernized", "revitalized", "transformed", "revolutionized"
    ]
    
    analytical_verbs = [
        "analyzed", "evaluated", "assessed", "researched", "investigated", 
        "examined", "reviewed", "studied", "identified", "discovered"
    ]
    
    all_strong_verbs = leadership_verbs + achievement_verbs + creation_verbs + improvement_verbs + analytical_verbs
    
    # Find verbs and categorize them
    verbs_found = {}
    total_strong_verbs = 0
    
    for verb in all_strong_verbs:
        count = len(re.findall(rf'\b{verb}(ed|ing|s)?\b', resume_text, re.IGNORECASE))
        if count > 0:
            verbs_found[verb] = count
            total_strong_verbs += count
    
    # Check for weak verbs that should be avoided
    weak_verbs = ["responsible for", "duties included", "worked on", "helped with", "assisted in"]
    weak_verbs_found = []
    for weak_phrase in weak_verbs:
        if re.search(rf'\b{weak_phrase}\b', resume_text, re.IGNORECASE):
            weak_verbs_found.append(weak_phrase)
    
    # IMPROVED: More generous scoring logic
    if total_strong_verbs < 2:  # Reduced from 3
        return 2, [  # Reduced from 4
            f"💡 Add more strong action verbs like 'led', 'developed', 'achieved' (found {total_strong_verbs})."
        ], [
            "Your resume would benefit from more strong action verbs to convey leadership and initiative. "
            f"Currently found: {', '.join(verbs_found.keys()) if verbs_found else 'none'}. "
            "Start bullet points with impactful verbs like 'spearheaded', 'optimized', or 'delivered'."
        ], False
    elif total_strong_verbs < 4:  # Reduced from 6
        feedback = [f"👍 Good use of action verbs ({total_strong_verbs} found)! Consider adding more variety."]
        if weak_verbs_found:
            feedback.append(f"💡 Try replacing '{weak_verbs_found[0]}' with stronger language.")
        return 1, feedback, [  # Reduced from 2
            f"You're using some strong action verbs ({', '.join(list(verbs_found.keys())[:5])}), "
            "which is excellent! Adding more variety will make your impact even clearer."
        ], True
    else:
        if weak_verbs_found:
            return 0, [f"👍 Great action verbs! Small tip: consider replacing '{weak_verbs_found[0]}'."], [
                f"Excellent use of action verbs! You might consider replacing any remaining passive phrases "
                f"like '{', '.join(weak_verbs_found[:2])}' for even stronger impact."
            ], True
        return 0, [], [], True

def detect_placeholder_content(resume_text: str) -> Tuple[int, List[str], List[str]]:
    """
    Enhanced detection of placeholder content, templates, and incomplete sections.
    
    Returns:
        tuple: (deduction_points, short_feedback, long_feedback)
    """
    placeholder_patterns = [
        # Classic placeholders
        r'lorem ipsum|dummy text|placeholder|sample text',
        r'your name here|enter your|insert your|add your',
        r'\[your \w+\]|\[insert \w+\]|\[add \w+\]',
        
        # Template-specific patterns
        r'company name|job title|start date|end date',
        r'description here|details here|information here',
        r'skills go here|experience here|education here',
        
        # Incomplete entries
        r'tbd|to be determined|coming soon|under construction',
        
        # Generic/vague content
        r'\b(example|sample)\s+(project|work|experience)\b',
    ]
    
    placeholders_found = []
    for pattern in placeholder_patterns:
        matches = re.findall(pattern, resume_text, re.IGNORECASE)
        placeholders_found.extend(matches)
    
    if placeholders_found:
        return 3, [  # Reduced from 4
            f"⚠️ Complete placeholder text: '{placeholders_found[0]}'"
        ], [
            f"Your resume contains placeholder or template text: {', '.join(set(placeholders_found)[:2])}. "
            "Replace this content with your actual information to maintain professionalism."
        ]
    
    return 0, [], []

def analyze_content_clarity(resume_text: str) -> Tuple[int, List[str], List[str]]:
    """
    Enhanced analysis of content clarity, readability, and professional language.
    
    Returns:
        tuple: (deduction_points, short_feedback, long_feedback)
    """
    issues = []
    
    # Check for overly long sentences (potential clarity issues)
    sentences = re.split(r'[.!?]+', resume_text)
    long_sentences = [s for s in sentences if len(s.split()) > 30]  # Increased from 25
    
    if len(long_sentences) > 5:  # Increased threshold
        issues.append("overly_long_sentences")
    
    # Check for excessive use of jargon or acronyms without context
    words = resume_text.split()
    all_caps_words = [w for w in words if w.isupper() and len(w) > 2 and w.isalpha()]
    if len(all_caps_words) > 15:  # Increased from 10
        issues.append("excessive_acronyms")
    
    # Check for potential formatting issues (more lenient)
    suspicious_patterns = [
        r'\s{5,}',  # Changed from 3+ to 5+ spaces
        r'[.]{4,}',  # Changed from 3+ to 4+ periods
        r'[,]{3,}',  # Changed from 2+ to 3+ commas
    ]
    
    formatting_issues = 0
    for pattern in suspicious_patterns:
        if re.search(pattern, resume_text):
            formatting_issues += 1
    
    if formatting_issues >= 3:  # Increased threshold
        issues.append("formatting_issues")
    
    # Check for very short bullet points (more lenient)
    bullet_points = re.findall(r'[•·▪▫‣⁃]\s*(.+)', resume_text)
    if not bullet_points:
        bullet_points = re.findall(r'^\s*[-*]\s*(.+)', resume_text, re.MULTILINE)
    
    short_bullets = [bp for bp in bullet_points if len(bp.split()) < 3]  # Reduced from 5
    if len(short_bullets) > len(bullet_points) * 0.5:  # Increased from 30% to 50%
        issues.append("short_bullet_points")
    
    # IMPROVED: Calculate deductions based on issues found (more lenient)
    total_deductions = 0
    feedback_short = []
    feedback_long = []
    
    if "overly_long_sentences" in issues:
        total_deductions += 0.5  # Reduced from 1
        feedback_short.append("💡 Consider shortening very long sentences for clarity.")
        feedback_long.append(
            "Some sentences are quite lengthy. Breaking them into shorter statements "
            "can improve readability for both ATS systems and human reviewers."
        )
    
    if "excessive_acronyms" in issues:
        total_deductions += 0.5  # Reduced from 1
        feedback_short.append("💡 Consider spelling out key acronyms on first use.")
        feedback_long.append(
            "Your resume shows strong technical expertise! To ensure accessibility for all reviewers, "
            "consider spelling out important acronyms on their first use."
        )
    
    if "formatting_issues" in issues:
        total_deductions += 1  # Reduced from 2
        feedback_short.append("⚠️ Clean up formatting for professional appearance.")
        feedback_long.append(
            "Some formatting inconsistencies were detected. Clean formatting helps with "
            "both ATS parsing and professional presentation."
        )
    
    if "short_bullet_points" in issues:
        total_deductions += 0.5  # Reduced from 1
        feedback_short.append("💡 Expand brief bullet points with more detail.")
        feedback_long.append(
            "Some bullet points could be expanded with more specific details about "
            "your accomplishments and the impact of your work."
        )
    
    return round(total_deductions), feedback_short, feedback_long

def analyze_bullet_structure(resume_text: str) -> Tuple[int, List[str], List[str], bool]:
    """
    NEW: Analyze the structure and quality of bullet points in the resume.
    
    Returns:
        tuple: (deduction_points, short_feedback, long_feedback, well_structured)
    """
    # Find bullet points using various patterns
    bullet_patterns = [
        r'[•·▪▫‣⁃]\s*(.+)',  # Unicode bullets
        r'^\s*[-*]\s*(.+)',   # Dash or asterisk bullets
        r'^\s*\d+\.\s*(.+)',  # Numbered lists
    ]
    
    all_bullets = []
    for pattern in bullet_patterns:
        bullets = re.findall(pattern, resume_text, re.MULTILINE)
        all_bullets.extend(bullets)
    
    if len(all_bullets) < 2:  # Reduced from 3
        return 1, ["💡 Use bullet points to organize achievements more clearly."], [  # Reduced from 2
            "Your resume would benefit from structured bullet points to organize your "
            "achievements and responsibilities. Bullet points make content easier to scan."
        ], False
    
    # Analyze bullet point quality (more lenient)
    issues = []
    
    # Check for bullets starting with weak words
    weak_starters = ["the", "a", "an", "i", "we", "my", "our"]
    weak_bullets = [bp for bp in all_bullets if bp.strip().lower().split()[0] in weak_starters]
    
    if len(weak_bullets) > len(all_bullets) * 0.5:  # Increased from 30% to 50%
        issues.append("weak_starters")
    
    # Check for consistent structure (more lenient)
    action_word_bullets = [bp for bp in all_bullets if re.match(r'^\s*[A-Z][a-z]+(ed|ing|s)?\s', bp)]
    if len(action_word_bullets) < len(all_bullets) * 0.4:  # Reduced from 60% to 40%
        issues.append("inconsistent_structure")
    
    deductions = 0
    short_feedback = []
    long_feedback = []
    
    if "weak_starters" in issues:
        deductions += 0.5  # Reduced from 1
        short_feedback.append("💡 Start more bullets with action verbs instead of 'the' or 'a'.")
        long_feedback.append(
            "Consider starting more bullet points with strong action verbs to immediately "
            "convey your impact and achievements."
        )
    
    if "inconsistent_structure" in issues:
        deductions += 0.5  # Reduced from 1
        short_feedback.append("💡 Try using more consistent bullet point structure.")
        long_feedback.append(
            "More consistent bullet point structure (parallel formatting) can improve "
            "readability and professional appearance."
        )
    
    well_structured = len(issues) == 0 and len(all_bullets) >= 3  # Reduced from 5
    return round(deductions), short_feedback, long_feedback, well_structured

def analyze_professional_tone(resume_text: str) -> Tuple[int, List[str], List[str], bool]:
    """
    NEW: Analyze professional language and tone throughout the resume.
    
    Returns:
        tuple: (deduction_points, short_feedback, long_feedback, professional_tone)
    """
    issues = []
    
    # Check for overly casual language (more specific)
    casual_phrases = [
        r'\bkinda\b|\bsorta\b|\bwanna\b|\bgonna\b',
        r'\ba bunch of\b|\ba ton of\b',
        r'\bawesome\b|\bsweet\b',  # Removed 'cool' and 'amazing' as they can be contextually appropriate
        r'\bguys\b|\bdude\b|\byeah\b',
        r'\bstuff\b(?!\s+like)|\bretty good\b'  # Allow "stuff like" but not standalone "stuff"
    ]
    
    for pattern in casual_phrases:
        if re.search(pattern, resume_text, re.IGNORECASE):
            issues.append("casual_language")
            break
    
    # Check for first person pronouns (more lenient)
    first_person = re.findall(r'\b(I|me|my|mine|myself)\b', resume_text, re.IGNORECASE)
    if len(first_person) > 8:  # Increased from 5
        issues.append("excessive_first_person")
    
    # Check for negative language (more specific)
    negative_phrases = [
        r'\bfailed\b|\bmistake\b|\bbad\b',  # Removed 'wrong' as it can be contextual
        r'\bunfortunately\b|\bterrible\b'  # Removed 'sadly' and 'poor' as they can be contextual
    ]
    
    for pattern in negative_phrases:
        if re.search(pattern, resume_text, re.IGNORECASE):
            issues.append("negative_language")
            break
    
    # Check for contractions (more lenient)
    contractions = re.findall(r"\b\w+'\w+\b", resume_text)
    common_contractions = ["don't", "won't", "can't", "didn't", "hasn't", "haven't", "isn't", "aren't"]
    formal_contractions = [c for c in contractions if c.lower() in common_contractions]
    
    if len(formal_contractions) > 4:  # Increased from 2
        issues.append("contractions")
    
    # IMPROVED: Calculate deductions and feedback (more encouraging)
    deductions = 0
    short_feedback = []
    long_feedback = []
    
    if "casual_language" in issues:
        deductions += 1  # Reduced from 2
        short_feedback.append("💡 Consider using more formal language throughout.")
        long_feedback.append(
            "Some casual expressions were found. Using more formal, professional language "
            "throughout your resume will strengthen its impact with hiring managers."
        )
    
    if "excessive_first_person" in issues:
        deductions += 0.5  # Reduced from 1
        short_feedback.append("💡 Reduce first-person pronouns - use action verbs instead.")
        long_feedback.append(
            "Consider reducing first-person pronouns for a more direct, impactful style. "
            "Instead of 'I managed a team', try 'Managed team of X people'."
        )
    
    if "negative_language" in issues:
        deductions += 1  # Reduced from 2
        short_feedback.append("💡 Focus on positive achievements rather than problems.")
        long_feedback.append(
            "Focus on positive accomplishments and learning experiences to maintain "
            "an optimistic, forward-looking tone throughout your resume."
        )
    
    if "contractions" in issues:
        deductions += 0.5  # Reduced from 1
        short_feedback.append("💡 Consider avoiding contractions for formal tone.")
        long_feedback.append(
            "Using full words instead of contractions can enhance the professional tone. "
            "For example, 'do not' instead of 'don't'."
        )
    
    professional_tone = len(issues) <= 1  # Allow one minor issue
    return round(deductions), short_feedback, long_feedback, professional_tone

# Example usage function for testing
def analyze_resume_content_quality(resume_text: str) -> Tuple[int, List[str], List[str]]:
    """
    Complete content quality analysis of resume.
    
    Args:
        resume_text (str): Full resume text
        
    Returns:
        tuple: (score, short_feedback, detailed_feedback)
    """
    return enhanced_content_quality_score_and_suggestions(resume_text)