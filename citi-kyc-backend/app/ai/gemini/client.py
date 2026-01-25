from __future__ import annotations

import json
import time
from typing import Any, Optional, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

try:
    from google import genai
except Exception as e:
    genai = None


class GeminiClientError(RuntimeError):
    pass


class GeminiClient:
    """
    Thin wrapper around Google Gen AI SDK to enforce:
    - retries
    - JSON response schema
    - consistent config
    """

    def __init__(
        self,
        api_key: Optional[str],
        model: str = "gemini-2.0-flash",
        max_retries: int = 2,
        retry_backoff_sec: float = 0.8,
    ):
        if genai is None:
            raise GeminiClientError("google-genai SDK not installed")

        if not api_key:
            raise GeminiClientError("Missing GEMINI_API_KEY")

        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.max_retries = max_retries
        self.retry_backoff_sec = retry_backoff_sec

    def _sleep(self, attempt: int) -> None:
        time.sleep(self.retry_backoff_sec * (2 ** attempt))

    def generate_structured(
        self,
        prompt: str,
        schema_model: Type[T],
        temperature: float = 0.2,
        max_output_tokens: int = 2048,
    ) -> T:
        """
        Generate JSON that conforms to schema_model (Pydantic).
        Uses response schema / controlled generation.
        """
        last_err: Exception | None = None

        # The SDK supports response schema / structured output on Gemini models.
        # See Gemini structured output docs.
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={
                        "temperature": temperature,
                        "max_output_tokens": max_output_tokens,
                        # Key part: structured output (schema)
                        "response_mime_type": "application/json",
                        "response_schema": schema_model.model_json_schema(),
                    },
                )
                # response.text is JSON string when response_mime_type is application/json
                raw = response.text or "{}"
                data = json.loads(raw)
                return schema_model.model_validate(data)

            except Exception as e:
                last_err = e
                if attempt < self.max_retries:
                    self._sleep(attempt)
                else:
                    raise GeminiClientError(f"Gemini structured generation failed: {e}") from e

        raise GeminiClientError(f"Gemini structured generation failed: {last_err}")
