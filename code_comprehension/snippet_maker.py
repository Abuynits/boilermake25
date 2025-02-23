import os
import re
import sys
from groq import Groq
from pydantic import BaseModel
from importlib.resources import read_text
from repo_llm_context import repo_url_to_context_json, files_json_to_model_context
from _secrets import GROQ_KEY
from joblib import Memory

memory = Memory("./.cache", verbose=0)

client = Groq(api_key=GROQ_KEY)
# client = instructor.from_groq(client, mode=instructor.Mode.JSON)

# load system_prompt from system_prompt.txt in current module directory
system_prompt = read_text(sys.modules[__name__], "system_prompt.txt")


class SnippetModel(BaseModel):
    hidden_thoughts: str
    snippet_source_code: str
    snippet_path: str
    snippet_explaination: str


def parse_to_json(text: str) -> dict[str, str]:
    # Initialize result dictionary
    result = {"path": "", "snippet": "", "explanation": ""}

    # Helper function to extract content between markers
    def extract_between_markers(text: str, start_marker: str, end_marker=None) -> str:
        start_idx = text.find(start_marker)
        if start_idx == -1:
            return ""

        content_start = start_idx + len(start_marker)

        if end_marker:
            end_idx = text.find(end_marker, content_start)
            if end_idx == -1:
                content = text[content_start:].strip()
            else:
                content = text[content_start:end_idx].strip()
        else:
            content = text[content_start:].strip()

        return content

    # Extract file path
    path_section = extract_between_markers(text, "# File Name\n", "\n# Code")
    result["path"] = path_section.strip()

    # Extract code snippet
    code_pattern = r"# Code Snippet\n```.*?\n(.*?)```"
    code_match = re.search(code_pattern, text, re.DOTALL)
    if code_match:
        result["snippet"] = code_match.group(1).strip()

    # Extract explanation
    explanation_section = extract_between_markers(text, "# Explanation\n")
    result["explanation"] = explanation_section.strip()

    return result


# @memory.cache
def get_code_snippet(git_url, topic, seed=1):
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
    suffix = f"</repo>\n<topic>{topic}</topic>"
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
        # stream=True
    )

    # out = completion.choices[0].message.content
    # print(completion.choices[0].message.content)
    out = ""
    for chunk in completion:
        content = chunk.choices[0].delta.content
        if content:
            out += content
            print(content, end="")

    # return completion.hidden_thoughts, completion.snippet_path, completion.snippet_source_code, completion.snippet_explaination
    out = parse_to_json(out)
    print(out)
    return out
