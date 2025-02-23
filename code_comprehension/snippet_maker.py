import os
import sys
import instructor
from groq import Groq
from pydantic import BaseModel
from repo_llm_context import repo_url_to_context_json, files_json_to_model_context

from dotenv import load_dotenv

load_dotenv()

GROQ_KEY = os.environ.get("GROQ_KEY")
client = Groq(api_key=GROQ_KEY)
client = instructor.from_groq(client, mode=instructor.Mode.JSON)

system_prompt = """You are a highly precise code analysis system. When shown code and a topic, you must:

1. Find the MOST complex and relevant code snippet that:
   - Is 10-50 lines long
   - Demonstrates non-trivial logic
   - Is completely self-contained 
   - Shows actual implementation, not just interfaces
   - Includes full function/class definitions when needed

2. Format your response EXACTLY as:

hidden_thoughts: [Explain specific technical reasons why this exact snippet demonstrates the topic]

snippet_source_code:
[PASTE THE EXACT CODE HERE, preserving all indentation]

snippet_path: [file path from the <file> tag]

snippet_explanation: [Detailed technical breakdown of:
- Exact data structures and algorithms used
- Specific control flow and logic
- Concrete error handling or edge cases
- How the code integrates with other components]

Your responses must be EXTREMELY concrete and specific. Never output generic descriptions. Every statement must reference exact details from the code.

Bad response: "This code handles assembly validation"
Good response: "This function validates register conflicts by maintaining a FxHashSet of used registers and checking for duplicate usage in slots[]"""


class SnippetModel(BaseModel):
    hidden_thoughts: str
    snippet_source_code: str
    snippet_path: str
    snippet_explaination: str


def get_code_snippet(git_url, topic):
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    files_json = repo_url_to_context_json(git_url, topic, char_limit=300_000)
    context = files_json_to_model_context(files_json) + "\n"
    suffix = f'The attached files are code from {git_url}.\nFind relevant snippets for the topic "{topic}"\n'
    messages.append(
        {
            "role": "user",
            "content": context + suffix,
        }
    )

    print(f"extracted context from {git_url}", file=sys.stderr)
    completion = client.chat.completions.create(
        messages=messages,
        response_model=SnippetModel,
        model="llama-3.3-70b-versatile",
        temperature=0.75
    )

    return completion.hidden_thoughts, completion.snippet_path, completion.snippet_source_code, completion.snippet_explaination