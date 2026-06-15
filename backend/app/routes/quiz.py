import math
from datetime import datetime, date, timedelta
from collections import defaultdict
from flask import Blueprint, request, jsonify
from sqlalchemy import func
from app.models import db, User, Question, QuestionOption, Attempt, UserProgress
from app.routes.auth import token_required

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/generate', methods=['GET'])
def generate_quiz():
    subject = request.args.get('subject')
    topic = request.args.get('topic')
    difficulty = request.args.get('difficulty')
    week = request.args.get('week')
    q_type = request.args.get('type')
    limit = int(request.args.get('limit', 5))
    
    query = Question.query
    if subject:
        query = query.filter_by(subject=subject)
    if topic and topic.lower() != 'all':
        query = query.filter_by(topic=topic)
    if difficulty and difficulty.lower() != 'all':
        query = query.filter_by(difficulty=difficulty)
    if week and week.lower() != 'all':
        try:
            query = query.filter(Question.week == int(week))
        except ValueError:
            pass
    if q_type and q_type.lower() != 'all':
        db_type = q_type.upper()
        if db_type == 'MULTIPLE SELECT' or db_type == 'MULTIPLE_SELECT':
            db_type = 'MSQ'
        elif db_type == 'CODING':
            db_type = 'COMMAND'
        query = query.filter(Question.type == db_type)
        
    # Get random questions
    questions = query.order_by(db.func.random()).limit(limit).all()
    
    # Serialize questions
    result = []
    for q in questions:
        q_data = {
            "id": q.id,
            "type": q.type,
            "difficulty": q.difficulty,
            "subject": q.subject,
            "topic": q.topic,
            "prompt": q.prompt,
            "options": [{"id": opt.id, "option_text": opt.option_text} for opt in q.options]
        }
        result.append(q_data)
        
    return jsonify({"questions": result}), 200

