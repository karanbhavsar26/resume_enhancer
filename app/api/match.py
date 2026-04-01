from fastapi import APIRouter
from app.services.match_engine import calculate_match

router = APIRouter()


@router.post("/score")
async def match_score(data: dict):
    resume = data["resume"]
    jd = data["jd"]

    result = calculate_match(resume, jd)

    return result

@router.post("/analyze")
async def analyze(data: dict):
    parsed_resume = data["resume"]
    jd = data["jd"]

    score_data = get_score_logic(parsed_resume, jd)  # your existing logic

    return {
        "score": score_data["score"],
        "missing_skills": [
            {
                "name": skill,
                "level": "NEW"  # default, frontend will change
            }
            for skill in score_data["missing_skills"]
        ]
    }