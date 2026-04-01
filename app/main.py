from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import jd, resume, suggestion, chat, match

app = FastAPI()

# ✅ Allow ALL origins (for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Test Route
@app.get("/")
def root():
    return {"message": "API is running 🚀"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Routers
app.include_router(jd.router, prefix="/jd")
app.include_router(resume.router, prefix="/resume")
app.include_router(suggestion.router, prefix="/suggestion")
app.include_router(chat.router, prefix="/chat")
app.include_router(match.router, prefix="/match")