import os
from flask import Flask
from flask_cors import CORS
from app.models import db

def create_app(config_overrides=None):
    app = Flask(__name__)
    
    # Configure SQLite database file or environment database (PostgreSQL/MySQL)
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        # Flask-SQLAlchemy expects 'postgresql://' instead of 'postgres://'
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    else:
        # Fallback to local SQLite database
        docker_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../database.db'))
        local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../database.db'))
        
        # Check which path is valid
        if os.path.exists(os.path.dirname(local_path)):
            db_path = local_path
        else:
            db_path = docker_path
            
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
