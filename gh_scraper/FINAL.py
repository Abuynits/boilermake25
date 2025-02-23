import os
import json

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from resume_parsing.json_format import CSResume, CSJobPosting
from resume_parsing.prompts import resume_prompt_template, posting_prompt_template
from resume_parsing.parse import load_input
from gh_scraper.parser import get_files
from gh_scraper.extract_gh_files import extract_gh_files
from gh_scraper.parsing_utils.bs_utils import extract_email_from_repo
from gh_scraper.pdf_annotator import annotate_resume 
from _secrets import OPENAI_API_KEY
from path import Path
import pdb
from gh_scraper.readme_scraper import scrape_readme
pdb.disable()


github_email="hvbhatt@purdue.edu"

resume_name='harmya_bhatt_resume.pdf'
output_file = resume_name.split('.')[0] + '_annotated.pdf'

tmp_file = resume_name.split('.')[0] + '_tmp.pdf'


resume_dir = Path(__file__).parent / 'data'
if not os.path.exists(resume_dir):
    os.mkdir(resume_dir)

in_path = resume_dir / resume_name
if not os.path.exists(in_path):
    print(f"resume {in_path} does not exist")
    exit(1)
breakpoint()
out_path = resume_dir / output_file
github_username = 'harmya'
user_json_path = Path(__file__).parent / 'data' / f'{github_username}.json'

if os.path.exists(user_json_path):
    with open(user_json_path, 'r') as f:
        rated_resume = json.load(f)
    annotate_resume(rated_resume, in_path, out_path)
    print("using cached stats")
    exit(0)

# breakpoint()
inp = load_input(in_path)
llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", api_key=OPENAI_API_KEY)

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

# Initialize the chains for use by the API
resume_chain = resume_prompt | llm | resume_parser

breakpoint()
# github_email = extract_email_from_repo('abuynits')
resume_text = load_input(in_path, is_txt=False)
# output resume dict
resume_result = resume_chain.invoke({"resume_text": resume_text})
github_username = resume_result['personal']['links']['github']
if '/' in github_username:
    github_username = github_username.split('/')[-1]
# github_email = extract_email_from_repo(github_username)

files = get_files(github_username)
scrape_readme(github_username, files)
# breakpoint()

breakpoint()

if not os.path.exists(user_json_path):
    rated_resume = extract_gh_files(resume_result, github_username, github_email)
    with open(user_json_path, 'w') as f:
        json.dump(rated_resume, f, indent=4)
    annotate_resume(rated_resume, in_path, out_path)
else:
    with open(user_json_path, 'r') as f:
        rated_resume = json.load(f)
    annotate_resume(rated_resume, in_path, out_path)