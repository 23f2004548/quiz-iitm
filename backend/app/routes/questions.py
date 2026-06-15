from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import func, case, or_
from app.models import db, Question, QuestionOption, Attempt, UserProgress, Bookmark, Comment
from app.routes.auth import token_required

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/questions', methods=['GET'])
@token_required
def get_questions(current_user):
    # Base query
    query = Question.query
    
    # 0. Subject filter
    subject_filter = request.args.get('subject')
    if subject_filter:
        query = query.filter(Question.subject == subject_filter)
        
    # 1. Search filter (prompt, tags, topic, difficulty)
    search_query = request.args.get('search')
    if search_query:
        search_query = f"%{search_query.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(Question.prompt).like(search_query),
                func.lower(Question.tags).like(search_query),
                func.lower(Question.topic).like(search_query),
                func.lower(Question.difficulty).like(search_query)
            )
        )
    
    # 2. Week filter
    week_filter = request.args.get('week')
    if week_filter and week_filter.lower() != 'all':
        try:
            query = query.filter(Question.week == int(week_filter))
        except ValueError:
            pass
            
    # 3. Topic filter
    topic_filter = request.args.get('topic')
    if topic_filter and topic_filter.lower() != 'all':
        query = query.filter(Question.topic == topic_filter)
        
    # 4. Type filter
    type_filter = request.args.get('type')
    if type_filter and type_filter.lower() != 'all':
        db_type = type_filter.upper()
        if db_type == 'MULTIPLE SELECT' or db_type == 'MULTIPLE_SELECT':
            db_type = 'MSQ'
        elif db_type == 'CODING':
            db_type = 'COMMAND'
        query = query.filter(Question.type == db_type)
        
    # 5. Difficulty filter
    diff_filter = request.args.get('difficulty')
    if diff_filter and diff_filter.lower() != 'all':
        query = query.filter(Question.difficulty == diff_filter.capitalize())
        
    # 6. Status filter (Solved, Attempted, Unattempted, Bookmarked)
    status_filter = request.args.get('status')
    if status_filter and status_filter.lower() != 'all':
        attempted_qids = db.session.query(Attempt.question_id).filter_by(user_id=current_user.id)
        solved_qids = db.session.query(Attempt.question_id).filter_by(user_id=current_user.id, is_correct=True)
        bookmarked_qids = db.session.query(Bookmark.question_id).filter_by(user_id=current_user.id)
        
        if status_filter == 'solved':
            query = query.filter(Question.id.in_(solved_qids))
        elif status_filter == 'attempted':
            query = query.filter(Question.id.in_(attempted_qids))
        elif status_filter == 'unattempted':
            query = query.filter(~Question.id.in_(attempted_qids))
        elif status_filter == 'bookmarked':
            query = query.filter(Question.id.in_(bookmarked_qids))
            
    # Sorting
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')
    
    sort_col = Question.id
    if sort_by == 'difficulty':
        sort_col = case(
            (Question.difficulty == 'Easy', 1),
            (Question.difficulty == 'Medium', 2),
            (Question.difficulty == 'Hard', 3),
            (Question.difficulty == 'Expert', 4),
            else_=5
        )
    elif sort_by == 'week':
        sort_col = Question.week
    elif sort_by == 'type':
        sort_col = Question.type
    elif sort_by == 'topic':
        sort_col = Question.topic
        
    if sort_order == 'desc':
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
        
    # Pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Bulk fetch solve/attempt/bookmark states
    solved_set = {r[0] for r in db.session.query(Attempt.question_id).filter_by(user_id=current_user.id, is_correct=True).all()}
    attempted_set = {r[0] for r in db.session.query(Attempt.question_id).filter_by(user_id=current_user.id).all()}
    bookmarked_set = {r[0] for r in db.session.query(Bookmark.question_id).filter_by(user_id=current_user.id).all()}
    
    result = []
    for q in paginated.items:
        status = 'unattempted'
        if q.id in solved_set:
            status = 'solved'
        elif q.id in attempted_set:
            status = 'attempted'
            
        result.append({
            "id": q.id,
            "type": q.type,
            "difficulty": q.difficulty,
            "subject": q.subject,
            "topic": q.topic,
            "prompt": q.prompt,
            "week": q.week,
            "tags": [t.strip() for t in q.tags.split(',')] if q.tags else [],
            "status": status,
            "is_bookmarked": q.id in bookmarked_set
        })
        
    return jsonify({
        "questions": result,
        "total": paginated.total,
        "page": paginated.page,
        "pages": paginated.pages,
        "per_page": paginated.per_page
    }), 200

