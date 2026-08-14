"""
seed.py
--------
Populates the database with starter skills, careers (+ required-skill
mappings), a couple of sample challenges, and one assessment.

Run with:  python -m database.seed
"""

import json
import os

from database.database import SessionLocal, init_db
from database import models

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_json(filename: str):
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.load(f)


def seed_skills(db) -> dict[str, models.Skills]:
    skills_data = load_json("skills.json")
    skill_map = {}
    for item in skills_data:
        skill = db.query(models.Skills).filter(models.Skills.name == item["name"]).first()
        if not skill:
            skill = models.Skills(**item)
            db.add(skill)
            db.commit()
            db.refresh(skill)
        skill_map[skill.name] = skill
    return skill_map


def seed_careers(db, skill_map: dict[str, models.Skills]) -> None:
    careers_data = load_json("careers.json")
    for item in careers_data:
        career = db.query(models.Careers).filter(models.Careers.title == item["title"]).first()
        if not career:
            career = models.Careers(
                title=item["title"],
                description=item["description"],
                average_salary=item["average_salary"],
                growth_outlook=item["growth_outlook"],
            )
            db.add(career)
            db.commit()
            db.refresh(career)

        for req in item["required_skills"]:
            skill = skill_map.get(req["skill"])
            if not skill:
                continue
            existing = (
                db.query(models.CareerSkills)
                .filter(models.CareerSkills.career_id == career.id, models.CareerSkills.skill_id == skill.id)
                .first()
            )
            if not existing:
                db.add(
                    models.CareerSkills(
                        career_id=career.id,
                        skill_id=skill.id,
                        required_proficiency=req["required_proficiency"],
                        weight=req["weight"],
                    )
                )
        db.commit()


def seed_sample_challenges(db, skill_map: dict[str, models.Skills]) -> None:
    python_skill = skill_map.get("Python")
    if not python_skill:
        return

    samples = [
        {
            "title": "Reverse a String",
            "difficulty": models.DifficultyLevel.prerequisite,
            "prompt": "Write a function that reverses a string without using slicing.",
            "solution_criteria": {"keywords": ["def", "for", "return"]},
        },
        {
            "title": "Two Sum",
            "difficulty": models.DifficultyLevel.practice,
            "prompt": "Given a list of integers and a target, return indices of the two numbers that add up to it.",
            "solution_criteria": {"keywords": ["def", "dict", "return"]},
        },
        {
            "title": "Design a Rate Limiter",
            "difficulty": models.DifficultyLevel.advanced,
            "prompt": "Design and implement a token-bucket rate limiter as a Python class.",
            "solution_criteria": {"keywords": ["class", "def", "bucket", "time"]},
        },
    ]

    for s in samples:
        exists = db.query(models.Challenges).filter(models.Challenges.title == s["title"]).first()
        if not exists:
            db.add(models.Challenges(skill_id=python_skill.id, **s))
    db.commit()


def seed_sample_assessment(db, skill_map: dict[str, models.Skills]) -> None:
    exists = db.query(models.Assessments).filter(models.Assessments.title == "Backend Fundamentals").first()
    if exists:
        return

    python_skill = skill_map.get("Python")
    sql_skill = skill_map.get("SQL")

    questions = [
        {
            "question": "What does 'def' declare in Python?",
            "options": ["A variable", "A function", "A class", "A loop"],
            "answer": "A function",
            "skill_id": python_skill.id if python_skill else None,
        },
        {
            "question": "Which SQL clause filters rows before grouping?",
            "options": ["HAVING", "WHERE", "ORDER BY", "GROUP BY"],
            "answer": "WHERE",
            "skill_id": sql_skill.id if sql_skill else None,
        },
    ]
    db.add(models.Assessments(title="Backend Fundamentals", questions=questions))
    db.commit()


def run():
    init_db()
    db = SessionLocal()
    try:
        skill_map = seed_skills(db)
        seed_careers(db, skill_map)
        seed_sample_challenges(db, skill_map)
        seed_sample_assessment(db, skill_map)
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
