resume_prompt_template = """
You are a job posting parser specialized in condensed computer science job postings.
Given the job posting text below, extract the following details:

Company Information:
  - Name (required)
  - Website (if available)
  - Location (if available)

Job Details:
  - Title (required)
  - Description (detailed job description)
  - Responsibilities (if available): list all responsibilities for the role
  - Requirements (if available): list required qualifications and skills
  - Skills (if available): list technical skills or proficiencies required
  - Employment Type (if available): e.g., Full-Time, Part-Time, Contract
  - Experience Level (if available): e.g., Entry-Level, Mid-Level, Senior
  - Salary Range (if available): e.g., '$70k-$90k'
  - Benefits (if available): list provided benefits (e.g., Health Insurance, 401k)
  - Posting Date (if available): in YYYY-MM-DD format
  - Closing Date (if available): in YYYY-MM-DD format

Application Details (if available):
  - How to Apply: instructions for applying to the job
  - Application URL (if available)
  - Contact Email (if available): for job-related inquiries

Job Posting Text:
{resume_text}

Return the output as valid JSON conforming to this schema:
{format_instructions}
"""

posting_prompt_template = """
You are a job posting parser specialized in condensed computer science job postings.
Given the job posting text below, extract the following details:

Company Information:
  - Name (required)
  - Website (if available)
  - Location (if available)

Job Details:
  - Title (required)
  - Description (detailed job description)
  - Responsibilities (if available): list key responsibilities for the role
  - Requirements (if available): list required qualifications and skills
  - Skills (if available): list technical skills or proficiencies required
  - Employment Type (if available): e.g., Full-Time, Part-Time, Contract
  - Experience Level (if available): e.g., Entry-Level, Mid-Level, Senior
  - Salary Range (if available): e.g., '$70k-$90k'
  - Benefits (if available): list provided benefits (e.g., Health Insurance, 401k)
  - Posting Date (if available): in YYYY-MM-DD format
  - Closing Date (if available): in YYYY-MM-DD format

Application Details (if available):
  - How to Apply: instructions for applying to the job
  - Application URL (if available)
  - Contact Email (if available): for job-related inquiries

Job Posting Text:
{posting_text}

Return the output as valid JSON conforming to this schema:
{format_instructions}
"""
