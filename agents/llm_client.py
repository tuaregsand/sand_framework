import os
import openai
from typing import Optional, Dict, Any
import requests
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai")
        
        # Load provider-specific keys from environment
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.deepseek_endpoint = os.getenv("DEEPSEEK_ENDPOINT")

        # Initialize clients based on provider
        if self.provider == "openai":
            if not self.openai_api_key:
                raise ValueError("OpenAI API key not found in environment")
            openai.api_key = self.openai_api_key
        elif self.provider == "anthropic":
            if not self.anthropic_api_key:
                raise ValueError("Anthropic API key not found in environment")
            try:
                import anthropic
                self.anthropic_client = anthropic.Client(api_key=self.anthropic_api_key)
            except ImportError:
                raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        elif self.provider == "deepseek":
            if not self.deepseek_endpoint:
                raise ValueError("DeepSeek endpoint not found in environment")

    def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        stop: Optional[list] = None,
        **kwargs
    ) -> str:
        """Generate a completion from the configured LLM provider."""
        try:
            if self.provider == "openai":
                return self._generate_openai(prompt, max_tokens, temperature, stop, **kwargs)
            elif self.provider == "anthropic":
                return self._generate_anthropic(prompt, max_tokens, temperature, stop, **kwargs)
            elif self.provider == "deepseek":
                return self._generate_deepseek(prompt, max_tokens, temperature, stop, **kwargs)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise

    def _generate_openai(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        stop: Optional[list],
        **kwargs
    ) -> str:
        """Generate completion using OpenAI's API."""
        response = openai.ChatCompletion.create(
            model=kwargs.get("model", "gpt-4"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop
        )
        return response.choices[0].message.content

    def _generate_anthropic(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        stop: Optional[list],
        **kwargs
    ) -> str:
        """Generate completion using Anthropic's Claude."""
        response = self.anthropic_client.completion(
            prompt=prompt,
            max_tokens_to_sample=max_tokens,
            temperature=temperature,
            stop_sequences=stop,
            model=kwargs.get("model", "claude-2")
        )
        return response.completion

    def _generate_deepseek(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        stop: Optional[list],
        **kwargs
    ) -> str:
        """Generate completion using DeepSeek's endpoint."""
        try:
            response = requests.post(
                self.deepseek_endpoint,
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stop": stop,
                    **kwargs
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get("completion") or data.get("text", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API request failed: {str(e)}")
            raise

    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        **kwargs
    ) -> str:
        """Specialized method for generating code with appropriate prompting."""
        enhanced_prompt = f"""Generate code in {language}. 
        Requirements:
        {prompt}
        
        Please provide only the code without explanations.
        """
        return self.generate_completion(
            enhanced_prompt,
            temperature=0.2,  # Lower temperature for more deterministic code generation
            **kwargs
        )
