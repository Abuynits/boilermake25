import json
import os

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from resume_parsing.format import CSResume

############################# UTIL FUNCTIONS ############################# 

def load_secrets():
    secrets_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'secrets.json')
    try:
        with open(secrets_path, 'r') as f:
            secrets = json.load(f)
            os.environ['OPENAI_API_KEY'] = secrets['OPENAI_API_KEY']
            return secrets
    except FileNotFoundError:
        raise FileNotFoundError(f"secrets.json not found at {secrets_path}. Please create it with your OpenAI API key.")
    except json.JSONDecodeError:
        raise ValueError("secrets.json is not a valid JSON file")

def load_resume(file_path: str) -> str:
    if file_path.lower().endswith(".pdf"):
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        # Join content from all pages
        return "\n".join(doc.page_content for doc in documents)
    elif file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError("Unsupported file format. Only PDF and TXT are supported.")


############################# TEMPLATE ############################# 

parser = JsonOutputParser(pydantic_object=CSResume)
prompt_template = """
You are a resume parser specialized in condensed computer science resumes.
Given the resume text below, extract the following details:
```

Personal Information:
  - Name, Email (required), Phone (if available), and online links (GitHub, LinkedIn, Website if available).

Education (if present):
  - For each entry: Institution, Degree, Start Date (YYYY-MM-DD), End Date (if available), and GPA (if available).

Experience:
  - For each job: Company, Role, Start Date (YYYY-MM-DD), End Date (if available), and key, abbreviated, highlights.

Projects:
  - For each project: Title, Description, URL (if available), and Technologies (if available).

Skills:
  - A list of skills.

Certifications (if any):
  - For each certification: Title, Issuer, and Date (YYYY-MM-DD).

Awards (if any):
  - For each award: Title, Awarder, and Date (YYYY-MM-DD).

Resume:
{resume_text}

Return the output as valid JSON conforming to this schema:
{format_instructions}
"""
secrets = load_secrets()
prompt = PromptTemplate(
    input_variables=["resume_text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    template=prompt_template,
)
################################################################ 


llm = ChatOpenAI(temperature=0, model="gpt-4o-mini") 

# Build the chain using the pipe syntax.
chain = prompt | llm | parser

resume_path = "jonathan_oppenheimer_resume.pdf" 
resume_text = load_resume(resume_path)
# Invoke the chain with the resume text and print the structured JSON output.
result = chain.invoke({"resume_text": resume_text})
print(result)

# Save the JSON output to a file
with open("output/output.json", "w") as f:
    json.dump(result, f, indent=4)