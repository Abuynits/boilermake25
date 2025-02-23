import subprocess
import tempfile
import os
from .base import CodeExecutor, CodeExecutionResult

class TypeScriptExecutor(CodeExecutor):
    def execute(self, code: str) -> CodeExecutionResult:
        """Execute TypeScript code by first compiling it to JavaScript."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as ts_file:
            try:
                # Write TypeScript code to temporary file
                ts_file.write(code)
                ts_file.flush()
                
                # Compile TypeScript to JavaScript
                compile_process = subprocess.run(
                    ['npx', 'tsc', ts_file.name, '--target', 'ES2020', '--module', 'commonjs'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if compile_process.returncode != 0:
                    return CodeExecutionResult(
                        output="",
                        error=f"TypeScript compilation failed:\n{compile_process.stderr}",
                        success=False
                    )
                
                # Get the JavaScript file path (same name but .js extension)
                js_file = ts_file.name.replace('.ts', '.js')
                
                # Execute the compiled JavaScript
                run_process = subprocess.run(
                    ['node', js_file],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                return CodeExecutionResult(
                    output=run_process.stdout,
                    error=run_process.stderr,
                    success=run_process.returncode == 0
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
                    error=f"Failed to execute TypeScript: {str(e)}",
                    success=False
                )
            finally:
                # Clean up temporary files
                try:
                    os.unlink(ts_file.name)
                    js_file = ts_file.name.replace('.ts', '.js')
                    if os.path.exists(js_file):
                        os.unlink(js_file)
                except:
                    pass
