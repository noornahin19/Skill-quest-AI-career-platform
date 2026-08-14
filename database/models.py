"""
models.py
---------
ORM models for every entity in the ERD:

UserProfile, Skills, UserSkills, Careers, CareerSkills, LearningProgress,
Challenges, ChallengeAttempts, Projects, ProjectSubmissions,
CareerSimulations, SimulationAttempts, Assessments, AssessmentAttempts,
Achievements, UserAchievements, Portfolio, ChatMessages, DailyMission,
CareerMission, Roadmap, CareerReadiness.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer,
    JSON, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


# --------------------------------------------------------------------------
# Core identity
# --------------------------------------------------------------------------
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    experience_level = Column(String, default="beginner")  # beginner/intermediate/advanced
    target_career_id = Column(String, ForeignKey("careers.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_skills = relationship("UserSkills", back_populates="user", cascade="all, delete-orphan")
    learning_progress = relationship("LearningProgress", back_populates="user", cascade="all, delete-orphan")
    challenge_attempts = relationship("ChallengeAttempts", back_populates="user", cascade="all, delete-orphan")
    project_submissions = relationship("ProjectSubmissions", back_populates="user", cascade="all, delete-orphan")
    simulation_attempts = relationship("SimulationAttempts", back_populates="user", cascade="all, delete-orphan")
    assessment_attempts = relationship("AssessmentAttempts", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievements", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessages", back_populates="user", cascade="all, delete-orphan")
    portfolio = relationship("Portfolio", back_populates="user", uselist=False, cascade="all, delete-orphan")
    readiness = relationship("CareerReadiness", back_populates="user", cascade="all, delete-orphan")
    daily_missions = relationship("DailyMission", back_populates="user", cascade="all, delete-orphan")
    target_career = relationship("Careers", foreign_keys=[target_career_id])


# --------------------------------------------------------------------------
# Skills
# --------------------------------------------------------------------------
class Skills(Base):
    __tablename__ = "skills"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)  # e.g. "backend", "design", "soft-skill"
    description = Column(Text, nullable=True)

    user_skills = relationship("UserSkills", back_populates="skill")
    career_skills = relationship("CareerSkills", back_populates="skill")


class UserSkills(Base):
    __tablename__ = "user_skills"
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=False)
    proficiency = Column(Float, default=0.0)  # 0-100, the "Skill DNA" value
    verified = Column(Boolean, default=False)  # verified via challenge/assessment
    last_practiced = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserProfile", back_populates="user_skills")
    skill = relationship("Skills", back_populates="user_skills")


# --------------------------------------------------------------------------
# Careers
# --------------------------------------------------------------------------
class Careers(Base):
    __tablename__ = "careers"

    id = Column(String, primary_key=True, default=gen_uuid)
    title = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    average_salary = Column(Float, nullable=True)
    growth_outlook = Column(String, nullable=True)  # e.g. "high", "medium", "low"

    career_skills = relationship("CareerSkills", back_populates="career", cascade="all, delete-orphan")
    missions = relationship("CareerMission", back_populates="career", cascade="all, delete-orphan")


class CareerSkills(Base):
    """Required skill + minimum proficiency for a given career."""
    __tablename__ = "career_skills"
    __table_args__ = (UniqueConstraint("career_id", "skill_id", name="uq_career_skill"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    career_id = Column(String, ForeignKey("careers.id"), nullable=False)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=False)
    required_proficiency = Column(Float, default=70.0)
    weight = Column(Float, default=1.0)  # importance of this skill to the career

    career = relationship("Careers", back_populates="career_skills")
    skill = relationship("Skills", back_populates="career_skills")


class CareerMission(Base):
    """The overarching mission/story-arc tied to a career track."""
    __tablename__ = "career_missions"

    id = Column(String, primary_key=True, default=gen_uuid)
    career_id = Column(String, ForeignKey("careers.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    career = relationship("Careers", back_populates="missions")


# --------------------------------------------------------------------------
# Roadmap
# --------------------------------------------------------------------------
class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    career_id = Column(String, ForeignKey("careers.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    resource_type = Column(String, nullable=True)  # challenge/project/course/assessment
    resource_id = Column(String, nullable=True)
    status = Column(String, default="locked")  # locked/available/in_progress/completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LearningProgress(Base):
    __tablename__ = "learning_progress"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=True)
    roadmap_step_id = Column(String, ForeignKey("roadmaps.id"), nullable=True)
    progress_percent = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserProfile", back_populates="learning_progress")


# --------------------------------------------------------------------------
# Challenges (branching difficulty per adaptive_learning_service)
# --------------------------------------------------------------------------
class DifficultyLevel(str, enum.Enum):
    prerequisite = "prerequisite"
    practice = "practice"
    advanced = "advanced"


class Challenges(Base):
    __tablename__ = "challenges"

    id = Column(String, primary_key=True, default=gen_uuid)
    title = Column(String, nullable=False)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.practice)
    prompt = Column(Text, nullable=False)
    solution_criteria = Column(JSON, nullable=True)  # rubric / expected keys
    max_score = Column(Float, default=100.0)

    attempts = relationship("ChallengeAttempts", back_populates="challenge", cascade="all, delete-orphan")


class ChallengeAttempts(Base):
    __tablename__ = "challenge_attempts"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False)
    submitted_answer = Column(Text, nullable=True)
    score = Column(Float, default=0.0)  # 0-100
    passed = Column(Boolean, default=False)
    next_recommended_difficulty = Column(Enum(DifficultyLevel), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserProfile", back_populates="challenge_attempts")
    challenge = relationship("Challenges", back_populates="attempts")


# --------------------------------------------------------------------------
# Projects
# --------------------------------------------------------------------------
class Projects(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=gen_uuid)
    title = Column(String, nullable=False)
    career_id = Column(String, ForeignKey("careers.id"), nullable=True)
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, nullable=True)  # list[skill_id]
    difficulty = Column(String, default="medium")

    submissions = relationship("ProjectSubmissions", back_populates="project", cascade="all, delete-orphan")


class ProjectSubmissions(Base):
    __tablename__ = "project_submissions"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    repo_url = Column(String, nullable=True)
    file_path = Column(String, nullable=True)  # uploads/ path
    status = Column(String, default="submitted")  # submitted/reviewed/accepted/rejected
    feedback = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserProfile", back_populates="project_submissions")
    project = relationship("Projects", back_populates="submissions")


# --------------------------------------------------------------------------
# Simulations
# --------------------------------------------------------------------------
class CareerSimulations(Base):
    __tablename__ = "career_simulations"

    id = Column(String, primary_key=True, default=gen_uuid)
    career_id = Column(String, ForeignKey("careers.id"), nullable=False)
    title = Column(String, nullable=False)
    scenario = Column(Text, nullable=False)
    decision_tree = Column(JSON, nullable=True)  # node graph of choices/outcomes

    attempts = relationship("SimulationAttempts", back_populates="simulation", cascade="all, delete-orphan")


class SimulationAttempts(Base):
    __tablename__ = "simulation_attempts"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    simulation_id = Column(String, ForeignKey("career_simulations.id"), nullable=False)
    choices_made = Column(JSON, nullable=True)
    outcome_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserProfile", back_populates="simulation_attempts")
    simulation = relationship("CareerSimulations", back_populates="attempts")


# --------------------------------------------------------------------------
# Assessments
# --------------------------------------------------------------------------
class Assessments(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, default=gen_uuid)
    title = Column(String, nullable=False)
    career_id = Column(String, ForeignKey("careers.id"), nullable=True)
    questions = Column(JSON, nullable=False)  # list of {question, options, answer, skill_id}

    attempts = relationship("AssessmentAttempts", back_populates="assessment", cascade="all, delete-orphan")


class AssessmentAttempts(Base):
    __tablename__ = "assessment_attempts"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    assessment_id = Column(String, ForeignKey("assessments.id"), nullable=False)
    answers = Column(JSON, nullable=True)
    score = Column(Float, default=0.0)
    result_summary = Column(JSON, nullable=True)  # per-skill breakdown
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserProfile", back_populates="assessment_attempts")
    assessment = relationship("Assessments", back_populates="attempts")


# --------------------------------------------------------------------------
# Achievements / Gamification
# --------------------------------------------------------------------------
class Achievements(Base):
    __tablename__ = "achievements"

    id = Column(String, primary_key=True, default=gen_uuid)
    title = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    criteria = Column(JSON, nullable=True)  # e.g. {"type": "challenge_count", "value": 10}

    user_achievements = relationship("UserAchievements", back_populates="achievement")


class UserAchievements(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    achievement_id = Column(String, ForeignKey("achievements.id"), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserProfile", back_populates="achievements")
    achievement = relationship("Achievements", back_populates="user_achievements")


# --------------------------------------------------------------------------
# Portfolio / Chat / Daily mission / Readiness
# --------------------------------------------------------------------------
class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), unique=True, nullable=False)
    headline = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    featured_projects = Column(JSON, nullable=True)  # list[project_submission_id]
    featured_achievements = Column(JSON, nullable=True)
    public_slug = Column(String, unique=True, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserProfile", back_populates="portfolio")


class ChatMessages(Base):
    """Mentor chat history (AI service)."""
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    role = Column(String, nullable=False)  # user/assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserProfile", back_populates="chat_messages")


class DailyMission(Base):
    __tablename__ = "daily_missions"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    resource_type = Column(String, nullable=True)
    resource_id = Column(String, nullable=True)
    completed = Column(Boolean, default=False)

    user = relationship("UserProfile", back_populates="daily_missions")


class CareerReadiness(Base):
    __tablename__ = "career_readiness"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    career_id = Column(String, ForeignKey("careers.id"), nullable=False)
    readiness_percent = Column(Float, default=0.0)
    skill_gap_summary = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserProfile", back_populates="readiness")
