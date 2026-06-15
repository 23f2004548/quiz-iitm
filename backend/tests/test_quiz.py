import os
import tempfile
import pytest
from app import create_app
from app.models import db, User, Question, QuestionOption

@pytest.fixture
def client():
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app(config_overrides={
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'TESTING': True
    })
    
    with app.app_context():
        db.create_all()
        
        # Seed basic questions for testing
        q = Question(
            type="MCQ",
            difficulty="Easy",
            subject="Linux",
            topic="Basics",
            prompt="What command displays current directory?",
            answer="pwd",
            explanation="pwd stands for print working directory."
        )
        db.session.add(q)
        db.session.flush()
        
        opt = QuestionOption(
            question_id=q.id,
            option_text="pwd",
            is_correct=True
        )
        db.session.add(opt)
        db.session.commit()
        
    yield app.test_client()
    
    # Cleanup database file
    with app.app_context():
        db.session.remove()
        db.get_engine().dispose()
    os.close(db_fd)
    os.unlink(db_path)

def test_auth_flow(client):
    # Register test
    res = client.post('/api/auth/register', json={
        "username": "testguy",
        "email": "testguy@iitm.ac.in",
        "password": "mypassword"
    })
    assert res.status_code == 201
    assert "token" in res.get_json()
    
    # Login test
    res = client.post('/api/auth/login', json={
        "email": "testguy@iitm.ac.in",
        "password": "mypassword"
    })
    assert res.status_code == 200
    token = res.get_json()['token']
    assert token is not None

def test_quiz_endpoints(client):
    # Fetch questions
    res = client.get('/api/quizzes/generate?subject=Linux')
    assert res.status_code == 200
    questions = res.get_json()['questions']
    assert len(questions) > 0
    q_id = questions[0]['id']
    
    # Register user first to get token
    auth_res = client.post('/api/auth/register', json={
        "username": "coder",
        "email": "coder@iitm.ac.in",
        "password": "password"
    })
    token = auth_res.get_json()['token']
    
    # Submit answer
    headers = {"Authorization": f"Bearer {token}"}
    submit_res = client.post('/api/quizzes/submit', headers=headers, json={
        "answers": {
            str(q_id): "pwd"
        }
    })
    assert submit_res.status_code == 200
    result = submit_res.get_json()
    assert result['score'] == 1
    assert result['xp_gained'] == 10
