from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.database import get_db
from database import models
from services import simulation_service
from core.security import get_current_user

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


class SimulationAttemptRequest(BaseModel):
    choices_made: list[str]


@router.get("/")
def list_simulations(career_id: str | None = None, db: Session = Depends(get_db)):
    return simulation_service.list_simulations(db, career_id)


@router.get("/{simulation_id}")
def get_simulation(simulation_id: str, db: Session = Depends(get_db)):
    return simulation_service.get_simulation(db, simulation_id)


@router.post("/{simulation_id}/attempt")
def submit_attempt(
    simulation_id: str,
    payload: SimulationAttemptRequest,
    current_user: models.UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return simulation_service.submit_attempt(db, current_user.id, simulation_id, payload.choices_made)
