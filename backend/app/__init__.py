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
        
        # In Docker (WORKDIR /app), local_path dirname resolves to '/' which is write-protected.
        # If the local parent dir is '/' or does not exist, use docker_path.
        local_parent = os.path.dirname(local_path)
        if local_parent == '/' or not os.path.exists(local_parent) or os.path.isdir('/app'):
            db_path = docker_path
        else:
            db_path = local_path
            
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
    
    @app.route('/')
    def health_check():
        return {"status": "healthy", "message": "LinuxMaster Backend API is running"}, 200
    
    # Ensure tables are created on startup
    with app.app_context():
        db.create_all()
        
    return app
