import os
import json

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from resume_parsing.json_format import CSResume, CSJobPosting
from .prompts import resume_prompt_template, posting_prompt_template

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

def load_input(file_path: str, is_txt: bool=False) -> str:
    if file_path.lower().endswith(".pdf") and not is_txt:
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

resume_parser = JsonOutputParser(pydantic_object=CSResume)
posting_parser = JsonOutputParser(pydantic_object=CSJobPosting)

secrets = load_secrets()
resume_prompt = PromptTemplate(
    input_variables=["resume_text"],
    partial_variables={"format_instructions": resume_parser.get_format_instructions()},
    template=resume_prompt_template,
)

posting_prompt = PromptTemplate(
    input_variables=["posting_text"],
    partial_variables={"format_instructions": posting_parser.get_format_instructions()},
    template=posting_prompt_template,
)
################################################################ 


llm = ChatOpenAI(temperature=0, model="gpt-4o-mini") 

# Build the chain using the pipe syntax.
resume_chain = resume_prompt | llm | resume_parser
posting_chain = posting_prompt | llm | posting_parser

# Initialize the chains for use by the API
resume_chain = resume_prompt | llm | resume_parser
posting_chain = posting_prompt | llm | posting_parser