from fastapi import APIRouter
from app.services.gemini import call_gemini
import json
import re

router = APIRouter()


def clean_json(text: str):
    if not text:
        raise ValueError("Empty response from Gemini")

    text = re.sub(r"```json|```", "", text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON:\n{text}")


def validate_response(data: dict):
    required_keys = ["type", "target", "value"]

    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing key: {key}")

    return data


@router.post("/")
async def chat(data: dict):
    message = data["message"]
    resume = data["resume"]
    jd = data["jd"]
    history = data.get("history", [])

    prompt = f"""
You are an AI Resume Editor.

STRICT RULES:
- Return ONLY valid JSON
- No explanation
- No markdown
- No extra text
- Output must be parseable

Allowed types:
- add_skill
- edit_summary
- add_experience_bullet

Return EXACT format:

{{
  "type": "add_skill",
  "target": {{
    "section": "skills"
  }},
  "value": "FastAPI"
}}

---

Chat History:
{history}

Resume:
{resume}

Job Description:
{jd}

User Request:
{message}
"""

    response = call_gemini(prompt)

    parsed = clean_json(response)
    validated = validate_response(parsed)

    return validated