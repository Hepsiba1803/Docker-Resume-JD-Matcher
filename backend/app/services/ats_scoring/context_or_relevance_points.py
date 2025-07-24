import re

def split_into_sections(resume_text: str):
    """
    Split the resume text into sections based on standard section headers.
    Args:
        resume_text (str): The resume text.
    Returns:
        dict: A dictionary with section names as keys and their corresponding text as values.
    """
    section_headers = [
        r"(?i)^\s*(contact|contact information|contact info)\s*?:",
        r"(?i)^\s*(profile|summary|professional summary|about me|objective):\s*?",
        r"(?i)^\s*(education|academic background|educational qualification):\s*?",
        r"(?i)^\s*(experience|work experience|professional experience|employment history):\s*?",
        r"(?i)^\s*(skills|technical skills|core competencies):\s*?",
        r"(?i)^\s*(projects|project experience):\s*?",
        r"(?i)^\s*(certifications|certificates):\s*?"
    ]
    matches = []
    for pattern in section_headers:
        for m in re.finditer(pattern, resume_text, flags=re.MULTILINE):
            matches.append((m.start(), m.end(), m.group(1).strip().lower()))
    matches.sort(key=lambda x: x[0])

    if not matches:
        return {"other": resume_text.strip()}
    sections = {}
    for i, (start, end, section_name) in enumerate(matches):
        content_start = end
        content_end = matches[i+1][0] if i+1 < len(matches) else len(resume_text)
        section_content = resume_text[content_start:content_end].strip()
        sections[section_name] = section_content
    return sections

def keyword_context_points(sections: dict, jd_keywords: list, max_points=10) -> tuple:
    """
    Calculate context points based on presence of job description keywords in standard sections.
    Args:
        sections (dict): A dictionary of section names and their content.
        jd_keywords (list): A list of keywords from the job description.
        max_points (int): Maximum possible points for context scoring.
    Returns:
        tuple: (score, feedback)
    """
    found_in_context = set()
    found_in_skills = set()
    missing = set()
    context_sections = {"projects", "experience", "work experience", "professional experience"}
    skill_sections = {"skills", "technical skills", "core competencies"}
    sections = {k.lower(): v.lower() for k, v in sections.items()}
    for kw in jd_keywords:
        kw = kw.lower()
        found = False
        # Check context sections
        for sec in context_sections:
            if sec in sections and re.search(rf"\b{re.escape(kw)}\b", sections[sec]):
                found = True
                found_in_context.add(kw)
                break
        # Check skills sections only if not found in context
        if not found:
            for sec in skill_sections:
                if sec in sections and re.search(rf"\b{re.escape(kw)}\b", sections[sec]):
                    found_in_skills.add(kw)
                    found = True
                    break
        if not found:
            missing.add(kw)
    # Scoring: prioritize context matches
    total = len(jd_keywords)
    context_score = len(found_in_context) / total if total else 0
    skills_score = len(found_in_skills) / total if total else 0
    score = max_points * (0.7 * context_score + 0.3 * skills_score)

    # Feedback
    short_feedback=[]
    detailed_feedback =[]
    # SHORT FEEDBACK — show in UI panel directly (snappy + clear)

    if found_in_skills:
        short_feedback.append(
        f"Move skills like `{', '.join(sorted(list(found_in_skills)[:3]))}` from Skills to Experience or Projects to show real-world use."
    )

    if found_in_context:
        short_feedback.append(
        f"Nice! You’ve highlighted `{', '.join(sorted(list(found_in_context)[:3]))}` in real-world sections like Experience."
    )
    if not found_in_context and not found_in_skills:
        short_feedback.append(
        f"Missing important keywords like `{', '.join(sorted(list(missing)[:3]))}` — add them to boost relevance."
    )

    # DETAILED FEEDBACK — shown in tooltip or expandable panel (clarity + guidance)

    if found_in_skills:
        detailed_feedback.append(
        f"Some key terms from the job description are mentioned only in your Skills section: `{', '.join(sorted(found_in_skills))}`. "
        "To make them more impactful, mention them in Experience or Projects, showing how you used them in real work."
    )

    if found_in_context:
        detailed_feedback.append(
        f"You’ve placed these skills directly into Experience or Projects: `{', '.join(sorted(found_in_context))}`. "
        "That’s excellent — it shows practical application, not just familiarity."
    )
    if not found_in_context and not found_in_skills:
        detailed_feedback.append(
        f"Your resume doesn’t seem to reflect important JD keywords like `{', '.join(sorted(missing)[:5])}`. "
        "Try weaving them into relevant sections to better align with the role and improve ATS matching."
    )
    return score,short_feedback,detailed_feedback