def enhanced_keyword_context_points(sections: Dict[str, str], jd_keywords: List[str], max_points: int = 30) -> Tuple[float, List[str], List[str]]:
    """
    Calculate enhanced context points with more balanced scoring.
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
        return 0.0, ["No keywords to analyze"], ["No keywords provided for analysis"]
    
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
    
    # Frequency bonus: reward repeated usage of important keywords
    avg_frequency = sum(keyword_frequency.values()) / len(keyword_frequency) if keyword_frequency else 0
    frequency_bonus = min(0.15, avg_frequency * 0.03)  # Increased cap to 15%
    
    # IMPROVED: Much gentler coverage penalty with higher threshold
    missing_ratio = len(missing) / total_keywords
    if missing_ratio > 0.8:  # Only penalize if >80% missing (was any missing)
        coverage_penalty = (missing_ratio - 0.8) * 0.2  # Gentler penalty
    else:
        coverage_penalty = 0
    
    # IMPROVED: Base score floor - everyone gets some points for trying
    base_floor = 0.15  # 15% base score
    
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
            minimum_score = max_points * 0.35  # At least 35%
        elif summary_ratio >= 0.1 or skills_ratio >= 0.2:  # Good summary or skills coverage
            minimum_score = max_points * 0.25  # At least 25%
        else:
            minimum_score = max_points * 0.2   # At least 20%
        
        final_score = max(final_score, minimum_score)
    
    # Clamp between 0 and max_points
    final_score = max(0, min(max_points, final_score))
    
    # Generate enhanced feedback
    short_feedback, detailed_feedback = generate_enhanced_feedback(
        found_in_context, found_in_skills, found_in_summary, missing_soft_skills, 
        keyword_frequency, total_keywords
    )
    
    return round(final_score, 1), short_feedback, detailed_feedback


def generate_enhanced_feedback(found_in_context: Set[str], found_in_skills: Set[str], 
                             found_in_summary: Set[str], missing_soft_skills: Set[str], 
                             keyword_frequency: Dict[str, int], total_keywords: int) -> Tuple[List[str], List[str]]:
    """
    Generate more encouraging and constructive feedback.
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
            f"💼 Consider showcasing soft skills like `{', '.join(missing_sample)}` through your achievements."
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