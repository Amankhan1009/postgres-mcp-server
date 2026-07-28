"""
Abstract LLM provider interface.

Every provider (Groq now, potentially OpenAI/Anthropic later) must
implement generate(). Services and later tools depend on this
interface only — never on a concrete provider class — so adding a
new provider never requires touching service code.
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Sends a prompt to the LLM and returns its text response.

        Args:
            system_prompt: Establishes the assistant's role/behavior.
            user_prompt: The actual question or task.
        """
        raise NotImplementedError