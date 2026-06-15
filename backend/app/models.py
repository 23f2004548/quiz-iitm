from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attempts = db.relationship('Attempt', backref='user', lazy=True, cascade="all, delete-orphan")
    progress = db.relationship('UserProgress', backref='user', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "xp": self.xp,
            "level": self.level,
            "streak": self.streak,
            "last_active": self.last_active.isoformat() if self.last_active else None
        }

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # MCQ, NAT, COMMAND, TRUE_FALSE
    difficulty = db.Column(db.String(20), nullable=False)  # Easy, Medium, Hard, Expert
    subject = db.Column(db.String(100), nullable=False)  # e.g., Linux, Python, SQL, Math
    topic = db.Column(db.String(100), nullable=False)  # e.g., File Commands, Loops, Select Queries
    prompt = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)  # For MCQ: correct option text, NAT: numerical value, COMMAND: correct command pattern or exact match
    explanation = db.Column(db.Text, nullable=False)
    week = db.Column(db.Integer, default=1, nullable=False)
    tags = db.Column(db.String(255), nullable=True) # comma-separated tags
    
    options = db.relationship('QuestionOption', backref='question', lazy=True, cascade="all, delete-orphan")
    attempts = db.relationship('Attempt', backref='question', lazy=True, cascade="all, delete-orphan")
    bookmarks = db.relationship('Bookmark', backref='question', lazy=True, cascade="all, delete-orphan")

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'question_id', name='uq_user_bookmark'),)

class QuestionOption(db.Model):
    __tablename__ = 'question_options'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    option_text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

class Attempt(db.Model):
    __tablename__ = 'attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    user_answer = db.Column(db.Text, nullable=True)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    questions_attempted = db.Column(db.Integer, default=0)
    questions_correct = db.Column(db.Integer, default=0)

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_rel = db.relationship('User', backref=db.backref('comments_list', lazy=True))
    question_rel = db.relationship('Question', backref=db.backref('comments_list', lazy=True, cascade="all, delete-orphan"))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user_rel.username if self.user_rel else "Unknown",
            "comment_text": self.comment_text,
            "created_at": self.created_at.isoformat()
        }
