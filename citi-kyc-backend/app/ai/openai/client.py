import base64
from openai import OpenAI


class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        self.client = OpenAI(api_key=api_key)
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
        messages = [
            {"role": "user", "content": prompt}
        ]

        # If you want to include file content, encode it and append to the prompt
        if file_bytes:
            file_content = base64.b64encode(file_bytes).decode()
            messages[0]["content"] = (
                f"{prompt}\n\n[BASE64_{mime_type}]: {file_content}"
            )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_output_tokens,
            response_format={
                "type": "json_object"
            },
        )

        return schema_model.model_validate_json(response.choices[0].message.content)