import httpx
import logging
from app.config.settings import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger("devflow.ai.groq")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


async def ask_groq(system_prompt: str, user_prompt: str, json_mode: bool = True) -> str:
    """
    Sends chat completion request to Groq API.
    """
    if not GROQ_API_KEY or GROQ_API_KEY == "YOUR_GROQ_API_KEY":
        raise ValueError(
            "GROQ_API_KEY is not configured in backend/.env. "
            "Please obtain a free API key from https://console.groq.com and set GROQ_API_KEY."
        )

    payload = {
        "model": GROQ_MODEL,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    }

    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        try:
            response = await client.post(
                GROQ_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.error(f"Groq API HTTP error: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"Groq API error ({e.response.status_code}): {e.response.text}") from e
        except Exception as e:
            logger.error(f"Failed to communicate with Groq: {str(e)}")
            raise
