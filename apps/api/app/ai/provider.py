from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AIProvider(ABC):
    @abstractmethod
    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """Generates plain text response."""
        pass

    @abstractmethod
    def generate_structured(self, system_prompt: str, user_prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generates JSON structured response adhering to schema."""
        pass
