import re
from collections import defaultdict
from typing import Dict, List, Tuple, Set

def split_into_sections(resume_text: str) -> Dict[str, str]:
    """
    Split the resume text into sections based on standard section headers.
    
    Args:
        resume_text (str): The resume text to parse
        
    Returns:
        dict: A dictionary with section names as keys and their corresponding text as values
    """
    # Enhanced section patterns with more variations
    section_headers = [
        r"(?i)^\s*(contact|contact information|contact info|personal details)\s*:?",
        r"(?i)^\s*(profile|summary|professional summary|about me|objective|career objective)\s*:?",
        r"(?i)^\s*(education|academic background|educational qualification|academics)\s*:?",
        r"(?i)^\s*(experience|work experience|professional experience|employment history|career history)\s*:?",
        r"(?i)^\s*(skills|technical skills|core competencies|key skills|expertise)\s*:?",
        r"(?i)^\s*(projects|project experience|key projects|notable projects)\s*:?",
        r"(?i)^\s*(certifications|certificates|credentials|licenses)\s*:?",
        r"(?i)^\s*(achievements|accomplishments|awards|honors)\s*:?",
        r"(?i)^\s*(volunteering|volunteer work|community service)\s*:?"
    ]
    
    matches = []
    for pattern in section_headers:
        for m in re.finditer(pattern, resume_text, flags=re.MULTILINE):
            section_name = m.group(1).strip().lower()
            # Normalize section names for consistency
            normalized_name = normalize_section_name(section_name)
            matches.append((m.start(), m.end(), normalized_name))
    
    matches.sort(key=lambda x: x[0])
    
    if not matches:
        return {"other": resume_text.strip()}
    
    sections = {}
    for i, (start, end, section_name) in enumerate(matches):
        content_start = end
        content_end = matches[i+1][0] if i+1 < len(matches) else len(resume_text)
        section_content = resume_text[content_start:content_end].strip()
        
        # Merge duplicate sections if they exist
        if section_name in sections:
            sections[section_name] += "\n" + section_content
        else:
            sections[section_name] = section_content
    
    return sections

def normalize_section_name(section_name: str) -> str:
    """
    Normalize section names to standard categories for consistent processing.
    
    Args:
        section_name (str): Raw section name from resume
        
    Returns:
        str: Normalized section name
    """
    section_name = section_name.lower().strip()
    
    # Map variations to standard names
    if any(word in section_name for word in ['contact', 'personal']):
        return 'contact'
    elif any(word in section_name for word in ['profile', 'summary', 'about', 'objective']):
        return 'summary'
    elif any(word in section_name for word in ['education', 'academic']):
        return 'education'
    elif any(word in section_name for word in ['experience', 'employment', 'career', 'work']):
        return 'experience'
    elif any(word in section_name for word in ['skill', 'competenc', 'expertise']):
        return 'skills'
    elif any(word in section_name for word in ['project']):
        return 'projects'
    elif any(word in section_name for word in ['cert', 'credential', 'license']):
        return 'certifications'
    elif any(word in section_name for word in ['achievement', 'accomplishment', 'award', 'honor']):
        return 'achievements'
    elif any(word in section_name for word in ['volunteer', 'community']):
        return 'volunteering'
    else:
        return section_name

def is_soft_skill(keyword: str) -> bool:
    """
    Check if a keyword is a soft skill.
    
    Args:
        keyword (str): The keyword to check
        
    Returns:
        bool: True if it's a soft skill, False otherwise
    """
    soft_skills = {
        'communication', 'collaboration', 'leadership', 'teamwork', 'problem solving',
        'critical thinking', 'analytical thinking', 'decision making', 'creativity',
        'innovation', 'adaptability', 'flexibility', 'time management', 'prioritization',
        'organization', 'attention to detail', 'stakeholder management', 'verbal communication',
        'written communication', 'presentation', 'public speaking', 'active listening',
        'conflict resolution', 'negotiation', 'team leadership', 'mentoring', 'coaching',
        'project management', 'product management', 'business analysis', 'requirements gathering'
    }
    return keyword.lower().strip() in soft_skills

