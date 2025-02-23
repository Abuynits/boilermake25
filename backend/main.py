from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .code_executors import execute_code
from .resume_analyzer import process_resume_and_posting, analysis_cache

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
    try:
        return process_resume_and_posting(resume, job_posting)
    except Exception as e:
        return {"error": str(e)}, 500

@app.post("/api/execute-code")
def execute_code_endpoint(request: CodeRequest):
    try:
        result = execute_code(request.code, request.language)
        return result
    except Exception as e:
        return {"error": str(e), "success": False, "output": ""}

@app.get("/api/get-analysis/{hash_key}")
def get_analysis(hash_key: str):
    cached_data = analysis_cache.get(hash_key)
    if not cached_data:
        return {"error": "Analysis not found"}, 404
    return cached_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)