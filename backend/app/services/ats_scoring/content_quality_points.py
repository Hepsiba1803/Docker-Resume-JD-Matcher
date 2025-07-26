import re
from typing import List, Tuple, Dict, Set
from collections import Counter

def enhanced_content_quality_score_and_suggestions(resume_text: str, max_points: int = 15) -> Tuple[int, List[str], List[str]]:
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
    if len(positive_findings) >= 3 and not short_feedback:
        short_feedback.append("✅ Excellent! Content is strong, metrics-driven, and professionally written.")
        long_feedback.append(
            "Outstanding content quality! Your resume demonstrates measurable results, uses strong action verbs, "
            "maintains professional tone, and follows good structural practices. This combination makes it highly "
            "compelling to both ATS systems and human recruiters."
        )
    elif len(positive_findings) >= 2:
        short_feedback.append("👍 Good content quality with room for minor improvements.")
    
    # Calculate final score
    final_score = max(max_points - deductions, 0)
    
    return final_score, short_feedback, long_feedback

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
    
    if not metrics_found:
        return 5, ["❌ Missing metrics like %, $, or numbers to show concrete results."], [
            "Quantified achievements are crucial for resume impact. Include specific metrics like "
            "'increased sales by 25%', 'managed $50K budget', or 'reduced processing time by 3 hours'. "
            "Numbers help recruiters quickly understand the scope and impact of your work."
        ], False
    elif len(metrics_found) < 3:
        return 2, ["⚠️ Add more specific metrics to strengthen impact statements."], [
            "You have some quantified results, but adding more specific metrics throughout your resume "
            "will significantly strengthen your impact statements and make achievements more compelling."
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
    
    # Scoring logic
    if total_strong_verbs < 3:
        return 4, [
            f"❌ Only {total_strong_verbs} strong action verbs found. Use more like 'led', 'developed', 'achieved'."
        ], [
            "Your resume needs more strong action verbs to convey leadership and initiative. "
            f"Currently found: {', '.join(verbs_found.keys()) if verbs_found else 'none'}. "
            "Start bullet points with impactful verbs like 'spearheaded', 'optimized', or 'delivered' "
            "instead of passive phrases like 'responsible for' or 'worked on'."
        ], False
    elif total_strong_verbs < 6:
        feedback = [f"⚠️ Good start with {total_strong_verbs} strong verbs, but add more variety for impact."]
        if weak_verbs_found:
            feedback.append(f"Replace weak phrases: '{', '.join(weak_verbs_found[:2])}'")
        return 2, feedback, [
            f"You're using some strong action verbs ({', '.join(list(verbs_found.keys())[:5])}), "
            "but adding more variety and replacing any passive language will significantly improve impact."
        ], True
    else:
        if weak_verbs_found:
            return 1, [f"⚠️ Replace passive phrases like '{weak_verbs_found[0]}' with strong action verbs."], [
                f"Great use of action verbs! Consider replacing remaining passive phrases "
                f"like '{', '.join(weak_verbs_found)}' with more dynamic language."
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
        r'n/a|not applicable|not available',
        
        # Generic/vague content
        r'\b(example|sample)\s+(project|work|experience)\b',
        r'various (tasks|duties|responsibilities)',
    ]
    
    placeholders_found = []
    for pattern in placeholder_patterns:
        matches = re.findall(pattern, resume_text, re.IGNORECASE)
        placeholders_found.extend(matches)
    
    if placeholders_found:
        return 4, [
            f"❌ Placeholder text detected: '{placeholders_found[0]}' - complete your resume."
        ], [
            f"Your resume contains placeholder or template text: {', '.join(set(placeholders_found)[:3])}. "
            "This makes the document appear unfinished and unprofessional. Replace all placeholder "
            "content with your actual information and experiences."
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
    long_sentences = [s for s in sentences if len(s.split()) > 25]
    
    if len(long_sentences) > 3:
        issues.append("overly_long_sentences")
    
    # Check for excessive use of jargon or acronyms without context
    words = resume_text.split()
    all_caps_words = [w for w in words if w.isupper() and len(w) > 2 and w.isalpha()]
    if len(all_caps_words) > 10:  # Too many acronyms might confuse readers
        issues.append("excessive_acronyms")
    
    # Check for potential typos or formatting issues
    suspicious_patterns = [
        r'\b\w*[0-9]+[a-zA-Z]+\w*\b',  # Mixed numbers and letters (potential formatting issues)
        r'\s{3,}',  # Excessive whitespace
        r'[.]{3,}',  # Multiple periods
        r'[,]{2,}',  # Multiple commas
    ]
    
    formatting_issues = 0
    for pattern in suspicious_patterns:
        if re.search(pattern, resume_text):
            formatting_issues += 1
    
    if formatting_issues >= 2:
        issues.append("formatting_issues")
    
    # Check for very short bullet points (might lack detail)
    bullet_points = re.findall(r'[•·▪▫‣⁃]\s*(.+)', resume_text)
    if not bullet_points:  # Try alternative bullet patterns
        bullet_points = re.findall(r'^\s*[-*]\s*(.+)', resume_text, re.MULTILINE)
    
    short_bullets = [bp for bp in bullet_points if len(bp.split()) < 5]
    if len(short_bullets) > len(bullet_points) * 0.3:  # More than 30% are too short
        issues.append("short_bullet_points")
    
    # Calculate deductions based on issues found
    total_deductions = 0
    feedback_short = []
    feedback_long = []
    
    if "overly_long_sentences" in issues:
        total_deductions += 1
        feedback_short.append("⚠️ Some sentences are too long - break them up for clarity.")
        feedback_long.append(
            "Several sentences exceed 25 words, which can reduce readability. "
            "Consider breaking longer sentences into shorter, more impactful statements."
        )
    
    if "excessive_acronyms" in issues:
        total_deductions += 1
        feedback_short.append("⚠️ Too many acronyms - spell out important terms first.")
        feedback_long.append(
            "Your resume contains many acronyms or technical terms. While expertise is good, "
            "ensure key terms are spelled out on first use to avoid confusing non-technical reviewers."
        )
    
    if "formatting_issues" in issues:
        total_deductions += 2
        feedback_short.append("❌ Formatting inconsistencies detected - review for errors.")
        feedback_long.append(
            "Potential formatting issues detected (irregular spacing, mixed formatting, etc.). "
            "Clean formatting is crucial for ATS systems and professional appearance."
        )
    
    if "short_bullet_points" in issues:
        total_deductions += 1
        feedback_short.append("⚠️ Several bullet points are too brief - add more detail.")
        feedback_long.append(
            "Many of your bullet points are quite short and may lack sufficient detail. "
            "Expand them to better showcase your accomplishments and responsibilities."
        )
    
    return total_deductions, feedback_short, feedback_long

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
    
    if len(all_bullets) < 3:
        return 2, ["⚠️ Use more bullet points to organize achievements clearly."], [
            "Your resume would benefit from more structured bullet points to organize your "
            "achievements and responsibilities. Bullet points make content easier to scan and understand."
        ], False
    
    # Analyze bullet point quality
    issues = []
    
    # Check for bullets starting with articles or weak words
    weak_starters = ["the", "a", "an", "i", "we", "my", "our"]
    weak_bullets = [bp for bp in all_bullets if bp.strip().lower().split()[0] in weak_starters]
    
    if len(weak_bullets) > len(all_bullets) * 0.3:
        issues.append("weak_starters")
    
    # Check for consistent structure
    action_word_bullets = [bp for bp in all_bullets if re.match(r'^\s*[A-Z][a-z]+(ed|ing|s)?\s', bp)]
    if len(action_word_bullets) < len(all_bullets) * 0.6:
        issues.append("inconsistent_structure")
    
    deductions = 0
    short_feedback = []
    long_feedback = []
    
    if "weak_starters" in issues:
        deductions += 1
        short_feedback.append("⚠️ Start bullet points with action verbs, not 'the' or 'a'.")
        long_feedback.append(
            "Many bullet points start with weak words like 'the', 'a', or 'I'. "
            "Begin with strong action verbs to immediately convey your impact and initiative."
        )
    
    if "inconsistent_structure" in issues:
        deductions += 1
        short_feedback.append("⚠️ Make bullet points more consistent - use parallel structure.")
        long_feedback.append(
            "Your bullet points lack consistent structure. Use parallel formatting where "
            "each bullet starts with an action verb and follows a similar pattern for better readability."
        )
    
    well_structured = len(issues) == 0 and len(all_bullets) >= 5
    return deductions, short_feedback, long_feedback, well_structured

def analyze_professional_tone(resume_text: str) -> Tuple[int, List[str], List[str], bool]:
    """
    NEW: Analyze professional language and tone throughout the resume.
    
    Returns:
        tuple: (deduction_points, short_feedback, long_feedback, professional_tone)
    """
    issues = []
    
    # Check for overly casual language
    casual_phrases = [
        r'\bkinda\b|\bsorta\b|\bwanna\b|\bgonna\b',
        r'\blots of\b|\ba bunch of\b|\ba ton of\b',
        r'\bawesome\b|\bcool\b|\bsweet\b|\bamazing\b',
        r'\bguys\b|\bdude\b|\byeah\b|\bokay\b',
        r'\bstuff\b|\bthings\b|\bretty good\b'
    ]
    
    for pattern in casual_phrases:
        if re.search(pattern, resume_text, re.IGNORECASE):
            issues.append("casual_language")
            break
    
    # Check for first person pronouns (should be minimal in resumes)
    first_person = re.findall(r'\b(I|me|my|mine|myself)\b', resume_text, re.IGNORECASE)
    if len(first_person) > 5:
        issues.append("excessive_first_person")
    
    # Check for negative language
    negative_phrases = [
        r'\bfailed\b|\bmistake\b|\bwrong\b|\bbad\b',
        r'\bunfortunately\b|\bsadly\b|\bpoor\b|\bterrible\b'
    ]
    
    for pattern in negative_phrases:
        if re.search(pattern, resume_text, re.IGNORECASE):
            issues.append("negative_language")
            break
    
    # Check for contractions (should be avoided in formal resumes)
    contractions = re.findall(r"\b\w+'\w+\b", resume_text)
    common_contractions = ["don't", "won't", "can't", "didn't", "hasn't", "haven't", "isn't", "aren't"]
    formal_contractions = [c for c in contractions if c.lower() in common_contractions]
    
    if len(formal_contractions) > 2:
        issues.append("contractions")
    
    # Calculate deductions and feedback
    deductions = 0
    short_feedback = []
    long_feedback = []
    
    if "casual_language" in issues:
        deductions += 2
        short_feedback.append("❌ Replace casual language with professional terminology.")
        long_feedback.append(
            "Your resume contains casual language that may not be appropriate for professional contexts. "
            "Replace informal phrases with more professional alternatives to maintain credibility."
        )
    
    if "excessive_first_person" in issues:
        deductions += 1
        short_feedback.append("⚠️ Reduce use of 'I', 'me', 'my' - use action verbs instead.")
        long_feedback.append(
            "Resumes should minimize first-person pronouns. Instead of 'I managed a team', "
            "simply write 'Managed team of X people' to create more impactful, concise statements."
        )
    
    if "negative_language" in issues:
        deductions += 2
        short_feedback.append("❌ Remove negative language - focus on positive achievements.")
        long_feedback.append(
            "Avoid negative language in your resume. Focus on positive accomplishments and "
            "learning experiences rather than failures or problems."
        )
    
    if "contractions" in issues:
        deductions += 1
        short_feedback.append("⚠️ Avoid contractions - use full words for formal tone.")
        long_feedback.append(
            "Replace contractions with full words for a more formal, professional tone. "
            "For example, use 'do not' instead of 'don't' and 'cannot' instead of 'can't'."
        )
    
    professional_tone = len(issues) == 0
    return deductions, short_feedback, long_feedback, professional_tone

# Example usage function for testing
def analyze_resume_content_quality(resume_text: str) -> Dict:
    """
    Complete content quality analysis of resume.
    
    Args:
        resume_text (str): Full resume text
        
    Returns:
        dict: Complete analysis results
    """
    score, short_feedback, detailed_feedback = enhanced_content_quality_score_and_suggestions(resume_text)
    
    return score, short_feedback, detailed_feedback