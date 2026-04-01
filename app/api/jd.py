from fastapi import APIRouter
from app.services.gemini import call_gemini
import json

import re
import json

router = APIRouter()

def clean_json(text: str):
    if not text:
        raise ValueError("Empty response from Gemini")

    # remove markdown
    text = re.sub(r"```json|```", "", text)

    # extract JSON part
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)

    raise ValueError("No JSON found in response")

@router.post("/parse-jd")
async def parse_jd(data: dict):
    jd = data["jd"]

    prompt = f"""
    You are a strict JSON generator.

    ONLY return valid JSON.
    DO NOT add explanation.
    DO NOT add text outside JSON.

    Format:
    {{
       "skills": [],
        "tools": [],
        "responsibilities": []
    }}

    JD:
    {jd}
    """

    response = call_gemini(prompt)

    print("RAW RESPONSE:", response)  # 👈 debug

    try:
        clean = clean_json(response)
        return json.loads(clean)
    except Exception as e:
        return {
            "error": "Failed to parse Gemini response",
            "raw": response
        }