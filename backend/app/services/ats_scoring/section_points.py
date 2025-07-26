import re
def section_completion(resume_text: str):
    """
    Calculate the completion score for each section of the resume using regex for header detection.

    Args:
        resume_text (str): The resume text.

    Returns:
        tuple: (section_score, list of suggestions)
    """
    # Map canonical section names to possible header variations
    section_variations = {
        "contact": [r"contact", r"contact information", r"contact info"],
        "profile": [r"profile", r"summary", r"professional summary", r"about me", r"objective"],
        "education": [r"education", r"academic background", r"educational qualification"],
        "experience": [r"experience", r"work experience", r"professional experience", r"employment history"],
        "skills": [r"skills", r"technical skills", r"core competencies" ,r"skill summary"],
        "projects": [r"projects", r"project experience",r"project"],
        "certifications": [r"certifications", r"certificates"],
    }

    found_sections = set()
    resume_lines = resume_text.lower().splitlines()

    for canonical, patterns in section_variations.items():
        # Compile a regex that matches any variation at the start of a line (possibly with punctuation)
        regex = re.compile(rf"^\s*({'|'.join(patterns)})\b[\s:]*", re.IGNORECASE)
        for line in resume_lines:
            if regex.match(line):
                found_sections.add(canonical)
                break  # No need to check more lines for this section

    missing_sections = set(section_variations.keys()) - found_sections

    max_points = 20
    points_per_section = 2
    section_score = min(len(found_sections) * points_per_section, max_points)

    suggestions = [
        f"Consider adding a '{section}' section to your resume to enhance its completeness."
        for section in missing_sections
    ]
    if not missing_sections:
        suggestions.append("Great job! Your resume includes all the standard sections.")

    return section_score, suggestions
