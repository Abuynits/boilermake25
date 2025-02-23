from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class CodeExecutionResult:
    output: str
    error: str
    success: bool

class CodeExecutor(ABC):
    """Base class for language-specific code executors."""
    
    @abstractmethod
    def execute(self, code: str) -> CodeExecutionResult:
        """
        Execute code in the specific language.
        Args:
            code: The code to execute
        Returns:
            CodeExecutionResult containing output, error, and success status
        """
        pass
