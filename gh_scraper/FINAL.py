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


def grift_check(in_path, resume_data_path=None):
    out_path = in_path.replace(".pdf", "_annotated.pdf")
    # breakpoint()
    if resume_data_path is None:
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", api_key=OPENAI_API_KEY)

        resume_parser = JsonOutputParser(pydantic_object=CSResume)
        resume_prompt = PromptTemplate(
            input_variables=["resume_text"],
            partial_variables={"format_instructions": resume_parser.get_format_instructions()},
            template=resume_prompt_template,
        )

        # Initialize the chains for use by the API
        resume_chain = resume_prompt | llm | resume_parser

        # github_email = extract_email_from_repo('abuynits')
        resume_text = load_input(in_path, is_txt=False)
        # output resume dict
        resume_result = resume_chain.invoke({"resume_text": resume_text})
    else:
        with open(resume_data_path, 'r') as f:
            resume_result = json.load(f)

    github_username = resume_result['personal']['links']['github']
    if '/' in github_username:
        github_username = github_username.split('/')[-1]
    # github_email = extract_email_from_repo(github_username)
    user_json_path = Path(__file__).parent / 'data' / f'{github_username}.json'

    if os.path.exists(user_json_path):
        with open(user_json_path, 'r') as f:
            rated_resume = json.load(f)
        annotate_resume(rated_resume, in_path, out_path)
        print("using cached stats")
        return out_path

    files = get_files(github_username)
    scrape_readme(github_username, files)
    # breakpoint()

    rated_resume = extract_gh_files(resume_result, github_username)
    with open(user_json_path, 'w') as f:
        json.dump(rated_resume, f, indent=4)
    annotate_resume(rated_resume, in_path, out_path)
    return out_path


def test_with_resume():
    resume_name='sagar_resume.pdf'
    resume_dir = Path(__file__).parent / 'data'
    if not os.path.exists(resume_dir):
        os.mkdir(resume_dir)

    in_path = resume_dir / resume_name
    if not os.path.exists(in_path):
        print(f"resume {in_path} does not exist")
        exit(1)
    grift_check(in_path)