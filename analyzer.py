import PyPDF2
import docx
import spacy
import nltk
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')
nlp = spacy.load("en_core_web_sm")

def extract_text(file):
    text = ""
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        raise ValueError("Unsupported file type.")
    return text


def analyze_resume(text, job_desc=""):
    doc = nlp(text)
    word_count = len([token.text for token in doc if token.is_alpha])
    stop_words = set(stopwords.words("english"))

    must_have = ["experience", "education", "skills", "projects"]
    found = [s for s in must_have if s in text.lower()]

    score = 0
    feedback = []

    for section in must_have:
        if section in text.lower():
            score += 2
        else:
            feedback.append(f"Missing section: {section.title()}")

    if word_count < 150:
        feedback.append("Too short. Add more detail.")
    elif word_count > 800:
        feedback.append("Too long. Be more concise.")
    else:
        score += 2

    filler = ["hardworking", "team player", "go-getter", "synergy"]
    used = [word for word in filler if word in text.lower()]
    if used:
        feedback.append(f"Try to avoid buzzwords: {', '.join(used)}")
    else:
        score += 1

    if len([s for s in doc.sents if len(s.text.split()) < 3]) > 2:
        feedback.append("Some sentences are too short or fragmented.")
    else:
        score += 1

    final_score = min(score, 10)
    summary = f"Resume has ~{word_count} words and covers {len(found)}/4 key sections."
    match_score = None

    if job_desc:
        job_doc = nlp(job_desc.lower())
        job_keywords = [t.lemma_ for t in job_doc if t.is_alpha and not t.is_stop]
        resume_keywords = [t.lemma_ for t in doc if t.is_alpha and not t.is_stop]
        common = set(job_keywords) & set(resume_keywords)
        match_score = round(len(common) / len(set(job_keywords)) * 100) if job_keywords else 0
        feedback.append(f"Job Match Score: {match_score}%")

    # New Feature: Probability of Selection (simple heuristic)
    # Probability is based on score and match_score if available
    if match_score is not None:
        probability = min(95, max(10, int(0.5 * final_score * 10 + 0.5 * match_score)))
    else:
        probability = min(90, max(10, final_score * 10))

    # New Feature: Resume Template Suggestion (simple)
    # Suggest a template based on detected sections
    template = "Basic"
    if len(found) == 4:
        template = "Professional (All sections present)"
    elif len(found) >= 2:
        template = "Intermediate (Add missing sections for best results)"
    else:
        template = "Starter (Add Experience, Education, Skills, Projects)"

    template_text = (
        f"--- Resume Template Suggestion ---\n"
        f"Name\nContact Information\n\n"
        f"Education\n[Degree], [Institution], [Year]\n\n"
        f"Experience\n[Job Title], [Company], [Year-Year]\n- [Responsibility/achievement]\n\n"
        f"Skills\n- [Skill 1]\n- [Skill 2]\n\n"
        f"Projects\n- [Project Title]: [Short Description]\n\n"
        f"Awards/Certifications (Optional)\n- [Award/Certification]\n\n"
        f"Interests (Optional)\n- [Interest]"
    )

    return {
        "summary": summary,
        "score": final_score,
        "feedback": feedback,
        "match_score": match_score,
        "probability": probability,
        "template": template,
        "template_text": template_text
    }
