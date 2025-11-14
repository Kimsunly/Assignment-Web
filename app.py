# app.py
from flask import Flask, render_template
from config import Config
from extensions import db, login_manager, csrf
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload folders exist
    os.makedirs(app.config.get("UPLOAD_FOLDER",
                "static/uploads/assignments"), exist_ok=True)
    os.makedirs(app.config.get("SUBMISSION_FOLDER",
                "static/uploads/submissions"), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'
    login_manager.session_protection = 'strong'
    csrf.init_app(app)  # Initialize CSRF protection

    # Import models so SQLAlchemy recognizes them
    with app.app_context():
        import models.models  # registers User, Teacher, Student, Assignment, Class, Submission
        
        # Check if database exists and if schema is outdated
        db_file = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        db_exists = os.path.exists(db_file)
        
        # Drop and recreate all tables if RECREATE_DB environment variable is set
        if os.environ.get('RECREATE_DB', '').lower() == 'true':
            print("⚠️  RECREATE_DB is set to True - dropping all tables...")
            db.drop_all()
            print("✅ All tables dropped")
        elif db_exists:
            # Check if schema is outdated by testing a query
            try:
                from models.user import User
                # Try to query - if it fails, schema is outdated
                test_user = User.query.first()
            except Exception as e:
                if 'no such column' in str(e).lower():
                    print("⚠️  Detected outdated database schema. Recreating tables...")
                    print(f"   Error: {str(e)[:100]}")
                    db.drop_all()
                    print("✅ Old tables dropped")
                else:
                    raise
        
        db.create_all()
        print("✅ Database tables created/verified")

    # Define user loader AFTER models are imported
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.teacher import teacher_bp
    from routes.student import student_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    # Home route — redirects or shows welcome page
    @app.route('/')
    def home():
        return render_template('login.html')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    return app


app = create_app()

if __name__ == '__main__':
    # Only run in debug mode if explicitly set via environment variable
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)
