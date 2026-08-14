"""
main.py
--------
FastAPI application entrypoint. Wires up every router from api/ and
creates DB tables on startup (swap for Alembic migrations in production).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import init_db
from api import (
    profile, skills, careers, roadmap, challenges, projects,
    simulation, assessment, interview, resume, portfolio, mentor,
)

app = FastAPI(
    title="Career Skills Platform API",
    description="Backend for skill tracking, career matching, adaptive learning, and mentorship.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your frontend origin(s) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router)
app.include_router(skills.router)
app.include_router(careers.router)
app.include_router(roadmap.router)
app.include_router(challenges.router)
app.include_router(projects.router)
app.include_router(simulation.router)
app.include_router(assessment.router)
app.include_router(interview.router)
app.include_router(resume.router)
app.include_router(portfolio.router)
app.include_router(mentor.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"status": "ok", "service": "career-skills-platform-api"}


@app.get("/health")
def health():
    return {"status": "healthy"}
