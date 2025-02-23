from .base import CodeExecutionResult
from .python_executor import PythonExecutor
from .javascript_executor import JavaScriptExecutor
from .typescript_executor import TypeScriptExecutor

# Map file extensions to language names
EXTENSION_TO_LANGUAGE = {
    'py': 'python',
    'js': 'javascript',
    'ts': 'typescript',
}

LANGUAGE_EXECUTORS = {
    'python': PythonExecutor(),
    'javascript': JavaScriptExecutor(),
    'typescript': TypeScriptExecutor(),
}

def execute_code(code: str, language: str) -> CodeExecutionResult:
    # Convert file extension to language name if needed
    language = EXTENSION_TO_LANGUAGE.get(language, language)
    """
    Execute code in the specified language.
    Args:
        code: The code to execute
        language: The programming language ('python', 'javascript', 'typescript', etc.)
    Returns:
        CodeExecutionResult containing output, error, and success status
    """
    executor = LANGUAGE_EXECUTORS.get(language.lower())
    if not executor:
        return CodeExecutionResult(
            output="",
            error=f"Unsupported language: {language}",
            success=False
        )
    
    return executor.execute(code)
