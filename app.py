import streamlit as st
import os
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def generate_response(message: str, system_prompt: str, temperature: float, max_tokens: int):
    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]

    response = client.chat.completions.create(
        model="llama-3.1-8B-Instant",
        messages=conversation,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False
    )

    return response.choices[0].message.content

def analyze_resume(resume_text, job_description, with_job_description, temperature, max_tokens):
    if with_job_description:
        prompt = f"""
        Analyze the following resume against the job description.
        Provide match percentage, missing keywords, and improvement suggestions.
        Job Description: {job_description}
        Resume: {resume_text}
        """
    else:
        prompt = f"""
        Analyze the resume and provide improvement suggestions.
        Resume: {resume_text}
        """
    return generate_response(prompt, "You are an expert ATS resume analyzer.", temperature, max_tokens)

def generate_cover_letter(resume_text, job_description, temperature, max_tokens):
    prompt = f"""
    Generate a compelling cover letter tailored to the job description.
    Resume: {resume_text}
    Job Description: {job_description}
    """
    return generate_response(prompt, "You are an expert in writing tailored cover letters.", temperature, max_tokens)

def generate_interview_questions(job_description, temperature, max_tokens):
    prompt = f"""
    Generate 10 interview questions based on the job description.
    Job Description: {job_description}
    """
    return generate_response(prompt, "You are an expert in creating interview questions.", temperature, max_tokens)

st.title("📄 ATS Resume Analyzer 📄")

st.sidebar.title("Navigation")
tab = st.sidebar.radio("Go to", ["Resume Analyzer", "Cover Letter Generator", "Interview Questions Generator"])

temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
max_tokens = st.sidebar.slider("Max Tokens", 100, 1000, 500)

if tab == "Resume Analyzer":
    st.header("Resume Analyzer")
    with_job_description = st.checkbox("Analyze with Job Description", True)
    job_description = st.text_area("Job Description")
    resume_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
    
    if resume_file:
        if resume_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume_file)
        else:
            resume_text = extract_text_from_docx(resume_file)
        
        if st.button("Analyze Resume"):
            result = analyze_resume(resume_text, job_description, with_job_description, temperature, max_tokens)
            st.write(result)

elif tab == "Cover Letter Generator":
    st.header("Cover Letter Generator")
    resume_text = st.text_area("Resume Content")
    job_description = st.text_area("Job Description")
    if st.button("Generate Cover Letter"):
        cover_letter = generate_cover_letter(resume_text, job_description, temperature, max_tokens)
        st.write(cover_letter)

elif tab == "Interview Questions Generator":
    st.header("Interview Questions Generator")
    job_description = st.text_area("Job Description")
    if st.button("Generate Interview Questions"):
        questions = generate_interview_questions(job_description, temperature, max_tokens)
        st.write(questions)
