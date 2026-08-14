from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from database import models


def list_simulations(db: Session, career_id: str | None = None) -> list[models.CareerSimulations]:
    query = db.query(models.CareerSimulations)
    if career_id:
        query = query.filter(models.CareerSimulations.career_id == career_id)
    return query.all()


def get_simulation(db: Session, simulation_id: str) -> models.CareerSimulations:
    sim = db.query(models.CareerSimulations).filter(models.CareerSimulations.id == simulation_id).first()
    if not sim:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Simulation not found")
    return sim


def score_decision_path(decision_tree: dict, choices_made: list[str]) -> float:
    """
    Walks the decision tree node-by-node, summing each chosen branch's
    'score' value. Tree shape: {node_id: {choices: [{label, next, score}]}}.
    Falls back gracefully if choices don't match the tree.
    """
    if not decision_tree:
        return 0.0

    total = 0.0
    node_id = "start"
    for choice_label in choices_made:
        node = decision_tree.get(node_id)
        if not node:
            break
        match = next((c for c in node.get("choices", []) if c["label"] == choice_label), None)
        if not match:
            break
        total += match.get("score", 0)
        node_id = match.get("next", "")

    return round(total, 2)


def submit_attempt(
    db: Session, user_id: str, simulation_id: str, choices_made: list[str]
) -> models.SimulationAttempts:
    sim = get_simulation(db, simulation_id)
    outcome_score = score_decision_path(sim.decision_tree or {}, choices_made)

    attempt = models.SimulationAttempts(
        user_id=user_id,
        simulation_id=simulation_id,
        choices_made=choices_made,
        outcome_score=outcome_score,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt
