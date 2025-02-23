from fastapi import FastAPI, File, Response, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel
from session import cookie, backend, SessionData
from uuid import uuid4

from .code_executors import execute_code
from .resume_analyzer import process_resume_and_posting


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
    # creates a session
    res_json, resume_content = await run_in_threadpool(
        process_resume_and_posting, resume, job_posting
    )

    res = Response(content=res_json)
    session = uuid4()
    data = SessionData(resume_text=resume_content, job_posting_text=job_posting)
    await backend.create(session, data)
    cookie.attach_to_response(res, session)

    return res


@app.post("/api/execute-code")
def execute_code_endpoint(request: CodeRequest):
    result = execute_code(request.code, request.language)
    return result


@app.get("/api/get-analysis")
def get_analysis():
    # cached_data = analysis_cache.get_resume(hash_key)
    if not cached_data:
        return {"error": "Analysis not found"}, 404
    return cached_data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
