import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # app/services
TEMPLATE_DIR = os.path.join(BASE_DIR, "..", "templates")  # go up to app, then templates
TEMPLATE_DIR = os.path.abspath(TEMPLATE_DIR)  # normalize path

def load_template(template_name: str) -> str:
    path = os.path.join(TEMPLATE_DIR, f"{template_name}")

    print("Resolved path:", path)

    if not os.path.exists(path):
        raise ValueError(f"Template not found at {path}")

    with open(path, "r", encoding="utf-8") as file:
        return file.read()