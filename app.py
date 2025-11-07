# main.py
from flask import Flask, render_template
from config import Config
from extensions import db, login_manager
from models.models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth_bp.login"
    login_manager.session_protection = "strong"

    # Register blueprints
    from routes.auth import auth_bp
    from routes.teacher import teacher_bp
    from routes.student import student_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    # Home route
    @app.route("/")
    def home():
        return render_template("home.html")

    # Create database tables if not exist
    with app.app_context():
        db.create_all()

    return app

# User loader for Flask-Login


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Create the app instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
