import os
import sys
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

# Use absolute imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.code_executors import execute_code
from backend.resume_analyzer import process_resume_and_posting, analysis_cache
from gh_scraper.FINAL import grift_check

class CodeRequest(BaseModel):
    code: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
    return process_resume_and_posting(resume, job_posting)

@app.post("/api/execute-code")
def execute_code_endpoint(request: CodeRequest):
    result = execute_code(request.code, request.language)
    return result

@app.get("/api/get-analysis/{hash_key}")
def get_analysis(hash_key: str):
    cached_data = analysis_cache.get_resume(hash_key)
    if not cached_data:
        return {"error": "Analysis not found"}, 404
    return cached_data

@app.post("/api/grift_check")
async def analyze_resume(
    hash: str = Form(...)
):
    try:
        # Get the base output directory from the resume analyzer
        output_dir = os.path.join(os.path.dirname(__file__), 'output', 'resumes', hash)
        
        # Find the resume PDF file
        pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
        if not pdf_files:
            raise ValueError(f"No PDF file found in {output_dir}")
        
        resume_pdf_path = os.path.join(output_dir, pdf_files[0])
        resume_json_path = os.path.join(output_dir, 'resumes_analysis.json')
        
        if not os.path.exists(resume_pdf_path):
            raise ValueError(f"Resume PDF not found at {resume_pdf_path}")
        if not os.path.exists(resume_json_path):
            raise ValueError(f"Resume analysis not found at {resume_json_path}")
        
        # Call grift check with the correct paths
        out_path = grift_check(resume_pdf_path, resume_json_path)
        
        # Make the path relative to the server root for the frontend
        relative_path = os.path.relpath(out_path, os.path.dirname(__file__))
        return {
            "out_path": f"/{relative_path.replace(os.sep, '/')}"
        }
    except Exception as e:
        print(f"Error in grift check: {str(e)}")
        return {"error": str(e)}, 500

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)