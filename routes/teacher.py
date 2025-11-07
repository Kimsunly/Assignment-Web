from flask import Blueprint, render_template

# ✅ Create the blueprint properly
teacher_bp = Blueprint("teacher_bp", __name__, url_prefix="/teacher")


@teacher_bp.route("/dashboard")
def dashboard():
    return render_template("teacher/dashboard.html")