def get_soft_skill_suggestions(missing_soft_skills: Set[str]) -> List[str]:
    """
    Generate contextual suggestions for soft skills.
    
    Args:
        missing_soft_skills (set): Set of missing soft skills
        
    Returns:
        list: List of suggestions for incorporating soft skills
    """
    suggestions = []
    
    # Group soft skills by type for better suggestions
    skill_groups = {
        'communication': ['communication', 'verbal communication', 'written communication', 'presentation', 'public speaking'],
        'leadership': ['leadership', 'team leadership', 'mentoring', 'coaching'],
        'collaboration': ['collaboration', 'teamwork', 'stakeholder management', 'conflict resolution', 'negotiation'],
        'analytical': ['problem solving', 'critical thinking', 'analytical thinking', 'decision making'],
        'management': ['time management', 'prioritization', 'organization', 'project management', 'product management'],
        'creativity': ['creativity', 'innovation', 'adaptability', 'flexibility'],
        'business': ['business analysis', 'requirements gathering', 'attention to detail']
    }
    
    for group, skills in skill_groups.items():
        missing_in_group = [skill for skill in missing_soft_skills if skill in skills]
        if missing_in_group:
            if group == 'communication':
                suggestions.append("💬 Demonstrate communication skills through examples like 'Presented technical solutions to stakeholders', 'Documented system architecture', or 'Facilitated cross-team meetings'")
            elif group == 'leadership':
                suggestions.append("👥 Show leadership through examples like 'Led a team of X developers', 'Mentored junior developers', or 'Drove technical decisions across teams'")
            elif group == 'collaboration':
                suggestions.append("🤝 Highlight collaboration with phrases like 'Collaborated with cross-functional teams', 'Worked closely with product managers', or 'Coordinated with QA teams'")
            elif group == 'analytical':
                suggestions.append("🧠 Show analytical skills through 'Analyzed system bottlenecks', 'Debugged complex issues', or 'Optimized database queries resulting in X% improvement'")
            elif group == 'management':
                suggestions.append("⏰ Demonstrate management skills with 'Managed project timelines', 'Prioritized feature development', or 'Organized sprint planning sessions'")
            elif group == 'creativity':
                suggestions.append("💡 Show creativity and adaptability through 'Designed innovative solutions', 'Adapted to new technologies', or 'Implemented creative workarounds'")
            elif group == 'business':
                suggestions.append("📊 Highlight business skills with 'Gathered requirements from stakeholders', 'Analyzed business needs', or 'Ensured attention to detail in code reviews'")
    
    return suggestions

