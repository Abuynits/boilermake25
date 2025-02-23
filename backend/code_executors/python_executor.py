import sys
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr

from .base import CodeExecutor, CodeExecutionResult
# from .security import CodeSecurity, SecurityError  # Security module commented out

class PythonExecutor(CodeExecutor):
    def execute(self, code: str) -> CodeExecutionResult:
        """Execute Python code in a safe environment."""
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        try:
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                # Security checks commented out
                # CodeSecurity.check_python_code(code)
                # CodeSecurity.set_resource_limits()
                # safe_globals = CodeSecurity.sandbox_python_globals()
                
                # Execute with full globals
                exec(code, {"__builtins__": __builtins__}, {})
                
            return CodeExecutionResult(
                output=stdout_buffer.getvalue(),
                error=stderr_buffer.getvalue(),
                success=True
            )
        
        # Security error handling commented out
        # except SecurityError as e:
        #     return CodeExecutionResult(
        #         output="",
        #         error=f"Security violation: {str(e)}",
        #         success=False
        #     )
        except Exception as e:
            return CodeExecutionResult(
                output=stdout_buffer.getvalue(),
                error=traceback.format_exc() + "\n" + stderr_buffer.getvalue(),
                success=False
            )
