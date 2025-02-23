import hashlib
import os
import tempfile
from typing import Dict, Any
from starlette.datastructures import UploadFile
from resume_parsing.parse import load_input, resume_chain, posting_chain
from joblib import Memory

memory = Memory(location='./.cache', verbose=0)

@memory.cache
def process_resume(resume_text: str) -> dict:
    return resume_chain.invoke({"resume_text": resume_text})

@memory.cache
def process_job_posting(job_posting_text: str) -> dict:
    return posting_chain.invoke({"posting_text": job_posting_text})


def process_resume_and_posting(resume: UploadFile, job_posting: str):
    """Process resume and job posting and return analysis results."""

    # Generate a unique hash for this combination of resume and job posting.
    resume_content = resume.file.read()
    resume.file.seek(0) # Reset file pointer for later use

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(resume.filename)[1]) as tmp:
        tmp.write(resume_content)
        tmp.flush()

        resume_text = load_input(tmp.name, is_txt=resume.filename.endswith('.txt'))
        resume_result = process_resume(resume_text)

    posting_result = process_job_posting(job_posting)

    return {
        "resume_analysis": resume_result,
        "job_analysis": posting_result,
    }, resume_text