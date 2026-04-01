def match_resume(resume, jd):
    def normalize(s):
        return s.lower().strip()

    resume_skills = set([normalize(s) for s in resume["skills"]])

    jd_all = jd.get("skills", []) + jd.get("tools", [])
    jd_skills = [normalize(s) for s in jd_all]

    matched = [s for s in jd_skills if s in resume_skills]
    missing = [s for s in jd_skills if s not in resume_skills]

    score = round((len(matched) / len(jd_skills)) * 100) if jd_skills else 0

    return {
        "score": score,
        "matchedSkills": matched,
        "missingSkills": missing,
        "weakAreas": missing[:5]
    }