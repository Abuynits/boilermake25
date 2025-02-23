import os
import resource
import signal
from functools import wraps
from typing import Set, Dict, Any

class SecurityError(Exception):
    """Raised when a security violation is detected."""
    pass

class CodeSecurity:
    # Banned Python modules that could be dangerous
    BANNED_MODULES: Set[str] = {
        'os',           # File system operations
        'sys',         # System-specific parameters
        'subprocess',  # Spawn new processes
        'socket',     # Network operations
        'requests',   # HTTP requests
        'urllib',     # URL handling
        'pathlib',    # File system paths
        'shutil',     # High-level file operations
        'pickle',     # Arbitrary code execution risk
        'marshal',    # Similar to pickle
    }
    
    # Banned JavaScript/TypeScript globals
    BANNED_JS_GLOBALS: Set[str] = {
        'process',      # Node.js process object
        'require',      # Node.js module system
        'fs',          # File system
        'child_process', # Process spawning
        'http',        # HTTP requests
        'net',         # Network operations
        'path',        # File system paths
    }
    
    @staticmethod
    def set_resource_limits() -> None:
        """Set resource limits for the process."""
        # 100MB memory limit
        memory_limit = 100 * 1024 * 1024
        
        # Set maximum CPU time to 5 seconds
        resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
        
        # Set maximum memory size
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
        
        # No child processes
        resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
        
        # Set up alarm for timeout
        signal.alarm(5)  # 5 second timeout
    
    @staticmethod
    def check_python_code(code: str) -> None:
        """Check Python code for security violations."""
        import ast
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise SecurityError(f"Invalid Python syntax: {str(e)}")
        
        for node in ast.walk(tree):
            # Check for import statements
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = node.names[0].name.split('.')[0]
                if module in CodeSecurity.BANNED_MODULES:
                    raise SecurityError(f"Use of banned module: {module}")
            
            # Check for exec/eval calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in {'exec', 'eval', 'compile'}:
                        raise SecurityError(f"Use of banned function: {node.func.id}")
    
    @staticmethod
    def check_js_code(code: str) -> None:
        """Basic check for JavaScript/TypeScript code for security violations."""
        # Check for banned globals
        for banned in CodeSecurity.BANNED_JS_GLOBALS:
            if banned in code:
                raise SecurityError(f"Use of banned JavaScript global: {banned}")
        
        # Check for require/import statements
        if "require(" in code or "import " in code:
            raise SecurityError("External module imports are not allowed")
    
    @staticmethod
    def sandbox_python_globals() -> Dict[str, Any]:
        """Create a restricted globals dictionary for Python execution."""
        safe_globals = {
            '__builtins__': {
                # Allow only safe builtins
                'abs': abs, 'all': all, 'any': any, 'ascii': ascii,
                'bin': bin, 'bool': bool, 'bytearray': bytearray,
                'bytes': bytes, 'chr': chr, 'complex': complex,
                'dict': dict, 'divmod': divmod, 'enumerate': enumerate,
                'filter': filter, 'float': float, 'format': format,
                'frozenset': frozenset, 'hash': hash, 'hex': hex,
                'int': int, 'isinstance': isinstance, 'issubclass': issubclass,
                'iter': iter, 'len': len, 'list': list, 'map': map,
                'max': max, 'min': min, 'next': next, 'oct': oct,
                'ord': ord, 'pow': pow, 'print': print, 'range': range,
                'repr': repr, 'reversed': reversed, 'round': round,
                'set': set, 'slice': slice, 'sorted': sorted, 'str': str,
                'sum': sum, 'tuple': tuple, 'type': type, 'zip': zip,
            }
        }
        return safe_globals
