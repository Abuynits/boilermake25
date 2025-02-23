# Resume Matcher

A web application that analyzes resumes and job postings using AI to help match candidates with positions. The application uses FastAPI for the backend, Next.js for the frontend, and LangChain for AI processing.

## Prerequisites

- Python 3.8 or higher
- [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)
- Node.js 14 or higher
- npm
- OpenAI API key
- Groq API Key
- Hyperbolic API Key
- GitHub Token

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Abuynits/boilermake25
cd boilermake25
```

### 2. Set Up Python Environment
```bash
uv sync
source .venv/bin/activate
```

### 3. Set Up Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### 4. Configure OpenAI API Key
Create a `_secrets.py` file in the repository root, and add these keys:
```py
GROQ_KEY="your_groq_key"
GITHUB_TOKEN="your_github_token"
OPENAI_API_KEY="your_openai_api_key"
HYPERBOLIC_API_KEY="your_hyperbolic_api_key"
```

## Running the Application

### 1. Start the Backend Server
In one terminal:
```bash
python -m backend.main
```
The backend will run on `http://localhost:8000`

### 2. Start the Frontend Development Server
In another terminal:
```bash
cd frontend
npm run dev
```
The frontend will run on `http://localhost:3000`

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Upload a resume (PDF or TXT format)
3. Paste the job posting text in the provided text area
4. Click Submit to analyze
5. View the analysis results below the form

## Output

The application will:
- Display the analysis results on the web page
- Save JSON files with the analysis results in the `backend/output` directory
- Generate unique filenames with timestamps for each analysis