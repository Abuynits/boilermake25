from saad.topics import get_relevant_topics
from saad.prs import driver
import json

def extract_code_from_json(input_text):
    # Extract JSON string from the input
    match = re.search(r'```json\n(.*?)\n```', input_text, re.DOTALL)
    if not match:
        raise ValueError("Invalid input format: No JSON block found")
    
    json_str = match.group(1)
    
    # Parse JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON format") from e
    
    # Extract code contents
    if "contents" in data:
        return data["contents"]
    else:
        raise ValueError("Invalid JSON structure: 'contents' key not found")
    
def generate_pr_assignment():
    resume_topics = ["C", "C++", "Python", "Scala", "Haskell", "Rust", "Linux", "Bash", "Git", "FreeRTOS", "Javascript", "Typescript", "PyTorch", "Langchain", "Docker", "Kubernetes", "AWS (S3, EC2, Lambda)", "React", "Svelte", "Node", "Express", "Flask", "PostgreSQL", "MongoDB", "Redis", "CI/CD", "OpenCL", "OpenGL", "CUDA", "WebAssembly", "x86(-64) AT&T Assembly", "ARM Assembly", "GCC", "Valgrind", "GDB", "CMake", "Make", "Meson", "Ninja", "Blender", "Unity", "Vim", "TCP/IP", "UDP", "HTTP(S)", "REST", "GraphQL", "gRPC"]
    job_posting_topics = ["HTML", "CSS", "JavaScript", "React", "Vue.js", "Angular", "Node.js", "Python", "PHP", "Ruby", "Java", "MySQL", "PostgreSQL", "MongoDB", "Git", "RESTful APIs"]
    topics = get_relevant_topics(resume_topics, job_posting_topics)
    topics = topics[0]
    print(topics)

    exercises = driver(topics)

    return extract_code_from_json(exercises[0])

if __name__ == "__main__":
    exercises = generate_pr_assignment()
    print(json.dumps(exercises, indent=4))