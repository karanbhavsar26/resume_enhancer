from fastapi import APIRouter
from app.services.gemini import call_gemini
import json
import re

router = APIRouter()


def clean_json(text: str):
    text = re.sub(r"```json|```", "", text)
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        return match.group(0)
    raise ValueError("No JSON array found")


@router.post("/generate")
async def generate_suggestions(data: dict):
    resume = data["resume"]
    jd = data["jd"]

    prompt = f"""
You are a professional resume editor.

STRICT RULES:
- Do NOT invent experience
- Only enhance existing content
- Use strong action verbs
- Add measurable impact where possible
- Keep under 25 words per bullet

TARGETING RULE:
- Always include "data-id" for section targeting

Resume:
{resume}

Job Description:
{jd}

Return ONLY JSON array:

[
  {{
    "type": "rewrite_bullet",
    "target": {{
      "section": "experience",
      "id": "exp-1",
      "bulletIndex": 0
    }},
    "suggestion": "Optimized API performance by 30% using Redis caching"
  }},
  {{
    "type": "add_skill",
    "target": {{
      "section": "skills"
    }},
    "suggestion": "GraphQL"
  }}
]
"""

    response = call_gemini(prompt)

    print("RAW:", response)  # debug

    try:
        clean = clean_json(response)
        parsed = json.loads(clean)

        # ✅ validate all suggestions
        valid = [s for s in parsed if validate_suggestion(s)]

        return valid

    except Exception as e:
        return {
            "error": "Failed to parse suggestions",
            "raw": response
        }


def validate_suggestion(suggestion):
    allowed_types = ["rewrite_bullet", "add_bullet", "add_skill"]

    if suggestion.get("type") not in allowed_types:
        return False

    if len(suggestion.get("suggestion", "")) > 200:
        return False

    return True

@router.post("/chat")
async def chat_edit(data: dict):
    resume = data["resume"]      # structured JSON
    jd = data["jd"]              # structured JD
    message = data["message"]    # user input

    prompt = f"""
You are an AI resume editor.

User Instruction:
"{message}"

STRICT RULES:
- Do NOT invent experience
- Only enhance existing content
- Keep bullet <= 25 words
- Use strong action verbs
- Only modify relevant sections

TARGETING RULE:
- Use:
  - section
  - id (for experience)
  - bulletIndex (if needed)

Resume:
{json.dumps(resume, indent=2)}

Job Description:
{json.dumps(jd, indent=2)}

Return ONLY JSON array:

[
  {{
    "type": "rewrite_bullet",
    "target": {{
      "section": "experience",
      "id": "exp-1",
      "bulletIndex": 0
    }},
    "suggestion": "Improved performance by 30% using lazy loading"
  }}
]
"""

    response = call_gemini(prompt)

    try:
        clean = clean_json(response)
        parsed = json.loads(clean)

        # validate
        valid = [s for s in parsed if validate_suggestion(s)]

        return {
            "suggestions": valid,
            "message": "Suggestions generated. Awaiting approval."
        }

    except:
        return {
            "error": "Failed to parse",
            "raw": response
        }