@quiz_bp.route('/submit', methods=['POST'])
@token_required
def submit_quiz(current_user):
    data = request.get_json()
    if not data or 'answers' not in data:
        return jsonify({"error": "Missing answers field"}), 400
        
    answers = data['answers']  # Dict mapping question_id (str) -> user_answer (str)
    
    total_questions = len(answers)
    if total_questions == 0:
        return jsonify({"error": "No answers submitted"}), 400
        
    correct_count = 0
    results_detail = []
    xp_gained = 0
    
    for q_id_str, user_ans in answers.items():
        try:
            q_id = int(q_id_str)
        except ValueError:
            continue
            
        question = Question.query.get(q_id)
        if not question:
            continue
            
        is_correct = False
        
        # Grading logic based on question type
        if question.type == 'MCQ':
            # Check if user_ans matches the correct option text exactly
            # Find the correct option text
            correct_option = QuestionOption.query.filter_by(question_id=q_id, is_correct=True).first()
            if correct_option and user_ans and correct_option.option_text.strip().lower() == user_ans.strip().lower():
                is_correct = True
        elif question.type == 'MSQ':
            # Get all correct options from the database
            correct_opts = QuestionOption.query.filter_by(question_id=q_id, is_correct=True).all()
            correct_texts = sorted([opt.option_text.strip().lower() for opt in correct_opts])
            
            # Parse user answer (which can be a string separated by '||' or ',')
            if user_ans:
                user_ans_str = str(user_ans).strip()
                if user_ans_str.startswith('[') and user_ans_str.endswith(']'):
                    import json
                    try:
                        user_selected = json.loads(user_ans_str)
                    except Exception:
                        user_selected = [x.strip() for x in user_ans_str.split('||')]
                else:
                    if '||' in user_ans_str:
                        user_selected = [x.strip() for x in user_ans_str.split('||')]
                    else:
                        user_selected = [x.strip() for x in user_ans_str.split(',')]
                
                user_texts = sorted([x.strip().lower() for x in user_selected if x.strip()])
                if user_texts == correct_texts:
                    is_correct = True
        elif question.type == 'NAT':
            # Float comparison to allow "3" vs "3.0"
            try:
                if float(question.answer.strip()) == float(user_ans.strip()):
                    is_correct = True
            except (ValueError, TypeError):
                if question.answer.strip().lower() == str(user_ans).strip().lower():
                    is_correct = True
        elif question.type == 'COMMAND':
            # Standardize command check (strip leading/trailing space)
            # We also support list of acceptable commands split by '||'
            acceptable = [a.strip().lower() for a in question.answer.split('||')]
            user_cmd = str(user_ans).strip().lower()
            # Remove redundant spacing
            user_cmd_normalized = " ".join(user_cmd.split())
            
            if user_cmd_normalized in acceptable:
                is_correct = True
            else:
                # Basic normalization check for options order (e.g., ls -a -l vs ls -al vs ls -la)
                def get_cmd_tokens(cmd_str):
                    parts = cmd_str.split()
                    if not parts:
                        return set()
                    cmd = parts[0]
                    args = set()
                    for p in parts[1:]:
                        if p.startswith('-') and len(p) > 1:
                            # Split combined options, e.g., -al -> a, l
                            for char in p[1:]:
                                args.add(char)
                        else:
                            args.add(p)
                    return (cmd, args)
                
                user_parsed = get_cmd_tokens(user_cmd_normalized)
                if user_parsed:
                    for acc in acceptable:
                        acc_parsed = get_cmd_tokens(acc)
                        if user_parsed == acc_parsed:
                            is_correct = True
                            break
        else:
            # Fallback exact match
            if str(question.answer).strip().lower() == str(user_ans).strip().lower():
                is_correct = True
                
        if is_correct:
            correct_count += 1
            
        # Log attempt
        attempt = Attempt(
            user_id=current_user.id,
            question_id=question.id,
            is_correct=is_correct,
            user_answer=str(user_ans)
        )
        db.session.add(attempt)
        
        # Update UserProgress
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            subject=question.subject,
            topic=question.topic
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=current_user.id,
                subject=question.subject,
                topic=question.topic,
                questions_attempted=1,
                questions_correct=1 if is_correct else 0
            )
            db.session.add(progress)
        else:
            progress.questions_attempted += 1
            if is_correct:
                progress.questions_correct += 1
                
        results_detail.append({
            "question_id": question.id,
            "type": question.type,
            "prompt": question.prompt,
            "is_correct": is_correct,
            "user_answer": user_ans,
            "correct_answer": question.answer.split('||')[0] if '||' in question.answer else question.answer,
            "explanation": question.explanation
        })
        
    # Calculate XP gained (e.g., 10 XP per correct answer)
    xp_gained = correct_count * 10
    current_user.xp += xp_gained
    
    # Calculate level based on XP (every 100 XP is a level)
    new_level = 1 + (current_user.xp // 100)
    current_user.level = new_level
    
    # Update last active date & streak
    now = datetime.utcnow()
    if current_user.last_active:
        delta = now.date() - current_user.last_active.date()
        if delta.days == 0:
            pass  # Same day quiz — keep streak unchanged
        elif delta.days == 1:
            current_user.streak += 1  # Consecutive day — increment
        else:
            current_user.streak = 1  # Missed a day — reset
    else:
        current_user.streak = 1  # First quiz ever
        
    current_user.last_active = now
    
    db.session.commit()
    
    return jsonify({
        "score": correct_count,
        "total": total_questions,
        "xp_gained": xp_gained,
        "new_xp": current_user.xp,
        "new_level": current_user.level,
        "new_streak": current_user.streak,
        "details": results_detail
    }), 200

@quiz_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    users = User.query.order_by(User.xp.desc()).limit(10).all()
    result = [
        {
            "username": u.username,
            "xp": u.xp,
            "level": u.level,
            "streak": u.streak
        } for u in users
    ]
    return jsonify({"leaderboard": result}), 200

@quiz_bp.route('/progress', methods=['GET'])
@token_required
def get_progress(current_user):
    progress_records = UserProgress.query.filter_by(user_id=current_user.id).all()
    result = [
        {
            "subject": p.subject,
            "topic": p.topic,
            "questions_attempted": p.questions_attempted,
            "questions_correct": p.questions_correct,
            "accuracy": round((p.questions_correct / p.questions_attempted) * 100, 1) if p.questions_attempted > 0 else 0
        } for p in progress_records
    ]
    return jsonify({"progress": result}), 200

@quiz_bp.route('/activity', methods=['GET'])
@token_required
def get_activity(current_user):
    from datetime import timedelta
    from sqlalchemy import func
    # Retrieve attempts from the last 365 days (53 weeks)
    num_days = 365
    start_date = datetime.utcnow().date() - timedelta(days=num_days - 1)
    
    # Query database to get attempts grouped by date
    attempts = db.session.query(
        func.date(Attempt.answered_at).label('date'),
        func.count(Attempt.id).label('attempted'),
        func.sum(db.case((Attempt.is_correct == True, 1), else_=0)).label('solved')
    ).filter(
        Attempt.user_id == current_user.id,
        Attempt.answered_at >= start_date
    ).group_by(
        func.date(Attempt.answered_at)
    ).all()
    
    activity_map = {}
    for date_str, attempted, solved in attempts:
        activity_map[date_str] = {
            "attempted": attempted,
            "solved": int(solved) if solved is not None else 0
        }
        
    return jsonify({
        "activity": activity_map,
        "start_date": start_date.isoformat(),
        "end_date": datetime.utcnow().date().isoformat()
    }), 200


@quiz_bp.route('/analytics', methods=['GET'])
@token_required
def get_analytics(current_user):
    """Rich analytics endpoint for the progress dashboard.
    Returns daily/weekly/monthly question counts, accuracy, subject breakdown,
    estimated study hours, and streak info.
    """
    now = datetime.utcnow()
    today = now.date()

    # ── 1. Time-series: last 90 days, grouped by day ──
    ninety_days_ago = today - timedelta(days=89)
    daily_rows = db.session.query(
        func.date(Attempt.answered_at).label('day'),
        func.count(Attempt.id).label('attempted'),
        func.sum(db.case((Attempt.is_correct == True, 1), else_=0)).label('correct')
    ).filter(
        Attempt.user_id == current_user.id,
        Attempt.answered_at >= ninety_days_ago
    ).group_by(func.date(Attempt.answered_at)).all()

    # Build filled 90-day map
    daily_map = {}
    for row in daily_rows:
        daily_map[str(row.day)] = {
            'attempted': row.attempted,
            'correct': int(row.correct or 0),
            'hours': round((row.attempted * 1.5) / 60, 2)  # ~1.5 min/question estimate
        }

    # Pad missing days with zeros
    daily_series = []
    for i in range(90):
        d = (ninety_days_ago + timedelta(days=i)).isoformat()
        entry = daily_map.get(d, {'attempted': 0, 'correct': 0, 'hours': 0})
        daily_series.append({'date': d, **entry})

    # ── 2. Weekly aggregation (last 12 weeks) ──
    weekly_map = defaultdict(lambda: {'attempted': 0, 'correct': 0})
    for entry in daily_series:
        from datetime import date as date_cls
        d = date_cls.fromisoformat(entry['date'])
        week_label = f"W{d.isocalendar()[1]} '{str(d.year)[2:]}"
        weekly_map[week_label]['attempted'] += entry['attempted']
        weekly_map[week_label]['correct'] += entry['correct']
    weekly_series = [
        {'week': k, 'attempted': v['attempted'], 'correct': v['correct'],
         'hours': round((v['attempted'] * 1.5) / 60, 2)}
        for k, v in list(weekly_map.items())[-12:]
    ]

    # ── 3. Monthly aggregation (last 6 months) ──
    monthly_map = defaultdict(lambda: {'attempted': 0, 'correct': 0})
    for entry in daily_series:
        d = entry['date'][:7]  # YYYY-MM
        monthly_map[d]['attempted'] += entry['attempted']
        monthly_map[d]['correct'] += entry['correct']
    monthly_series = [
        {'month': k, 'attempted': v['attempted'], 'correct': v['correct'],
         'hours': round((v['attempted'] * 1.5) / 60, 2)}
        for k, v in sorted(monthly_map.items())[-6:]
    ]

    # ── 4. Subject breakdown ──
    subject_rows = db.session.query(
        Question.subject,
        func.count(Attempt.id).label('attempted'),
        func.sum(db.case((Attempt.is_correct == True, 1), else_=0)).label('correct')
    ).join(Question, Attempt.question_id == Question.id
    ).filter(Attempt.user_id == current_user.id
    ).group_by(Question.subject).all()

    subject_breakdown = [
        {
            'subject': row.subject,
            'attempted': row.attempted,
            'correct': int(row.correct or 0),
            'accuracy': round((int(row.correct or 0) / row.attempted) * 100, 1) if row.attempted > 0 else 0
        }
        for row in subject_rows
    ]

    # ── 5. Overall totals ──
    total_attempted = sum(e['attempted'] for e in daily_series)
    total_correct = sum(e['correct'] for e in daily_series)
    total_hours = round(sum(e['hours'] for e in daily_series), 1)

    # ── 6. Longest streak (compute from daily_series) ──
    longest_streak = 0
    cur_streak = 0
    for entry in daily_series:
        if entry['attempted'] > 0:
            cur_streak += 1
            longest_streak = max(longest_streak, cur_streak)
        else:
            cur_streak = 0

    return jsonify({
        'daily': daily_series,
        'weekly': weekly_series,
        'monthly': monthly_series,
        'subjects': subject_breakdown,
        'totals': {
            'attempted': total_attempted,
            'correct': total_correct,
            'accuracy': round((total_correct / total_attempted) * 100, 1) if total_attempted else 0,
            'hours': total_hours,
            'streak': current_user.streak,
            'longest_streak': longest_streak,
            'xp': current_user.xp,
            'level': current_user.level
        }
    }), 200


@quiz_bp.route('/ranking', methods=['GET'])
@token_required
def get_ranking(current_user):
    """Returns the current user's global rank (1-based, sorted by XP desc)."""
    rank = db.session.query(func.count(User.id)).filter(User.xp > current_user.xp).scalar()
    total_users = db.session.query(func.count(User.id)).scalar()
    return jsonify({
        'rank': rank + 1,
        'total_users': total_users,
        'xp': current_user.xp
    }), 200
