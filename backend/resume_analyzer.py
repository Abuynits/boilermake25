import hashlib
import json
import os
import tempfile
from typing import Dict, Any, Union 
from starlette.datastructures import UploadFile

from resume_parsing.parse import load_input, resume_chain, posting_chain

class AnalysisCache:
    def __init__(self):
        self.cache: Dict[str, Dict[str, Dict[str, Any]]] = {"resumes": {}, "job_postings": {}}
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        self.load_from_files()
    
    def load_from_files(self):
        """Load all previously saved analyses into the cache."""
        resume_output_dir = os.path.join(self.output_dir, 'resumes')
        job_output_dir = os.path.join(self.output_dir, 'job_postings')
        
        if not os.path.exists(resume_output_dir):
            os.makedirs(resume_output_dir)
        if not os.path.exists(job_output_dir):
            os.makedirs(job_output_dir)
        
        for hash_key in os.listdir(resume_output_dir):
            hash_dir = os.path.join(resume_output_dir, hash_key)
            if not os.path.isdir(hash_dir):
                continue
            
            resume_file = os.path.join(hash_dir, 'resume_analysis.json')
            if not os.path.exists(resume_file):
                continue
            
            try:
                with open(resume_file, 'r') as f:
                    resume_analysis = json.load(f)
                
                self.cache["resumes"].setdefault(hash_key, {})["resume_analysis"] = resume_analysis
            except Exception as e:
                print(f"Error loading resume cache for {hash_key}: {str(e)}")
        
        for hash_key in os.listdir(job_output_dir):
            hash_dir = os.path.join(job_output_dir, hash_key)
            if not os.path.isdir(hash_dir):
                continue
            
            job_file = os.path.join(hash_dir, 'job_analysis.json')
            if not os.path.exists(job_file):
                continue
            
            try:
                with open(job_file, 'r') as f:
                    job_analysis = json.load(f)
                
                self.cache["job_postings"].setdefault(hash_key, {})["job_analysis"] = job_analysis
            except Exception as e:
                print(f"Error loading job posting cache for {hash_key}: {str(e)}")
    
    def get_resume(self, hash_key: str) -> Dict[str, Any]:
        return self.cache.get("resumes", {}).get(hash_key)
    
    def get_job_posting(self, hash_key: str) -> Dict[str, Any]:
        return self.cache.get("job_postings", {}).get(hash_key)
    
    def set_resume(self, hash_key: str, data: Dict[str, Any]):
        self.cache["resumes"][hash_key] = data
    
    def set_job_posting(self, hash_key: str, data: Dict[str, Any]):
        self.cache["job_postings"][hash_key] = data
    
    def exists_resume(self, hash_key: str) -> bool:
        return hash_key in self.cache.get("resumes", {})
    
    def exists_job_posting(self, hash_key: str) -> bool:
        return hash_key in self.cache.get("job_postings", {})

# Global cache instance
analysis_cache = AnalysisCache()

def generate_hash(content) -> str:
    return hashlib.sha256(content).hexdigest()

def save_analysis(hash_key: str, analysis_result: Dict, content: Union[UploadFile, str], category: str) -> str:
    """Save analysis and original content to a file and return the analysis file path."""
    output_dir = os.path.join(os.path.dirname(__file__), f'output/{category}')
    hashed_dir = os.path.join(output_dir, hash_key)
    os.makedirs(hashed_dir, exist_ok=True)
    
    # Save analysis
    analysis_file = os.path.join(hashed_dir, f'{category}_analysis.json')
    with open(analysis_file, 'w') as f:
        json.dump(analysis_result, f, indent=2)
    
    # Save original content
    if isinstance(content, UploadFile):
        content_path = os.path.join(hashed_dir, content.filename)
        with open(content_path, 'wb') as f:
            f.write(content.file.read())
    else:
        content_path = os.path.join(hashed_dir, f'{category}.txt')
        with open(content_path, 'w') as f:
            f.write(content)
    
    return analysis_file

def process_resume_and_posting(resume: UploadFile, job_posting: str) -> Dict[str, Any]:
    """Process resume and job posting and return analysis results."""

    # Generate a unique hash for this combination of resume and job posting.
    resume_content = resume.file.read()
    resume.file.seek(0) # Reset file pointer for later use
    resume_hash = generate_hash(resume_content)

    job_posting_hash = generate_hash(job_posting.encode('utf-8'))

    # Get resume
    if analysis_cache.exists_resume(resume_hash):
        resume_result = analysis_cache.get_resume(resume_hash)
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(resume.filename)[1]) as tmp:
            tmp.write(resume_content)
            tmp.flush()
            
            resume_text = load_input(tmp.name, is_txt=resume.filename.endswith('.txt'))
            resume_result = resume_chain.invoke({"resume_text": resume_text})
        # os.unlink(temp_path)
        resume_file = save_analysis(resume_hash, resume_result, resume, 'resumes')
        analysis_cache.set_resume(resume_hash, resume_result)
    
    # Get job posting
    if analysis_cache.exists_job_posting(job_posting_hash):
        posting_result = analysis_cache.get_job_posting(job_posting_hash)
    else:
        posting_result = posting_chain.invoke({"posting_text": job_posting})    
        job_file = save_analysis(job_posting_hash, posting_result, job_posting, 'job_postings')
        analysis_cache.set_job_posting(job_posting_hash, posting_result)
    
    return {
        "resume_analysis": resume_result,
        "job_analysis": posting_result,
        "saved_files": {
            "resume": resume_file,
            "job": job_file
        },
        "hash": resume_hash,
        "cached": False
    }