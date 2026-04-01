from bs4 import BeautifulSoup


def add_bullet(html: str, exp_id: str, new_text: str):
    soup = BeautifulSoup(html, "html.parser")

    exp = soup.find(attrs={"data-id": exp_id})
    if not exp:
        return html

    ul = exp.find("ul")
    if not ul:
        return html

    new_li = soup.new_tag("li")
    new_li.string = new_text

    ul.append(new_li)

    return str(soup)


def add_skill(html: str, skill: str):
    soup = BeautifulSoup(html, "html.parser")

    skills_section = soup.find(attrs={"data-section": "skills"})
    if not skills_section:
        return html

    ul = skills_section.find("ul")
    if not ul:
        return html

    # prevent duplicates
    existing_text = ul.get_text().lower()
    if skill.lower() in existing_text:
        return html

    new_li = soup.new_tag("li")
    new_li.string = skill

    ul.append(new_li)

    return str(soup)

def update_bullet(html: str, exp_id: str, bullet_index: int, new_text: str):
    soup = BeautifulSoup(html, "html.parser")

    exp = soup.find(attrs={"data-id": exp_id})
    if not exp:
        return html

    bullets = exp.select("ul li")

    if bullet_index >= len(bullets):
        return html

    bullets[bullet_index].string = new_text

    return str(soup)