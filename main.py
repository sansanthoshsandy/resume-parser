# -----------------------------
# IMPORT LIBRARIES
# -----------------------------
import streamlit as st
import re
import pandas as pd
import pdfplumber
from docx import Document
import datetime
import base64

# spaCy safe import (Cloud ready)
import spacy
from spacy.cli import download

# -----------------------------
# LOAD SPACY MODEL (AUTO DOWNLOAD)
# -----------------------------
try:
    nlp = spacy.load("en_core_web_sm")
except:
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="NLP Resume Parser", layout="centered")

# -----------------------------
# BACKGROUND IMAGE (LOCAL FILE)
# -----------------------------
def add_bg_from_local(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ❗IMPORTANT:
# On Streamlit Cloud, LOCAL PC PATH WILL NOT WORK
# Use image inside project folder (example: "assets/bg.png")
add_bg_from_local("resume-parser.png")

# -----------------------------
# EXTRACT TEXT FROM PDF
# -----------------------------
def extract_text_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# -----------------------------
# EXTRACT TEXT FROM DOCX
# -----------------------------
def extract_text_docx(file):
    doc = Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# -----------------------------
# EXTRACT EMAIL
# -----------------------------
def extract_email(text):
    text = text.replace("(at)", "@").replace(" at ", "@")
    text = text.replace("(dot)", ".").replace(" dot ", ".")
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    emails = re.findall(pattern, text)
    return emails[0] if emails else "Not Found"

# -----------------------------
# EXTRACT PHONE NUMBER
# -----------------------------
def extract_phone(text):
    phones = re.findall(r"\b\d{10}\b", text)
    return phones[0] if phones else "Not Found"

# -----------------------------
# EXTRACT NAME
# -----------------------------
def extract_name(text):
    lines = text.split("\n")

    # First 5 lines heuristic
    for line in lines[:5]:
        line = line.strip()
        if 2 <= len(line.split()) <= 4:
            return line

    # spaCy fallback
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text

    return "Not Found"

# -----------------------------
# EXTRACT SKILLS
# -----------------------------
def extract_skills(text):
    skills_list = [
        "python", "sql", "excel", "nlp", "machine learning",
        "deep learning", "power bi", "tableau",
        "data analysis", "c++", "java"
    ]

    text = text.lower()
    found = [skill for skill in skills_list if skill in text]
    return list(set(found))

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.title("📄 NLP Resume Parser")
st.write("Upload your resume (PDF or DOCX)")

uploaded_file = st.file_uploader("Choose Resume File", type=["pdf", "docx"])

# -----------------------------
# MAIN LOGIC
# -----------------------------
if uploaded_file:

    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_pdf(uploaded_file)
    else:
        resume_text = extract_text_docx(uploaded_file)

    name = extract_name(resume_text)
    email = extract_email(resume_text)
    phone = extract_phone(resume_text)
    skills = extract_skills(resume_text)

    personal_link = "https://www.linkedin.com/in/your-profile"

    # Display Output
    st.markdown(
        f"""
        <div style="background-color: rgba(255,255,255,0.85);
                    padding: 20px; border-radius: 10px;">
        <h4>✅ Extracted Information</h4>
        <p><b>Name:</b> {name}</p>
        <p><b>Email:</b> {email}</p>
        <p><b>Phone:</b> {phone}</p>
        <p><b>Skills:</b> {', '.join(skills)}</p>
        <p><b>Profile:</b> <a href="{personal_link}" target="_blank">{personal_link}</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Save to Excel
    df = pd.DataFrame([{
        "Name": name,
        "Email": email,
        "Phone": phone,
        "Skills": ", ".join(skills),
        "Profile Link": personal_link
    }])

    filename = f"resume_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(filename, index=False)

    st.success("📁 Excel file generated successfully")

    with open(filename, "rb") as f:
        st.download_button(
            "📥 Download Excel",
            data=f,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