def enhanced_keyword_context_points(sections: Dict[str, str], jd_keywords: List[str], max_points: int = 30) -> Tuple[int, List[str], List[str]]:
    """
    Calculate enhanced context points based on keyword placement and usage patterns.
    
    Args:
        sections (dict): Dictionary of section names and their content
        jd_keywords (list): List of keywords from the job description
        max_points (int): Maximum possible points for context scoring
        
    Returns:
        tuple: (score, short_feedback, detailed_feedback)
    """
    
    # Define section categories with different weights
    context_sections = {"projects", "experience", "achievements", "volunteering"}
    skill_sections = {"skills", "certifications"}
    summary_sections = {"summary"}
    
    # Convert all sections to lowercase for case-insensitive matching
    sections_lower = {k.lower(): v.lower() for k, v in sections.items()}
    
    # Track keyword findings with more detail
    found_in_context = set()
    found_in_skills = set()
    found_in_summary = set()
    keyword_frequency = defaultdict(int)
    missing = set()
    
    # Enhanced keyword matching with frequency tracking
    for kw in jd_keywords:
        kw_lower = kw.lower().strip()
        found = False
        
        # Create word boundary pattern for better matching
        pattern = rf"\b{re.escape(kw_lower)}\b"
        
        # Check context sections (highest priority)
        for sec in context_sections:
            if sec in sections_lower:
                matches = re.findall(pattern, sections_lower[sec])
                if matches:
                    found = True
                    found_in_context.add(kw)
                    keyword_frequency[kw] += len(matches)
        
        # Check summary sections (medium priority) - only if not found in context
        if not found:
            for sec in summary_sections:
                if sec in sections_lower:
                    matches = re.findall(pattern, sections_lower[sec])
                    if matches:
                        found = True
                        found_in_summary.add(kw)
                        keyword_frequency[kw] += len(matches)
        
        # Check skills sections (lower priority) - only if not found elsewhere
        if not found:
            for sec in skill_sections:
                if sec in sections_lower:
                    matches = re.findall(pattern, sections_lower[sec])
                    if matches:
                        found_in_skills.add(kw)
                        keyword_frequency[kw] += len(matches)
                        found = True
        
        if not found:
            missing.add(kw)
    
    # Filter missing keywords to only include soft skills for context suggestions
    missing_soft_skills = {kw for kw in missing if is_soft_skill(kw)}
    
    # Enhanced scoring with multiple factors
    total_keywords = len(jd_keywords)
    if total_keywords == 0:
        return 0, ["No keywords to analyze"], ["No keywords provided for analysis"]
    
    # Calculate base scores
    context_ratio = len(found_in_context) / total_keywords
    summary_ratio = len(found_in_summary) / total_keywords
    skills_ratio = len(found_in_skills) / total_keywords
    
    # IMPROVED: More balanced weighted scoring (less harsh on skills-only matches)
    weighted_score = (0.6 * context_ratio) + (0.25 * summary_ratio) + (0.15 * skills_ratio)
    
    # IMPROVED: More generous context bonus with lower threshold
    if found_in_context and context_ratio >= 0.05:  # Lowered from 0.1 to 0.05
        context_bonus = 0.15 + (context_ratio * 0.2)  # Base 15% + up to 20% more
    else:
        context_bonus = 0
    
    # IMPROVED: Skills bonus for good skills coverage
    if skills_ratio >= 0.3:  # If 30%+ of keywords are in skills
        skills_bonus = 0.1  # 10% bonus
    else:
        skills_bonus = 0
    
    # IMPROVED: More generous frequency bonus
    avg_frequency = sum(keyword_frequency.values()) / len(keyword_frequency) if keyword_frequency else 0
    frequency_bonus = min(0.15, avg_frequency * 0.03)  # Increased cap to 15%
    
    # IMPROVED: Much gentler coverage penalty with higher threshold
    missing_ratio = len(missing) / total_keywords
    if missing_ratio > 0.8:  # Only penalize if >80% missing (was any missing)
        coverage_penalty = (missing_ratio - 0.8) * 0.15  # Gentler penalty
    else:
        coverage_penalty = 0
    
    # IMPROVED: Base score floor - everyone gets some points for trying
    base_floor = 0.2  # 20% base score
    
    # Final score calculation with improved baseline
    final_score = max_points * (
        base_floor + 
        weighted_score + 
        context_bonus + 
        skills_bonus + 
        frequency_bonus - 
        coverage_penalty
    )
    
    # IMPROVED: More generous minimum scores based on different scenarios
    total_found = len(found_in_context) + len(found_in_skills) + len(found_in_summary)
    found_ratio = total_found / total_keywords
    
    if found_ratio >= 0.1:  # If at least 10% of keywords found anywhere
        if context_ratio >= 0.05:  # Has some context
            minimum_score = max_points * 0.4  # At least 40%
        elif summary_ratio >= 0.1 or skills_ratio >= 0.2:  # Good summary or skills coverage
            minimum_score = max_points * 0.3  # At least 30%
        else:
            minimum_score = max_points * 0.25  # At least 25%
        
        final_score = max(final_score, minimum_score)
    
    # Clamp between 0 and max_points
    final_score = max(0, min(max_points, final_score))
    
    # Generate enhanced feedback
    short_feedback, detailed_feedback = generate_enhanced_feedback(
        found_in_context, found_in_skills, found_in_summary, missing_soft_skills, 
        keyword_frequency, total_keywords
    )
    
    return round(final_score), short_feedback, detailed_feedback

