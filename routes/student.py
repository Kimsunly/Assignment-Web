from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models.student import Student
from models.assignment import Assignment  # <-- needed for queries

student_bp = Blueprint("student_bp", __name__, url_prefix="/student")

student_bp = Blueprint("student_bp", __name__, url_prefix="/student")


# -------------------------
# Dashboard
# -------------------------
@student_bp.route("/dashboard")
@login_required
def dashboard():
    student = Student.query.filter_by(user_id=current_user.id).first()

    stats = {
        "enrolled_classes": 4,
        "pending_assignments": 2,
        "submitted_assignments": 5,
        "average_grade": 85
    }

    assignments = []
    grades = []

    return render_template(
        "student/dashboard.html",
        student=student,
        stats=stats,
        assignments=assignments,
        grades=grades,
    )



# -------------------------
# Assignments
# -------------------------
@student_bp.route("/assignments")
@login_required
def assignments():
    # Example dynamic stats
    stats = {
        "total_assignments": Assignment.query.filter_by(student_id=current_user.id).count(),
        "due_this_week": Assignment.query.filter(
            Assignment.student_id == current_user.id,
            Assignment.due_date >= datetime.today(),
            Assignment.due_date <= datetime.today() + timedelta(days=7)
        ).count(),
        "pending_assignments": Assignment.query.filter_by(student_id=current_user.id, status="pending").count()
    }

    # Fetch actual assignments for the student if needed
    assignments = Assignment.query.filter_by(student_id=current_user.id).all()

    return render_template(
        "student/assignments.html",
        stats=stats,
        assignments=assignments
    )


# -------------------------
# Grades
# -------------------------
@student_bp.route("/grades")
@login_required
def grades():
    return render_template("student/grades.html")


# -------------------------
# Profile
# -------------------------
@student_bp.route("/profile")
@login_required
def profile():
    return render_template("student/profile.html")
