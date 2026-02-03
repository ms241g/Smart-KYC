import base64
from google import genai


class GeminiClient:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate_structured(
        self,
        prompt: str,
        schema_model,
        temperature: float = 0.2,
        max_output_tokens: int = 2048,
        file_bytes: bytes | None = None,
        mime_type: str = "application/pdf",
    ):
        parts = [{"text": prompt}]

        if file_bytes:
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": base64.b64encode(file_bytes).decode("utf-8"),
                }
            })

        response = self.client.models.generate_content(
            model=self.model,
            contents=[{
                "role": "user",
                "parts": parts
            }],
            config={
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
                "response_mime_type": "application/json",
                "response_schema": schema_model.model_json_schema(),
            },
        )

        return schema_model.model_validate_json(response.text)
