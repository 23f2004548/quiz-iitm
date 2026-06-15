import os
import tempfile
import pytest
from app import create_app
from app.models import db, Question, QuestionOption
from app.utils.ingester import validate_and_ingest_questions

@pytest.fixture
def app_ctx():
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    app = create_app(config_overrides={
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'TESTING': True
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.get_engine().dispose()
        
    os.close(db_fd)
    os.unlink(db_path)

def test_json_validation_and_insertion(app_ctx):
    with app_ctx.app_context():
        sample_questions = [
            {
                "question": "What does cd command do?",
                "type": "mcq",
                "difficulty": "easy",
                "options": ["Change Directory", "Create Directory", "Copy Directory", "Clear Disk"],
                "correct_answer": "Change Directory",
                "explanation": "cd changes working directory"
            },
            {
                "question": "Standard output stream descriptor?",
                "type": "nat",
                "difficulty": "medium",
                "correct_answer": "1"
            }
        ]
        
        imported, skipped = validate_and_ingest_questions(sample_questions, "Linux Test", "Ingest Test")
        assert imported == 2
        assert skipped == 0
        
        # Verify db records
        qs = Question.query.filter_by(subject="Linux Test").all()
        assert len(qs) == 2
        
        mcq_q = Question.query.filter_by(type="MCQ").first()
        assert mcq_q is not None
        assert len(mcq_q.options) == 4
        
        correct_opts = [o for o in mcq_q.options if o.is_correct]
        assert len(correct_opts) == 1
        assert correct_opts[0].option_text == "Change Directory"

def test_duplicate_prevention(app_ctx):
    with app_ctx.app_context():
        question = [
            {
                "question": "What is 2+2?",
                "type": "nat",
                "difficulty": "easy",
                "correct_answer": "4"
            }
        ]
        
        imported1, skipped1 = validate_and_ingest_questions(question, "Maths", "Calculations")
        assert imported1 == 1
        assert skipped1 == 0
        
        # Attempt to import again
        imported2, skipped2 = validate_and_ingest_questions(question, "Maths", "Calculations")
        assert imported2 == 0
        assert skipped2 == 1

def test_msq_and_coding_ingestion_and_grading(app_ctx):
    with app_ctx.app_context():
        sample_questions = [
            {
                "question": "Which of these are Linux commands?",
                "type": "multiple_select",
                "difficulty": "easy",
                "options": ["ls", "pwd", "select", "mkdir"],
                "correct_answers": ["ls", "pwd", "mkdir"]
            },
            {
                "question": "Rename old.txt to new.txt.",
                "type": "coding",
                "difficulty": "easy",
                "accepted_answers": ["mv old.txt new.txt"]
            }
        ]
        
        imported, skipped = validate_and_ingest_questions(sample_questions, "Linux Test", "Advanced Test")
        assert imported == 2
        assert skipped == 0
        
        # Verify MSQ
        msq_q = Question.query.filter_by(type="MSQ").first()
        assert msq_q is not None
        assert len(msq_q.options) == 4
        correct_opts = sorted([o.option_text for o in msq_q.options if o.is_correct])
        assert correct_opts == ["ls", "mkdir", "pwd"]
        assert msq_q.answer == "ls||pwd||mkdir"
        
        # Verify Coding mapped to COMMAND
        cmd_q = Question.query.filter_by(type="COMMAND").first()
        assert cmd_q is not None
        assert cmd_q.answer == "mv old.txt new.txt"
