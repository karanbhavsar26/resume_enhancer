from bs4 import BeautifulSoup
import re


def parse_resume(html: str):
    soup = BeautifulSoup(html, "html.parser")

    return {
        "skills": extract_skills(soup),
        "experience": extract_experience(soup)
    }


# ✅ SKILLS
def extract_skills(soup):
    skills_section = soup.find(attrs={"data-section": "skills"})

    if not skills_section:
        return []

    skills = []

    # FIX: support both <p> and <li>
    items = skills_section.find_all(["p", "li"])

    for item in items:
        text = item.get_text(" ", strip=True)

        # remove labels like "Frontend:"
        if ":" in text:
            text = text.split(":", 1)[1]

        parts = text.replace("•", ",").split(",")

        for p in parts:
            clean = p.strip()
            if clean:
                skills.append(clean)

    return list(set(skills))


# ✅ EXPERIENCE
def extract_experience(soup):
    experiences = []

    exp_blocks = soup.find_all(attrs={"data-item": "experience"})

    for exp in exp_blocks:
        exp_id = exp.get("data-id")

        # fields
        company = exp.find(attrs={"data-field": "company"})
        role = exp.find(attrs={"data-field": "role"})
        tech = exp.find(attrs={"data-field": "tech"})

        company_text = company.get_text(strip=True) if company else ""
        role_text = role.get_text(strip=True) if role else ""
        tech_text = tech.get_text(strip=True) if tech else ""

        # bullets
        bullets = []
        bullet_elements = exp.find_all(attrs={"data-bullet": True})

        for li in bullet_elements:
            text = li.get_text(" ", strip=True)
            if text:
                bullets.append(text)

        experiences.append({
            "id": exp_id,
            "company": company_text,
            "role": role_text,
            "tech": tech_text,
            "bullets": bullets
        })

    return experiences