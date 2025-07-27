from ...services.nlp.context_keyword_extraction import extract_relevant_skills_and_keywords
from ...services.create_suggestions import create_suggestion

def compute_keyword_score_and_suggestions(job_description: str, resume_text: str) -> tuple:
    """
    Find matching keywords and calculate a score based on the number of matches.
    Find missing keywords and provide suggestions for improvement.

    Args:
        job_description (str): The job description text.
        resume_text (str): The resume text.

    Returns:
        tuple: (score, suggestions)
    """
    # Extract keywords from both job description and resume
    jd_keywords = extract_relevant_skills_and_keywords(job_description)
    resume_keywords = extract_relevant_skills_and_keywords(resume_text)
    max_points = 40
    points_per_matched_keyword = 5
    matched_keywords = jd_keywords.intersection(resume_keywords)
    missing_keywords = list(jd_keywords.difference(resume_keywords))
    score = min(len(matched_keywords) * points_per_matched_keyword, max_points)
    suggestion = "💡 Add these terms somewhere in your resume to improve ATS compatibility"
    return score, missing_keywords, suggestion
