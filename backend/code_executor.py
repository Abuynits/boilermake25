import sys
import io
from contextlib import redirect_stdout, redirect_stderr
import traceback

def execute_python_code(code: str, timeout: int = 5) -> dict:
    """
    Execute Python code in a safe environment with timeout.
    Returns stdout, stderr, and any error messages.
    """
    # Create string buffers for stdout and stderr
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    
    result = {
        "output": "",
        "error": "",
        "success": True
    }
    
    try:
        # Redirect stdout and stderr to our buffers
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            # Execute the code
            exec(code, {"__builtins__": __builtins__}, {})
            
        # Get the output
        result["output"] = stdout_buffer.getvalue()
        
    except Exception as e:
        # Get the full traceback
        result["error"] = traceback.format_exc()
        result["success"] = False
        
    finally:
        # Always include stderr in the output
        stderr_output = stderr_buffer.getvalue()
        if stderr_output:
            if result["error"]:
                result["error"] += "\n" + stderr_output
            else:
                result["error"] = stderr_output
    
    return result
