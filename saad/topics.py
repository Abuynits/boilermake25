import openai
from . import topic_examples
from . import prompts
from importlib.resources import read_text
from _secrets import HYPERBOLIC_API_KEY

topics = topic_examples.topics

system_content = None
user_content = str(topics[4])
system_content = read_text(prompts, 'prompt.txt')

client = openai.OpenAI(
    api_key=HYPERBOLIC_API_KEY,
    base_url="https://api.hyperbolic.xyz/v1",
    )

chat_completion = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct",
    messages=[
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ],
    temperature=0.7,
    max_tokens=1024,
)

response = chat_completion.choices[0].message.content
print("Response:\n", response)

