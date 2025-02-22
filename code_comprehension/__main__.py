import os
from groq import Groq
from repo_llm_context import repo_url_to_context

GROQ_KEY = os.environ.get("GROQ_KEY")
client = Groq(api_key=GROQ_KEY)

system_prompt = """
You are responsible for coming up with code comprehension challenges to test an applicant for a job. The user message
will consist of the contents of a git repository, followed by a topic in question. You will respond with a snippet
of relavant code from the repository, along with a brief explanation of the code. This explanation will be compared
against the user's explanation to determine if they are correct.

Ensure that the code snippets you respond are relavant to the topic in question, and contain enough context for
a person to determine the purpose of the code.
"""

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

    context = repo_url_to_context(git_url)
    prefix = f"The following content is code from {git_url}\n"
    suffix = f"The topic in question is: {topic}\n"
    messages.append(
        {
            "role": "user",
            "content": prefix + context + suffix,
        }
    )

    completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
    )

    print(completion.choices[0].message.content)
