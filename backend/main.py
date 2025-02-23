import datetime
import hashlib
import json
import os
import tempfile

from fastapi import FastAPI, File, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gh_scraper.FINAL import grift_check

class CodeRequest(BaseModel):
    code: str
    language: str = 'python'  # Default to Python if not specified

from .code_executors import execute_code

from resume_parsing.parse import (
    load_input,
    resume_chain,
    posting_chain
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this based on your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/api/analyze")
def analyze_resume(
    resume: UploadFile = File(...),
    job_posting: str = Form(...)
):
    try:
        # Save resume to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(resume.filename)[1]) as tmp:
            content = resume.file.read()
            tmp.write(content)
            tmp.flush()
            
            # Process resume
            resume_text = load_input(tmp.name, is_txt=resume.filename.endswith('.txt'))
            resume_result = resume_chain.invoke({"resume_text": resume_text})
            
        # Remove temporary file
        os.unlink(tmp.name)
        
        # Process job posting
        posting_result = posting_chain.invoke({"posting_text": job_posting})
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp for unique filenames
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Make directory for files via hash
        to_hash = resume.filename.encode('utf-8')
        hash = hashlib.sha256(to_hash).hexdigest()
        hashed_dir = os.path.join(output_dir, hash)
        os.makedirs(hashed_dir, exist_ok=True)
        
        # Save individual JSON files
        resume_file = os.path.join(hashed_dir, f'resume_analysis_{timestamp}.json')
        job_file = os.path.join(hashed_dir, f'job_analysis_{timestamp}.json')
        
        with open(resume_file, 'w') as f:
            json.dump(resume_result, f, indent=2)
        with open(job_file, 'w') as f:
            json.dump(posting_result, f, indent=2)
        
        return {
            "resume_analysis": resume_result,
            "job_analysis": posting_result,
            "saved_files": {
                "resume": resume_file,
                "job": job_file
            },
            "hash": hash
        }
        
    except Exception as e:
        return {"error": str(e)}, 500

@app.post("/api/execute-code")
def execute_code_endpoint(request: CodeRequest):
    try:
        result = execute_code(request.code, request.language)
        return result
    except Exception as e:
        return {"error": str(e), "success": False, "output": ""}

@app.post("/api/grift_check")
def analyze_resume(
    resume_path: str = Form(...),
    resume_data_path: str = Form(...)
):
    try:
        out_path = grift_check(resume_path, resume_data_path)
        return {
            "out_path": out_path
        }
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