def generate_enhanced_feedback(found_in_context: Set[str], found_in_skills: Set[str], 
                             found_in_summary: Set[str], missing_soft_skills: Set[str], 
                             keyword_frequency: Dict[str, int], total_keywords: int) -> Tuple[List[str], List[str]]:
    """
    Generate comprehensive feedback based on keyword analysis results.
    
    Returns:
        tuple: (short_feedback, detailed_feedback)
    """
    short_feedback = []
    detailed_feedback = []
    
    # Check if this is a zero score case (no keywords found anywhere)
    total_found = len(found_in_context) + len(found_in_skills) + len(found_in_summary)
    is_zero_score = total_found == 0
    
    if is_zero_score:
        # More encouraging messaging for zero score
        short_feedback.append("🎯 This role focuses on different skills - consider roles that match your background better.")
        detailed_feedback.append(
            "🎯 While your professional experience has value, this particular role emphasizes "
            "different technical areas. Consider: (1) Targeting roles that better align with your "
            "current expertise, (2) Highlighting transferable skills, or (3) If interested in this "
            "domain, consider learning the key technologies mentioned in the job description."
        )
        return short_feedback, detailed_feedback
    
    # More encouraging regular feedback
    coverage = total_found / total_keywords
    
    # Lead with positives
    if found_in_context:
        top_context_keywords = sorted(list(found_in_context)[:3])
        short_feedback.append(
            f"🌟 Great job! You demonstrate `{', '.join(top_context_keywords)}` with real project examples."
        )
        detailed_feedback.append(
            f"Excellent contextual evidence: You show practical experience with "
            f"`{', '.join(sorted(found_in_context))}` through specific examples in your "
            "projects and work experience. This is exactly what hiring managers want to see!"
        )
    
    # Acknowledge skills section positively
    if found_in_skills:
        skills_sample = sorted(list(found_in_skills)[:4])  # Show more skills
        short_feedback.append(
            f"✅ Your skills section shows knowledge of `{', '.join(skills_sample)}`."
        )
        detailed_feedback.append(
            f"Skills foundation: You list relevant technologies `{', '.join(sorted(found_in_skills))}` "
            "in your skills section. To strengthen your application further, consider adding brief "
            "examples of how you've applied these skills in your work experience."
        )
    
    # Summary placement
    if found_in_summary:
        short_feedback.append(
            f"👍 Your summary effectively highlights `{', '.join(sorted(list(found_in_summary)[:3]))}` upfront."
        )
        detailed_feedback.append(
            f"Strong summary positioning: `{', '.join(sorted(found_in_summary))}` are prominently "
            "featured in your professional summary, immediately showcasing your relevance."
        )
    
    # IMPROVED: More encouraging coverage feedback with better thresholds
    if coverage >= 0.5:  # Lowered from 0.7
        short_feedback.append("🎯 Excellent match! Your resume shows strong alignment with this role.")
    elif coverage >= 0.25:  # Lowered from 0.4  
        short_feedback.append("👌 Good foundation! You have relevant experience for this position.")
    elif coverage >= 0.1:   # New tier
        short_feedback.append("📈 You have some relevant skills - focus on highlighting them better.")
    else:
        short_feedback.append("🔄 Consider targeting roles that better match your current expertise.")
    
    # Constructive suggestions for missing soft skills (only if they have some technical match)
    if missing_soft_skills and coverage >= 0.1:
        missing_sample = sorted(list(missing_soft_skills)[:3])  # Show fewer to be less overwhelming
        short_feedback.append(
            f"💼 Consider showcasing soft skills like `{missing_sample[0]}` through your achievements."
        )
        
        # Add specific suggestions for soft skills
        soft_skill_suggestions = get_soft_skill_suggestions(missing_soft_skills)
        if soft_skill_suggestions:
            detailed_feedback.extend(soft_skill_suggestions[:2])  # Limit to avoid overwhelming
    
    # Highlight frequency strengths
    high_freq_keywords = [kw for kw, freq in keyword_frequency.items() if freq > 1]  # Lowered threshold
    if high_freq_keywords:
        detailed_feedback.append(
            f"Consistency strength: You consistently mention `{', '.join(high_freq_keywords[:3])}` "
            "throughout your resume, demonstrating deep familiarity with these areas."
        )
    
    return short_feedback, detailed_feedback

def analyze_resume_context(resume_text: str, job_keywords: List[str]) -> Tuple[int, List[str], List[str]]:
    """
    Complete analysis of resume context and keyword alignment.
    
    Args:
        resume_text (str): Full resume text
        job_keywords (list): Keywords extracted from job description
        
    Returns:
        tuple: (score, short_feedback, detailed_feedback)
    """
    sections = split_into_sections(resume_text)
    score, short_feedback, detailed_feedback = enhanced_keyword_context_points(sections, job_keywords)
    
    # No additional zero score handling here - it's already handled in generate_enhanced_feedback
    return score, short_feedback, detailed_feedback