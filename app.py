# app.py
from flask import Flask, render_template
from config import Config
from extensions import db, login_manager
from models.user import User  # ✅ updated import


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ==============================
    # Initialize extensions
    # ==============================
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # ✅ match blueprint route name
    login_manager.session_protection = "strong"

    # ==============================
    # Register Blueprints
    # ==============================
    from routes.auth import auth_bp
    from routes.teacher import teacher_bp
    from routes.student import student_bp
    from routes.admin import admin_bp

    # ✅ Added URL prefixes for clarity
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(teacher_bp, url_prefix="/teacher")
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # ==============================
    # Basic route (homepage)
    # ==============================
    @app.route("/")
    def home():
        return render_template("base.html")

    # ==============================
    # Database initialization
    # ==============================
    with app.app_context():
        db.create_all()

    return app


# ==============================
# Flask-Login user loader
# ==============================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==============================
# Run the application
# ==============================
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
