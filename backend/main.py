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
from pydantic import BaseModel
import json
import tempfile
from uuid import uuid4

from .resume_analyzer import process_resume_and_posting
from .code_executors import execute_code
from .pr_assignment import generate_pr_assignment
from gh_scraper.FINAL import grift_check
from code_comprehension.snippet_maker import get_code_snippet


class SessionData:
    def __init__(self, resume_content: bytes, job_post: str):
        self.resume_content = resume_content
        self.job_post = job_post
        self.annot_pdf = None


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
    resume_data = session_data.resume_content
    job_posting = session_data.job_post

    proccessed = process_resume_and_posting(resume_data, job_posting)
    resume_json = proccessed["resume_analysis"]

    # resume_pdf_path = os.path.join(output_dir, pdf_files[0])
    # resume_json_path = os.path.join(output_dir, "resumes_analysis.json")

    # save both to temp files
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as resume_pdf_tmp:
        resume_pdf_tmp.write(resume_data)
        resume_pdf_tmp.flush()
        resume_pdf_path = resume_pdf_tmp.name

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".json"
        ) as resume_json_tmp:
            resume_json_tmp.write(json.dumps(resume_json).encode())
            resume_json_tmp.flush()
            resume_json_path = resume_json_tmp.name

            # Call grift check with the correct paths
            print("calling grift check")
            out_path = grift_check(resume_pdf_path, resume_json_path)
            print(f"Generated annotated PDF at: {out_path}")

            # load out_path into a byte array
            with open(out_path, "rb") as f:
                annot_pdf = f.read()

    # add it to session
    session_data.annot_pdf = annot_pdf

    return {}


@app.get("/api/pdf")
def get_pdf(session_data: SessionData = Depends(get_session)):
    pdf_data = session_data.resume_content
    return Response(content=pdf_data, media_type="application/pdf")


@app.get("/api/annotated-pdf")
def get_annot_pdf(session_data: SessionData = Depends(get_session)):
    pdf_data = session_data.annot_pdf
    if pdf_data is None:
        raise HTTPException(status_code=404, detail="Annotated PDF not found")
    return Response(content=pdf_data, media_type="application/pdf")


@app.get("/api/comprehension-problem")
def get_comprehension_problem():
    repo_url = "https://github.com/aws-samples/automated-datastore-discovery-with-aws-glue.git"
    topic = "AWS Data Pipelines"

    result = get_code_snippet(repo_url, topic)
    return {
        "repo": repo_url,
        "path": result["path"],
        "snippet": result["snippet"],
    }


class ComprehensionProblemRequest(BaseModel):
    answer: str


@app.post("/api/comprehension-problem")
def post_comprehension_problem(request: ComprehensionProblemRequest):
    print(request.answer)
    return {"score": 0.9}

@app.get("/api/pr_assessment")
def get_pr_assessment():
    exercises = generate_pr_assignment()
    return {
        exercises
    }

@app.post("/api/pr_assessment")
def post_pr_assessment():
    return {"score": 0.9}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
