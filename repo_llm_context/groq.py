import sys

import json
from groq import Groq
from joblib import Memory
from _secrets import GROQ_KEY

memory = Memory("./.cache", verbose=0)
# client = instructor.from_groq(Groq(api_key=GROQ_KEY), mode=instructor.Mode.JSON)
client = Groq(api_key=GROQ_KEY)

filter_list_prompt = """Given a list of file names and a topic, return a JSON list containing a subset of file names which are relevant to the topic, in order of relevancy (most to least relevant). Format should look like this
```
{
  "files": ["path/to/important.ext", ..., "path/to/not_very_important.ext"]
}
```"""


@memory.cache
def groq_filter_list(file_list: list[str], topic: str):
    # for name in file_list:
    #     print(name, file=sys.stderr)
    messages = [
        {
            "role": "system",
            "content": filter_list_prompt,
        },
        {
            "role": "user",
            "content": f"<file-list>\n{file_list}\n</file-list>\n<topic>{topic}</topic>",
        },
    ]

    completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
        temperature=0.0,
        response_format={"type": "json_object"},
    )

    out = completion.choices[0].message.content
    out = json.loads(out)["files"]
    out = [x for x in out if x in file_list]

    return out


if __name__ == "__main__":
    import sys

    file_list = sys.argv[1]
    topic = sys.argv[2]

    file_list = open(file_list).read().splitlines()
    out = groq_filter_list(file_list, topic)

    for name in out:
        print(name)
