from marshmallow import Schema, fields, post_load
from app.models import User, Question, QuestionOption, Attempt, UserProgress

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    xp = fields.Int(dump_only=True)
    level = fields.Int(dump_only=True)
    streak = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class QuestionOptionSchema(Schema):
    id = fields.Int(dump_only=True)
    option_text = fields.Str(required=True)
    is_correct = fields.Bool(dump_only=True) # Hidden from client during quiz generation

class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    type = fields.Str(required=True)
    difficulty = fields.Str(required=True)
    subject = fields.Str(required=True)
    topic = fields.Str(required=True)
    prompt = fields.Str(required=True)
    explanation = fields.Str(dump_only=True) # Hidden from client until after answering
    week = fields.Int(dump_only=True)
    tags = fields.Str(dump_only=True)
    options = fields.Nested(QuestionOptionSchema, many=True)

class AttemptSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    question_id = fields.Int(required=True)
    is_correct = fields.Bool(required=True)
    user_answer = fields.Str(allow_none=True)
    answered_at = fields.DateTime(dump_only=True)

class UserProgressSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    subject = fields.Str(required=True)
    topic = fields.Str(required=True)
    questions_attempted = fields.Int(dump_only=True)
    questions_correct = fields.Int(dump_only=True)
