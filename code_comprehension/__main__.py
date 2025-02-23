import os
import instructor
from groq import Groq
from pydantic import BaseModel
from repo_llm_context import repo_url_to_context

from dotenv import load_dotenv
load_dotenv()

GROQ_KEY = os.environ.get("GROQ_KEY")
client = Groq(api_key=GROQ_KEY)
client = instructor.from_groq(client, mode=instructor.Mode.JSON)

system_prompt = """
You are responsible for coming up with code comprehension challenges to test an applicant for a job. The user message
will consist of the contents of a git repository, followed by a topic in question. You will respond with a snippet
of relavant code from the repository, along with a brief explanation of the code. This explanation will be compared
against the user's explanation to determine if they are correct.

Ensure that the code snippets you respond are relavant to the topic in question, and contain enough context for
a person to determine the purpose of the code.

Your response will contain 4 components:
- hidden_thoughts: this is space for you to plan out what you will respond with
- snippet_source_code: the code snippet, copied verbatim from the repository, that you will respond with
- snippet_path: the path to the file in the repository that contains the code snippet, from the <file> tag
- snippet_explaination: a detailed explanation of the code snippet, explaining what it does and why it is important

The snippets you find must be fairly complex but also self contained and short. It should span AT LEAST 10 lines of code.
DO NOT PROVIDE SUGGESTIONS ABOUT THE CODE!! JUST EXPLAIN IT IN THE EXPLAINATION FIELD. THATS IT. NO MORE. NO LESS.
"""


class SnippetModel(BaseModel):
    hidden_thoughts: str
    snippet_source_code: str
    snippet_path: str
    snippet_explaination: str


if __name__ == "__main__":
    import sys

    git_url = sys.argv[1]
    topic = sys.argv[2]

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    context = repo_url_to_context(git_url, char_limit=300000)
    prefix = f"The following content is code from {git_url}\n"
    suffix = f"Find relavant examples within this code base for the topic \"{topic}\"\n"
    messages.append(
        {
            "role": "user",
            "content": prefix + context + suffix,
        }
    )

    print(f"downloaded context from {git_url}", file=sys.stderr)
    print(context, file=sys.stderr)
    completion = client.chat.completions.create(
        messages=messages,
        response_model=SnippetModel,
        model="llama-3.3-70b-versatile",
    )

    # print(completion.choices[0].message.content)
    print("=== Thoughts ===")
    print(completion.hidden_thoughts)
    print(f"\n=== {completion.snippet_path} ===")
    print(completion.snippet_source_code)
    print("\n=== Explaination ===")
    print(completion.snippet_explaination)