@questions_bp.route('/questions/<int:id>', methods=['GET'])
@token_required
def get_question_details(current_user, id):
    q = Question.query.get_or_404(id)
    
    solved = Attempt.query.filter_by(user_id=current_user.id, question_id=q.id, is_correct=True).first() is not None
    attempted = Attempt.query.filter_by(user_id=current_user.id, question_id=q.id).first() is not None
    is_bookmarked = Bookmark.query.filter_by(user_id=current_user.id, question_id=q.id).first() is not None
    
    status = 'unattempted'
    if solved:
        status = 'solved'
    elif attempted:
        status = 'attempted'
        
    options = [{"id": opt.id, "option_text": opt.option_text} for opt in q.options]
    
    return jsonify({
        "id": q.id,
        "type": q.type,
        "difficulty": q.difficulty,
        "subject": q.subject,
        "topic": q.topic,
        "prompt": q.prompt,
        "explanation": q.explanation,
        "week": q.week,
        "tags": [t.strip() for t in q.tags.split(',')] if q.tags else [],
        "status": status,
        "is_bookmarked": is_bookmarked,
        "options": options,
        "answer": q.answer
    }), 200

@questions_bp.route('/topics', methods=['GET'])
def get_topics():
    week = request.args.get('week')
    subject = request.args.get('subject')
    query = db.session.query(Question.topic).distinct()
    if subject:
        query = query.filter(Question.subject == subject)
    if week and week.lower() != 'all':
        try:
            query = query.filter(Question.week == int(week))
        except ValueError:
            pass
    topics = [r[0] for r in query.all() if r[0]]
    return jsonify({"topics": sorted(topics)}), 200

@questions_bp.route('/weeks', methods=['GET'])
def get_weeks():
    subject = request.args.get('subject')
    query = db.session.query(Question.week).distinct()
    if subject:
        query = query.filter(Question.subject == subject)
    weeks = [r[0] for r in query.order_by(Question.week.asc()).all() if r[0] is not None]
    return jsonify({"weeks": weeks}), 200

@questions_bp.route('/tags', methods=['GET'])
def get_tags():
    all_tags_rows = db.session.query(Question.tags).all()
    tags_set = set()
    for row in all_tags_rows:
        if row[0]:
            for t in row[0].split(','):
                cleaned = t.strip()
                if cleaned:
                    tags_set.add(cleaned)
    return jsonify({"tags": sorted(list(tags_set))}), 200

@questions_bp.route('/questions/<int:id>/bookmark', methods=['POST'])
@token_required
def toggle_bookmark(current_user, id):
    Question.query.get_or_404(id)
    
    existing = Bookmark.query.filter_by(user_id=current_user.id, question_id=id).first()
    if existing:
        db.session.delete(existing)
        is_bookmarked = False
    else:
        bookmark = Bookmark(user_id=current_user.id, question_id=id)
        db.session.add(bookmark)
        is_bookmarked = True
        
    db.session.commit()
    return jsonify({"is_bookmarked": is_bookmarked}), 200

@questions_bp.route('/user/progress', methods=['GET'])
@token_required
def get_user_statistics(current_user):
    subject_filter = request.args.get('subject')
    
    q_query = Question.query
    if subject_filter:
        q_query = q_query.filter(Question.subject == subject_filter)
    total_questions = q_query.count()
    
    solved_qids_query = db.session.query(Attempt.question_id).filter_by(user_id=current_user.id, is_correct=True).distinct()
    if subject_filter:
        solved_qids_query = solved_qids_query.join(Question, Question.id == Attempt.question_id).filter(Question.subject == subject_filter)
    solved_questions = solved_qids_query.count()
    
    attempted_qids_query = db.session.query(Attempt.question_id).filter_by(user_id=current_user.id).distinct()
    if subject_filter:
        attempted_qids_query = attempted_qids_query.join(Question, Question.id == Attempt.question_id).filter(Question.subject == subject_filter)
    attempted_questions = attempted_qids_query.count()
    
    attempts_query = Attempt.query.filter_by(user_id=current_user.id)
    if subject_filter:
        attempts_query = attempts_query.join(Question, Question.id == Attempt.question_id).filter(Question.subject == subject_filter)
    total_attempts = attempts_query.count()
    
    correct_attempts_query = Attempt.query.filter_by(user_id=current_user.id, is_correct=True)
    if subject_filter:
        correct_attempts_query = correct_attempts_query.join(Question, Question.id == Attempt.question_id).filter(Question.subject == subject_filter)
    correct_attempts = correct_attempts_query.count()
    
    accuracy = round((correct_attempts / total_attempts) * 100, 1) if total_attempts > 0 else 0.0
    
    streak = current_user.streak
    questions_remaining = max(0, total_questions - solved_questions)
    
    # Difficulty breakdown
    easy_query = Question.query.filter_by(difficulty='Easy')
    medium_query = Question.query.filter_by(difficulty='Medium')
    hard_query = Question.query.filter_by(difficulty='Hard')
    expert_query = Question.query.filter_by(difficulty='Expert')
    
    if subject_filter:
        easy_query = easy_query.filter(Question.subject == subject_filter)
        medium_query = medium_query.filter(Question.subject == subject_filter)
        hard_query = hard_query.filter(Question.subject == subject_filter)
        expert_query = expert_query.filter(Question.subject == subject_filter)
        
    easy_total = easy_query.count()
    medium_total = medium_query.count()
    hard_total = hard_query.count()
    expert_total = expert_query.count()
    
    easy_solved = Question.query.filter(Question.id.in_(solved_qids_query), Question.difficulty == 'Easy').count()
    medium_solved = Question.query.filter(Question.id.in_(solved_qids_query), Question.difficulty == 'Medium').count()
    hard_solved = Question.query.filter(Question.id.in_(solved_qids_query), Question.difficulty == 'Hard').count()
    expert_solved = Question.query.filter(Question.id.in_(solved_qids_query), Question.difficulty == 'Expert').count()
    
    return jsonify({
        "total_questions": total_questions,
        "solved_questions": solved_questions,
        "attempted_questions": attempted_questions,
        "accuracy": accuracy,
        "streak": streak,
        "questions_remaining": questions_remaining,
        "easy_total": easy_total,
        "easy_solved": easy_solved,
        "medium_total": medium_total,
        "medium_solved": medium_solved,
        "hard_total": hard_total,
        "hard_solved": hard_solved,
        "expert_total": expert_total,
        "expert_solved": expert_solved
    }), 200

