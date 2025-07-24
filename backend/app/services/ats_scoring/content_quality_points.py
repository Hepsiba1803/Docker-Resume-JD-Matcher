import re

def content_quality_score_and_suggestions(resume_text: str, max_points=15):
    """
    Scores resume content quality based on metrics, verbs, clarity, and structure.
    Returns score, short suggestions (for UI), and long-form tooltips (for deeper context).
    """
    deductions = 0
    short_feedback = []
    long_feedback = []

    # 1. Quantified Achievements
    quantified = re.findall(r'\b\d+(\.\d+)?(%|\$|k|K|m|M)?\b', resume_text)
    if not quantified:
        deductions += 5
        short_feedback.append("Missing metrics like % or $ to show results.")
        long_feedback.append(
            "Try to include quantifiable results in your bullet points. Numbers like 'increased performance by 30%' or 'managed a budget of $5,000' help convey real-world value and stand out to both recruiters and ATS systems."
        )

    # 2. Action Verbs
    action_verbs = [
        "achieved", "managed", "led", "developed", "designed", "implemented",
        "improved", "created", "increased", "reduced", "launched", "built",
        "organized", "coordinated", "analyzed", "delivered", "presented"
    ]
    action_verbs_found = [
        verb for verb in action_verbs if re.search(rf'\b{verb}\b', resume_text, re.IGNORECASE)
    ]
    if len(action_verbs_found) < 3:
        deductions += 4
        short_feedback.append("Too few strong verbs like 'led' or 'developed'.")
        long_feedback.append(
            "Start your bullet points with strong action verbs like 'developed', 'managed', or 'led'. These communicate initiative and ownership—two things recruiters look for in high-performing candidates."
        )

    # 3. Placeholder Text
    if re.search(r'lorem ipsum|dummy text|your name here', resume_text, re.IGNORECASE):
        deductions += 3
        short_feedback.append("Placeholder text still present in resume.")
        long_feedback.append(
            "Looks like your resume may still contain filler text (e.g., 'Lorem Ipsum', 'Your Name Here'). Be sure to replace all placeholders with your real information—leaving them in makes the document feel unprofessional."
        )

    # 4. Spelling/Clarity Check
    words = resume_text.split()
    suspicious_words = [w for w in words if len(w) > 4 and not re.search(r'[aeiouAEIOU]', w)]
    if len(suspicious_words) > 10:
        deductions += 2
        short_feedback.append("Possible typos or unclear wording detected.")
        long_feedback.append(
            "Some words in your resume may be misspelled or appear suspicious (like missing vowels). While this isn’t a full spellcheck, it's a hint to review your text for typos or formatting issues that reduce credibility."
        )

    # If nothing wrong, show positive feedback
    if not short_feedback:
        short_feedback.append("Content is strong and metrics-driven.")
        long_feedback.append(
            "Great job! Your resume includes measurable results, strong verbs, and clear, relevant content. This makes it compelling to both humans and ATS systems."
        )

    score = max(max_points - deductions, 0)
    return score, short_feedback, long_feedback
