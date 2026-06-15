import os
from flask import Flask
from flask_cors import CORS
from app.models import db

def create_app(config_overrides=None):
    app = Flask(__name__)
    
    # Configure SQLite database file
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    if config_overrides:
        app.config.update(config_overrides)
    
    # Enable Cross-Origin Resource Sharing (CORS)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    db.init_app(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.quiz import quiz_bp
    from app.routes.questions import questions_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(quiz_bp, url_prefix='/api/quizzes')
    app.register_blueprint(questions_bp, url_prefix='/api')
    
    # Ensure tables are created on startup
    with app.app_context():
        db.create_all()
        
    return app
