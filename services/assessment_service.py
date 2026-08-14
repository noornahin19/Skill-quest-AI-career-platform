from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from database import models
from services import skill_dna_service


def create_assessment(db: Session, title: str, career_id: str | None, questions: list[dict]) -> models.Assessments:
    assessment = models.Assessments(title=title, career_id=career_id, questions=questions)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def get_assessment(db: Session, assessment_id: str) -> models.Assessments:
    assessment = db.query(models.Assessments).filter(models.Assessments.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Assessment not found")
    return assessment


def grade_assessment(
    db: Session, user_id: str, assessment_id: str, answers: dict[str, str]
) -> models.AssessmentAttempts:
    """
    Grades each question, tallies per-skill correctness, updates Skill DNA
    for every skill touched by the assessment, and stores the attempt.
    """
    assessment = get_assessment(db, assessment_id)
    questions = assessment.questions

    per_skill_correct: dict[str, int] = {}
    per_skill_total: dict[str, int] = {}
    correct_count = 0

    for idx, q in enumerate(questions):
        skill_id = q.get("skill_id")
        given = answers.get(str(idx))
        is_correct = given is not None and given == q.get("answer")

        if skill_id:
            per_skill_total[skill_id] = per_skill_total.get(skill_id, 0) + 1
            if is_correct:
                per_skill_correct[skill_id] = per_skill_correct.get(skill_id, 0) + 1

        if is_correct:
            correct_count += 1

    score = round(100 * correct_count / len(questions), 2) if questions else 0.0

    result_summary = {
        skill_id: round(100 * per_skill_correct.get(skill_id, 0) / total, 2)
        for skill_id, total in per_skill_total.items()
    }

    attempt = models.AssessmentAttempts(
        user_id=user_id,
        assessment_id=assessment_id,
        answers=answers,
        score=score,
        result_summary=result_summary,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    # Feed each skill's assessment performance into the user's Skill DNA
    for skill_id, skill_score in result_summary.items():
        skill_dna_service.bump_proficiency_from_challenge_score(db, user_id, skill_id, skill_score)

    return attempt
