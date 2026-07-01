# AI-Powered Contract & Legal Document Risk Analyzer

# Project Overview

The AI-Powered Contract & Legal Document Risk Analyzer is designed to simplify the review of legal documents by automatically extracting important information, identifying potential risks, and generating concise summaries. The application supports PDF, DOCX, and TXT files, making contract analysis faster and more efficient.

This project demonstrates the practical use of Natural Language Processing (NLP), text extraction, and rule-based artificial intelligence techniques to solve a real-world business problem.

---
# Features

* User Registration and Login
* Secure Password Hashing
* Upload PDF, DOCX, and TXT Documents
* Automatic Contract Analysis
* Contract Type Detection
* Effective and Expiry Date Extraction
* Payment Term Identification
* Confidentiality Clause Detection
* Termination Clause Detection
* Renewal Clause Detection
* Responsibility Extraction
* AI-Based Risk Detection
* Executive Summary Generation
* Risk Score Calculation
* Professional PDF Report Generation
* Analysis History Dashboard

---

# Technologies Used

* Python
* Streamlit
* SQLite
* spaCy
* NLTK
* pdfplumber
* PyPDF2
* python-docx
* ReportLab
* bcrypt
* Pandas

---

# Project Structure

AI_Document_RiskAnalyzer/

│── app.py
│── database.py
│── auth.py
│── analyzer.py
│── report_generator.py
│── requirements.txt
│
├── uploads/
├── reports/
└── RiskAnalyzer.db

---

# Installation

Clone the repository

```bash
git clone https://github.com/your-username/AI-Contract-Risk-Analyzer.git
```

Move into the project folder

```bash
cd AI-Contract-Risk-Analyzer
```

Install all dependencies

```bash
pip install -r requirements.txt
```

Download the spaCy language model

```bash
python -m spacy download en_core_web_sm
```

Run the application

```bash
streamlit run app.py
```

Open your browser and visit

```
http://localhost:8501
```

---

# How It Works

1. Register a new account.
2. Log in securely.
3. Upload a legal document (PDF, DOCX, or TXT).
4. The application extracts text from the document.
5. Important contract clauses are identified.
6. Potential legal risks are highlighted.
7. An executive summary and recommendations are generated.
8. Export the analysis as a PDF report.

---

# Supported File Formats

* PDF
* DOCX
* TXT

---

# Future Improvements

* Semantic Search
* Admin Dashboard
* Role-Based Access Control
* DOCX Report Export
* AI API Integration (Gemini/OpenAI)
* Contract Comparison
* Risk Trend Dashboard

---

# Author

**Salman Nazar**

Teyzix Core Internship (AI-3)

Artificial Intelligence Project

---
