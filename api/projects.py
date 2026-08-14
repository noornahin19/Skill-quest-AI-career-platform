import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from schemas.project import ProjectCreate, ProjectOut, ProjectSubmissionOut, ProjectReviewRequest
from services import project_service
from core.security import get_current_user

router = APIRouter(prefix="/api/projects", tags=["projects"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    return project_service.create_project(db, payload)


@router.get("/", response_model=list[ProjectOut])
def list_projects(career_id: str | None = None, db: Session = Depends(get_db)):
    return project_service.list_projects(db, career_id)


@router.post("/{project_id}/submit", response_model=ProjectSubmissionOut)
def submit_project(
    project_id: str,
    repo_url: str | None = Form(None),
    file: UploadFile | None = File(None),
    current_user: models.UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from schemas.project import ProjectSubmissionCreate

    file_path = None
    if file:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())

    payload = ProjectSubmissionCreate(user_id=current_user.id, project_id=project_id, repo_url=repo_url)
    return project_service.submit_project(db, payload, file_path=file_path)


@router.patch("/submissions/{submission_id}/review", response_model=ProjectSubmissionOut)
def review_submission(submission_id: str, payload: ProjectReviewRequest, db: Session = Depends(get_db)):
    return project_service.review_submission(db, submission_id, payload)
