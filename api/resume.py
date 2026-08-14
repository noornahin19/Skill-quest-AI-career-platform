from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from services import skill_dna_service
from core.security import get_current_user

router = APIRouter(prefix="/api/resume", tags=["resume"])


@router.get("/me")
def generate_my_resume(
    current_user: models.UserProfile = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Assembles a structured resume payload (JSON) from profile, top skills,
    accepted project submissions, and earned achievements. A frontend or
    the docx/pdf skill can render this into a downloadable file.
    """
    top_skills = (
        db.query(models.UserSkills, models.Skills)
        .join(models.Skills, models.UserSkills.skill_id == models.Skills.id)
        .filter(models.UserSkills.user_id == current_user.id)
        .order_by(models.UserSkills.proficiency.desc())
        .limit(10)
        .all()
    )

    accepted_projects = (
        db.query(models.ProjectSubmissions, models.Projects)
        .join(models.Projects, models.ProjectSubmissions.project_id == models.Projects.id)
        .filter(
            models.ProjectSubmissions.user_id == current_user.id,
            models.ProjectSubmissions.status == "accepted",
        )
        .all()
    )

    achievements = (
        db.query(models.UserAchievements, models.Achievements)
        .join(models.Achievements, models.UserAchievements.achievement_id == models.Achievements.id)
        .filter(models.UserAchievements.user_id == current_user.id)
        .all()
    )

    return {
        "full_name": current_user.full_name,
        "email": current_user.email,
        "bio": current_user.bio,
        "experience_level": current_user.experience_level,
        "skills": [
            {"name": skill.name, "proficiency": us.proficiency, "verified": us.verified}
            for us, skill in top_skills
        ],
        "projects": [
            {"title": project.title, "description": project.description, "score": sub.score}
            for sub, project in accepted_projects
        ],
        "achievements": [a.title for _, a in achievements],
    }
