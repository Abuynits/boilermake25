from fastapi import Depends, Request, HTTPException, FastAPI, File, Response, UploadFile, Form
from starlette.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4

from .code_executors import execute_code
from .resume_analyzer import process_resume_and_posting


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
    res.set_cookie("session", str(session), httponly=True, secure=False, samesite="strict")

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
