import os
import json

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from resume_parsing.json_format import CSResume, CSJobPosting
from .prompts import resume_prompt_template, posting_prompt_template
from _secrets import OPENAI_API_KEY

############################# UTIL FUNCTIONS ############################# 

def load_input(file_path: str) -> str:
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    # Join content from all pages
    return "\n".join(doc.page_content for doc in documents)


############################# TEMPLATE ############################# 

resume_parser = JsonOutputParser(pydantic_object=CSResume)
posting_parser = JsonOutputParser(pydantic_object=CSJobPosting)

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

llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", api_key=OPENAI_API_KEY)

# Build the chain using the pipe syntax.
resume_chain = resume_prompt | llm | resume_parser
posting_chain = posting_prompt | llm | posting_parser

# # Initialize the chains for use by the API
# resume_chain = resume_prompt | llm | resume_parser
# posting_chain = posting_prompt | llm | posting_parser