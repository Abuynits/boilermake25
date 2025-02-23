import os
import sys
from groq import Groq
from pydantic import BaseModel
from importlib.resources import read_text
from repo_llm_context import repo_url_to_context_json, files_json_to_model_context

from dotenv import load_dotenv

load_dotenv()

GROQ_KEY = os.environ.get("GROQ_KEY")
client = Groq(api_key=GROQ_KEY)
# client = instructor.from_groq(client, mode=instructor.Mode.JSON)

# load system_prompt from system_prompt.txt in current module directory
system_prompt = read_text(sys.modules[__name__], "system_prompt.txt")

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

    files_json = repo_url_to_context_json(git_url, topic, char_limit=250_000)
    context = files_json_to_model_context(files_json)
    # with open("temp.txt", "w") as f:
    #     f.write(context)

    prefix = f'<repo url="{git_url}">\n'
    suffix = f'</repo>\n<topic>{topic}</topic>'
    messages.append(
        {
            "role": "user",
            "content": prefix + context + suffix,
        }
    )

    print(f"extracted context from {git_url}", file=sys.stderr)
    completion = client.chat.completions.create(
        messages=messages,
        # response_model=SnippetModel,
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        stream=True
    )

    # print(completion.choices[0].message.content)
    for chunk in completion:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="")
    print("")

    # return completion.hidden_thoughts, completion.snippet_path, completion.snippet_source_code, completion.snippet_explaination