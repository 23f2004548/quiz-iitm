import json
from app.models import db, Question, QuestionOption

def map_topic_by_tags(tags_list, default_topic):
    tags_lower = [t.lower() for t in tags_list]
    if "redirection" in tags_lower:
        return "Redirection"
    if any(t in tags_lower for t in ["links", "hard-links", "symbolic-links"]):
        return "Links"
    if any(t in tags_lower for t in ["permissions", "octal", "chmod", "ls-l"]):
        return "Linux Permissions"
    if any(t in tags_lower for t in ["filesystem", "fhs", "etc", "root", "tmp", "var-log"]):
        return "Filesystem Hierarchy"
    if any(t in tags_lower for t in ["terminal", "basic-commands", "navigation", "listing", "ls", "pwd", "man", "manual", "clear"]):
        return "Basic Commands"
    if any(t in tags_lower for t in ["commands", "file", "mkdir", "cp", "mv", "rm", "touch"]):
        return "Basic Commands"
    return "Command Line Environment"

def validate_and_ingest_questions(questions_data, default_subject="Linux System Commands", default_topic="Week 1 Overview", default_week=1):
    """
    Ingests a list of questions (in JSON format) into the database.
    Normalizes difficulty and maps options for MCQ questions.
    """
    imported_count = 0
    skipped_count = 0

    for q_data in questions_data:
        prompt = q_data.get('question') or q_data.get('prompt')
        if not prompt:
            continue
            
        # Parse week early
        week = q_data.get('week')
        if week is None:
            q_id = q_data.get('id', '')
            if '_w1_' in q_id or '_w1' in q_id:
                week = 1
            else:
                week = default_week
        try:
            week = int(week)
        except (ValueError, TypeError):
            week = default_week

        # Normalize difficulty: easy -> Easy, medium -> Medium, hard -> Hard
        raw_diff = q_data.get('difficulty', 'Easy')
        difficulty = raw_diff.capitalize() if raw_diff else 'Easy'
        if difficulty not in ['Easy', 'Medium', 'Hard', 'Expert']:
            difficulty = 'Easy'
            
        q_type = (q_data.get('type') or 'MCQ').upper()
        if q_type == 'MULTIPLE_SELECT':
            q_type = 'MSQ'
        elif q_type == 'CODING':
            q_type = 'COMMAND'

        # Check for duplicates by prompt and week
        existing = Question.query.filter_by(prompt=prompt, week=week).first()
        if existing:
            skipped_count += 1
            continue
        
        # Determine answer
        correct_answer = q_data.get('correct_answer') or q_data.get('answer') or ''
        if q_type == 'MSQ':
            correct_answers = q_data.get('correct_answers', [])
            correct_answer = "||".join(correct_answers)
        elif q_type == 'COMMAND':
            accepted_answers = q_data.get('accepted_answers', [])
            if accepted_answers:
                correct_answer = "||".join(accepted_answers)
        
        # Subject, topic, and tags
        subject = q_data.get('subject') or default_subject
        raw_tags = q_data.get('tags', [])
        
        if isinstance(raw_tags, list):
            tags_list = [t.strip().lower() for t in raw_tags if t.strip()]
            tags_str = ",".join(tags_list)
        elif isinstance(raw_tags, str):
            tags_list = [t.strip().lower() for t in raw_tags.split(',') if t.strip()]
            tags_str = ",".join(tags_list)
        else:
            tags_list = []
            tags_str = ""
            
        # Dynamically map topic for week 1 Overview questions
        raw_topic = q_data.get('topic') or default_topic
        if raw_topic in ["Week 1 Overview", "Basics"]:
            topic = map_topic_by_tags(tags_list, raw_topic)
        else:
            topic = raw_topic


        explanation = q_data.get('explanation')
        if not explanation:
            if q_type == 'MSQ':
                explanation = f"The correct answers are: {', '.join(q_data.get('correct_answers', []))}."
            else:
                explanation = f"The correct answer is {correct_answer}."

        new_question = Question(
            type=q_type,
            difficulty=difficulty,
            subject=subject,
            topic=topic,
            prompt=prompt,
            answer=correct_answer,
            explanation=explanation,
            week=week,
            tags=tags_str
        )
        
        db.session.add(new_question)
        db.session.flush() # Populate new_question.id
        
        # Add options if MCQ or MSQ
        if q_type == 'MCQ':
            options = q_data.get('options', [])
            for opt_text in options:
                is_correct = (opt_text.strip().lower() == correct_answer.strip().lower())
                new_opt = QuestionOption(
                    question_id=new_question.id,
                    option_text=opt_text,
                    is_correct=is_correct
                )
                db.session.add(new_opt)
        elif q_type == 'MSQ':
            options = q_data.get('options', [])
            correct_answers = q_data.get('correct_answers', [])
            correct_answers_clean = [ans.strip().lower() for ans in correct_answers]
            for opt_text in options:
                is_correct = (opt_text.strip().lower() in correct_answers_clean)
                new_opt = QuestionOption(
                    question_id=new_question.id,
                    option_text=opt_text,
                    is_correct=is_correct
                )
                db.session.add(new_opt)
                
        imported_count += 1
        
    db.session.commit()
    return imported_count, skipped_count
