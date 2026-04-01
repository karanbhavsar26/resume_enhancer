from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import jd, resume, suggestion, chat, match

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:3000",  # React / Next.js frontend
    "http://127.0.0.1:3000",
    # add your deployed frontend URL later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # or ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],         # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],         # allow all headers
)

# Routers
app.include_router(jd.router, prefix="/jd")
app.include_router(resume.router, prefix="/resume")
app.include_router(suggestion.router, prefix="/suggestion")
app.include_router(chat.router, prefix="/chat")
app.include_router(match.router, prefix="/match")