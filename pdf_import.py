import pdfplumber

def extract_questions(pdf_path):
    questions = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for line in text.split("\n"):
                if "؟" in line:
                    questions.append(line.strip())
    return questions