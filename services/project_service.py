from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from database import models
from schemas.project import ProjectCreate, ProjectSubmissionCreate, ProjectReviewRequest
from services import skill_dna_service


def create_project(db: Session, payload: ProjectCreate) -> models.Projects:
    project = models.Projects(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def list_projects(db: Session, career_id: str | None = None) -> list[models.Projects]:
    query = db.query(models.Projects)
    if career_id:
        query = query.filter(models.Projects.career_id == career_id)
    return query.all()


def submit_project(
    db: Session, payload: ProjectSubmissionCreate, file_path: str | None = None
) -> models.ProjectSubmissions:
    project = db.query(models.Projects).filter(models.Projects.id == payload.project_id).first()
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")

    submission = models.ProjectSubmissions(
        user_id=payload.user_id,
        project_id=payload.project_id,
        repo_url=payload.repo_url,
        file_path=file_path,
        status="submitted",
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def review_submission(
    db: Session, submission_id: str, review: ProjectReviewRequest
) -> models.ProjectSubmissions:
    submission = (
        db.query(models.ProjectSubmissions)
        .filter(models.ProjectSubmissions.id == submission_id)
        .first()
    )
    if not submission:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Submission not found")

    submission.status = review.status
    submission.feedback = review.feedback
    submission.score = review.score
    db.commit()
    db.refresh(submission)

    # A well-reviewed accepted project reinforces the skills it required
    if review.status == "accepted" and review.score is not None:
        project = db.query(models.Projects).filter(models.Projects.id == submission.project_id).first()
        for skill_id in (project.required_skills or []):
            skill_dna_service.bump_proficiency_from_challenge_score(
                db, submission.user_id, skill_id, review.score
            )

    return submission
