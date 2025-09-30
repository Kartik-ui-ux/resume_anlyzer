import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from analyzer import extract_text, analyze_resume
from generate_pdf import generate_pdf_report
import uuid


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



@app.route('/')
def home():
    return render_template('index.html')


def extract_keywords(text, top_n=10):
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    # Extract nouns and proper nouns as keywords
    keywords = [token.lemma_.lower() for token in doc if token.pos_ in ("NOUN", "PROPN") and not token.is_stop]
    from collections import Counter
    most_common = Counter(keywords).most_common(top_n)
    return [kw for kw, _ in most_common]

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    resume = request.files['resume']
    job_desc = request.form.get("job_description", "")

    filename = secure_filename(resume.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    resume.save(filepath)

    try:
        with open(filepath, "rb") as f:
            text = extract_text(f)
            result = analyze_resume(text, job_desc)
            # Add new feature: extract top keywords from resume
            result['keywords'] = extract_keywords(text, top_n=10)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        os.remove(filepath)

    return jsonify(result)

@app.route('/download-report', methods=['POST'])
def download_report():
    data = request.json
    # data contains summary, score, feedback, match_score, keywords
    filename = f"Resume_Report_{uuid.uuid4().hex}.pdf"
    path = generate_pdf_report(
        summary=data.get('summary', ''),
        score=data.get('score', 0),
        feedback=data.get('feedback', []),
        match_score=data.get('match_score'),
        ai_summary=None,  # No AI summary
        keywords=data.get('keywords', []),
        probability=data.get('probability'),
        template=data.get('template'),
        template_text=data.get('template_text'),
        filename=filename
    )
    return send_file(path, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(debug=True)
