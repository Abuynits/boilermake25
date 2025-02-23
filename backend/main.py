import os
import uvicorn

from fastapi import (
    Depends,
    Request,
    HTTPException,
    FastAPI,
    File,
    Response,
    UploadFile,
    Form,
)
from starlette.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import tempfile
from uuid import uuid4

from .resume_analyzer import process_resume_and_posting
from .code_executors import execute_code
from gh_scraper.FINAL import grift_check


class SessionData:
    def __init__(self, resume_content: bytes, job_post: str):
        self.resume_content = resume_content
        self.job_post = job_post


sessions = {}


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
async def analyze_resume(resume: UploadFile = File(...), job_posting: str = Form(...)):
    resume_content = await resume.read()
    await run_in_threadpool(process_resume_and_posting, resume_content, job_posting)

    res = Response()
    session = str(uuid4())
    sessions[session] = SessionData(resume_content, job_posting)
    res.set_cookie(
        "session", str(session), httponly=True, secure=False, samesite="strict"
    )

    return res


async def get_session(request: Request):  # Rename and add type hint
    session = request.cookies.get("session")
    if session is None:
        raise HTTPException(status_code=403, detail="Not authorized")
    session_data = sessions.get(session)
    if session_data is None:
        raise HTTPException(status_code=403, detail="Not authorized")
    return session_data


@app.post("/api/execute-code")
def execute_code_endpoint(request: CodeRequest):
    result = execute_code(request.code, request.language)
    return result


@app.get("/api/get-analysis")
def get_analysis(session_data: SessionData = Depends(get_session)):
    resume_content = session_data.resume_content
    job_posting = session_data.job_post

    return process_resume_and_posting(resume_content, job_posting)


@app.post("/api/grift_check")
def grift_check_endpoint(session_data: SessionData = Depends(get_session)):
    try:
        resume_data = session_data.resume_content
        job_posting = session_data.job_post

        proccessed = process_resume_and_posting(resume_data, job_posting)
        resume_json = proccessed["resume_analysis"]

        # resume_pdf_path = os.path.join(output_dir, pdf_files[0])
        # resume_json_path = os.path.join(output_dir, "resumes_analysis.json")

        # save both to temp files
        resume_pdf_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        resume_pdf_tmp.write(resume_data)
        resume_pdf_tmp.flush()
        resume_pdf_path = resume_pdf_tmp.name

        resume_json_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        resume_json_tmp.write(resume_json)
        resume_json_tmp.flush()
        resume_json_path = resume_json_tmp.name

        # Call grift check with the correct paths
        out_path = grift_check(resume_pdf_path, resume_json_path)
        print(f"Generated annotated PDF at: {out_path}")

        # Return the full path - we'll serve it directly in a separate endpoint
        return {"out_path": out_path}
    except Exception as e:
        print(f"Error in grift check: {str(e)}")
        return {"error": str(e)}, 500


@app.get("/api/pdf")
async def get_pdf(session_data: SessionData = Depends(get_session)):
    try:
        pdf_data = session_data.resume_content
        return Response(content=pdf_data, media_type="application/pdf")
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error serving PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
