from fastapi import APIRouter
from app.services.parser import parse_resume
from app.services.template_loader import load_template
from app.services.editor import update_bullet, add_bullet, add_skill
from bs4 import BeautifulSoup
import os
from app.services.gemini import call_gemini
from typing import List, Dict
import re
import json

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # app/services
TEMPLATE_DIR = os.path.join(BASE_DIR, "..", "templates")  # go up to app, then templates
TEMPLATE_DIR = os.path.abspath(TEMPLATE_DIR)  # normalize path



def extract_json(text: str):
    if not text:
        return {}

    # remove ```json ``` wrappers
    text = re.sub(r"```json|```", "", text).strip()

    # extract first JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())

    raise ValueError("No valid JSON found in response")
# ✅ 1. Get available templates
@router.get("/templates")
async def get_templates():
    files = [
        f for f in os.listdir(TEMPLATE_DIR) if f.endswith(".html")
    ]
    return {"templates": files}


# ✅ 2. Load + Parse template (MAIN ENTRY POINT)
@router.get("/load/{name}")
async def load_and_parse(name: str):
    html = load_template(name)

    parsed = parse_resume(html)

    return {
        "html": html,
        "parsed": parsed
    }


@router.post("/apply")
async def apply_updates(data: dict):
    html = data["html"]
    skills = data.get("skills", [])
    exp_updates = data.get("experience_updates", [])

    prompt = f"""
    You are an expert resume editor and ATS optimizer.

    TASK:
    Update the given resume HTML based on selected skills and experience updates.

    -----------------------
    STRICT RULES (VERY IMPORTANT)
    -----------------------

    ### 🔒 HTML + STYLING LOCK (CRITICAL)
    - You MUST NOT rewrite existing HTML
    - You MUST NOT change styling
    - You MUST NOT remove or modify:
    - <strong> tags
    - <span class="highlight">
    - existing class names
    - existing inline styles

    - You are ONLY allowed to:
    ✅ append new <li> bullets
    ✅ append new skills inside existing <ul>

    - DO NOT rewrite full sections
    - DO NOT reformat text
    - DO NOT regenerate existing content

    ---

    ### SKILLS SECTION
    1. Add new skills into EXISTING categories only
    2. If category exists → append using " • "
    3. If new category needed → create ONE new <li> (same style)

    4. DO NOT:
    - duplicate skills
    - create overlapping categories
    - add generic categories (Database Concepts, etc.)

    ---

    ### EXPERIENCE SECTION
    1. Use ONLY provided experience_updates
    2. DO NOT generate anything extra
    3. DO NOT modify existing bullets

    4. ADD ONLY NEW BULLETS:
    - Append as new <li data-bullet="next-index">
    - Match EXACT structure:

    <li data-bullet="X">
        New bullet text here
    </li>

    5. DO NOT:
    - wrap full sentence in <strong>
    - remove existing highlight spans
    - change previous bullets

    ---

    ### GENERAL RULES
    - Treat input HTML as FINAL DESIGN
    - You are doing PATCH, not rewrite
    - Only ADD, never MODIFY existing content
    - Keep all data-* attributes unchanged

    ---

    ### INPUT

    HTML:
    {html}

    Selected Skills:
    {skills}

    Experience Updates:
    {exp_updates}

    ---

    ### OUTPUT
    Return ONLY updated valid HTML.
    """

    updated_html = call_gemini(prompt)

    return {
        "html": updated_html,
        "parsed": parse_resume(updated_html)
    }
@router.post("/generate-experience")
async def generate_experience(data: Dict):
    skills: List[Dict] = data.get("skills", [])
    parsed = data.get("parsed", {})

    # filter only RELATED + STRONG
    skills = [s for s in skills if s["level"] != "NEW"]

    if not skills:
        return {"options_by_skill": {}}

    skills_text = "\n".join(
        [f"- {s['name']} ({s['level']})" for s in skills]
    )

    prompt = f"""
You are an expert resume writer.

User Resume:
{parsed}

Skills to enhance:
{skills_text}

TASK:
For EACH skill, generate 4 resume bullet points.

RULES:
- RELATED → slight enhancement (realistic)
- STRONG → strong impact-based bullets
- Do NOT fake experience
- Keep concise (1 line)

Return STRICT JSON:
{{
  "options_by_skill": {{
    "skill1": ["opt1", "opt2", "opt3", "opt4", "Do not add this experience"],
    "skill2": [...]
  }}
}}
"""

    raw = call_gemini(prompt)

    try:
        parsed_json = extract_json(raw)
    except Exception as e:
        print("Gemini RAW:", raw)
        raise e

    return parsed_json