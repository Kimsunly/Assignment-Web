# app.py
from flask import Flask, render_template
from config import Config
from extensions import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'
    login_manager.session_protection = 'strong'

    # Import models so SQLAlchemy recognizes them
    with app.app_context():
        import models.models  # registers all models
        db.create_all()

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

    @app.route('/')
    def home():
        return render_template('login.html')
        
    print(">>> Database path:", app.config["SQLALCHEMY_DATABASE_URI"])

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
