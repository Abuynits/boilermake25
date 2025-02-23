import subprocess
import tempfile
import os
from .base import CodeExecutor, CodeExecutionResult
# from .security import CodeSecurity, SecurityError  # Security module commented out

class JavaScriptExecutor(CodeExecutor):
    def execute(self, code: str) -> CodeExecutionResult:
        """Execute JavaScript code using Node.js."""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                # Security checks commented out
                # CodeSecurity.check_js_code(code)
                # secured_code = (
                #     '"use strict";\n'
                #     'const process = undefined;\n'
                #     'const require = undefined;\n'
                #     + code
                # )
                
                # Write the code directly
                f.write(code)
                f.flush()
            
                # Run the code with Node.js
                process = subprocess.run(
                    ['node', f.name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            
            return CodeExecutionResult(
                output=process.stdout,
                error=process.stderr,
                success=process.returncode == 0
            )
        
        except subprocess.TimeoutExpired:
            return CodeExecutionResult(
                output="",
                error="Execution timed out after 5 seconds",
                success=False
            )
        except subprocess.SubprocessError as e:
            return CodeExecutionResult(
                output="",
                error=f"Failed to execute JavaScript: {str(e)}",
                success=False
            )
        finally:
            # File cleanup is handled by the context manager
            pass