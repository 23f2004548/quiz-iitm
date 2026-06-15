"""
seed_admin.py — Run once to create the admin demo account with realistic data.

Usage (from the quiz app root directory):
  cd "e:/personal projects/quiz app/backend"
  ..\venv\Scripts\python seed_admin.py

Credentials:
  Email:    admin@linuxmaster.dev
  Password: Admin@123
  Username: admin
"""

import sys
import os
import random
from datetime import datetime, timedelta

# Make the backend importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, User, Question, Attempt, UserProgress
from werkzeug.security import generate_password_hash

ADMIN_EMAIL    = "admin@linuxmaster.dev"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin@123"

app = create_app()

with app.app_context():
    # ── 1. Create or fetch admin user ──────────────────────────────────
    existing = User.query.filter_by(email=ADMIN_EMAIL).first()
    if existing:
        print(f"[seed] Admin user already exists (id={existing.id}). Skipping creation.")
        admin = existing
    else:
        admin = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password_hash=generate_password_hash(ADMIN_PASSWORD),
        )
        db.session.add(admin)
        db.session.flush()   # get admin.id before commit
        print(f"[seed] Created admin user id={admin.id}")

    # ── 2. Set XP / level / streak ────────────────────────────────────
    admin.xp         = 3200
    admin.level      = 33
    admin.streak     = 30
    admin.last_active = datetime.utcnow()

    # ── 3. Delete existing attempts for a clean re-seed ───────────────
    Attempt.query.filter_by(user_id=admin.id).delete()
    UserProgress.query.filter_by(user_id=admin.id).delete()
    db.session.flush()

    # ── 4. Seed attempts for the last 30 days ─────────────────────────
    all_questions = Question.query.all()
    if not all_questions:
        print("[seed] WARNING: No questions in the database. Run question seeding first.")
        db.session.rollback()
        sys.exit(1)

    today = datetime.utcnow().date()
    attempts_to_add = []

    for day_offset in range(30):  # day 0 = today, 29 = 29 days ago
        day = today - timedelta(days=29 - day_offset)

        # 15–25 questions per day → ~2–3 hours at 1.5 min/question
        daily_count = random.randint(15, 25)

        # Pick random questions
        day_questions = random.sample(all_questions, min(daily_count, len(all_questions)))

        for hour_offset, q in enumerate(day_questions):
            # Spread attempts through the day (8 AM – 11 PM)
            hour   = 8 + (hour_offset % 15)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            answered_at = datetime(day.year, day.month, day.day, hour, minute, second)

            # Admin is very good — 85–95 % accuracy
            is_correct = random.random() < random.uniform(0.85, 0.95)

            attempts_to_add.append(Attempt(
                user_id=admin.id,
                question_id=q.id,
                is_correct=is_correct,
                user_answer="seeded",
                answered_at=answered_at,
            ))

    db.session.add_all(attempts_to_add)
    db.session.flush()

    # ── 5. Rebuild UserProgress from the attempts just seeded ─────────
    progress_map: dict[tuple, list] = {}
    for att in attempts_to_add:
        q = next((x for x in all_questions if x.id == att.question_id), None)
        if not q:
            continue
        key = (q.subject, q.topic)
        if key not in progress_map:
            progress_map[key] = [0, 0]
        progress_map[key][0] += 1
        if att.is_correct:
            progress_map[key][1] += 1

    for (subject, topic), (attempted, correct) in progress_map.items():
        up = UserProgress(
            user_id=admin.id,
            subject=subject,
            topic=topic,
            questions_attempted=attempted,
            questions_correct=correct,
        )
        db.session.add(up)

    db.session.commit()

    total_att = len(attempts_to_add)
    total_corr = sum(1 for a in attempts_to_add if a.is_correct)
    print(f"\n[seed] Admin seeded successfully!")
    print(f"   Email:     {ADMIN_EMAIL}")
    print(f"   Password:  {ADMIN_PASSWORD}")
    print(f"   XP / Lvl:  {admin.xp} / {admin.level}")
    print(f"   Streak:    {admin.streak} days")
    print(f"   Attempts:  {total_att}  ({total_corr} correct, {round(total_corr/total_att*100,1)}% accuracy)")
    print(f"   Subjects:  {len(set(k[0] for k in progress_map))}")
