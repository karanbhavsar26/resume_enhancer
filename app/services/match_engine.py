def normalize(text: str):
    return text.strip().lower()

def is_match(skill, resume_skills):
    for r in resume_skills:
        if skill in r or r in skill:
            return True
    return False

def extract_resume_skills(resume):
    skills = []

    for s in resume.get("skills", []):
        # split by separators
        parts = s.replace("•", ",").split(",")
        skills.extend([normalize(p) for p in parts if p.strip()])

    return list(set(skills))


def extract_jd_skills(jd):
    skills = jd.get("skills", []) + jd.get("tools", [])
    return list(set([normalize(s) for s in skills]))


def calculate_match(resume, jd):
    resume_skills = extract_resume_skills(resume)
    jd_skills = extract_jd_skills(jd)

    if not jd_skills:
        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "suggestions": []
        }

    matched = [s for s in jd_skills if is_match(s, resume_skills)]
    missing = [s for s in jd_skills if not is_match(s, resume_skills)]

    score = int((len(matched) / len(jd_skills)) * 100)

    suggestions = [f"Consider adding {s}" for s in missing]

    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "suggestions": suggestions
    }