@questions_bp.route('/questions/<int:id>/attempt', methods=['POST'])
@token_required
def attempt_question(current_user, id):
    question = Question.query.get_or_404(id)
    data = request.get_json()
    if not data or 'user_answer' not in data:
        return jsonify({"error": "Missing user_answer field"}), 400
        
    user_ans = data['user_answer']
    is_correct = False
    
    # Grading logic
    if question.type == 'MCQ':
        correct_option = QuestionOption.query.filter_by(question_id=id, is_correct=True).first()
        if correct_option and user_ans and correct_option.option_text.strip().lower() == str(user_ans).strip().lower():
            is_correct = True
    elif question.type == 'MSQ':
        correct_opts = QuestionOption.query.filter_by(question_id=id, is_correct=True).all()
        correct_texts = sorted([opt.option_text.strip().lower() for opt in correct_opts])
        
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
        try:
            if float(question.answer.strip()) == float(str(user_ans).strip()):
                is_correct = True
        except (ValueError, TypeError):
            if question.answer.strip().lower() == str(user_ans).strip().lower():
                is_correct = True
    elif question.type == 'COMMAND':
        acceptable = [a.strip().lower() for a in question.answer.split('||')]
        user_cmd = str(user_ans).strip().lower()
        user_cmd_normalized = " ".join(user_cmd.split())
        
        if user_cmd_normalized in acceptable:
            is_correct = True
        else:
            def get_cmd_tokens(cmd_str):
                parts = cmd_str.split()
                if not parts:
                    return set()
                cmd = parts[0]
                args = set()
                for p in parts[1:]:
                    if p.startswith('-') and len(p) > 1:
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
        if str(question.answer).strip().lower() == str(user_ans).strip().lower():
            is_correct = True
            
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
            
    # XP and Level updates
    xp_gained = 10 if is_correct else 2
    current_user.xp += xp_gained
    current_user.level = 1 + (current_user.xp // 100)
    
    # Streak update
    now = datetime.utcnow()
    if current_user.last_active:
        delta = now.date() - current_user.last_active.date()
        if delta.days == 1:
            current_user.streak += 1
        elif delta.days > 1:
            current_user.streak = 1
    else:
        current_user.streak = 1
        
    current_user.last_active = now
    db.session.commit()
    
    return jsonify({
        "is_correct": is_correct,
        "correct_answer": question.answer.split('||')[0] if '||' in question.answer else question.answer,
        "explanation": question.explanation,
        "xp_gained": xp_gained,
        "new_xp": current_user.xp,
        "new_level": current_user.level,
        "new_streak": current_user.streak
    }), 200

@questions_bp.route('/questions/<int:id>/comments', methods=['GET'])
def get_comments(id):
    Question.query.get_or_404(id)
    comments = Comment.query.filter_by(question_id=id).order_by(Comment.created_at.desc()).all()
    return jsonify({"comments": [c.to_dict() for c in comments]}), 200

@questions_bp.route('/questions/<int:id>/comments', methods=['POST'])
@token_required
def add_comment(current_user, id):
    Question.query.get_or_404(id)
    data = request.get_json()
    if not data or 'comment_text' not in data:
        return jsonify({"error": "Missing comment_text field"}), 400
        
    comment_text = data['comment_text'].strip()
    if not comment_text:
        return jsonify({"error": "Comment text cannot be empty"}), 400
        
    comment = Comment(
        user_id=current_user.id,
        question_id=id,
        comment_text=comment_text
    )
    db.session.add(comment)
    db.session.commit()
    
    return jsonify(comment.to_dict()), 201
