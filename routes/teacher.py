from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.teacher import Teacher
from models.models import Class  # your class model
from models.assignment import Assignment
from models.student import Student

teacher_bp = Blueprint("teacher_bp", __name__, url_prefix="/teacher")

# -------------------------
# Dashboard
# -------------------------


@teacher_bp.route("/dashboard")
@login_required
def dashboard():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    # Dynamic stats
    total_classes = Class.query.filter_by(teacher_id=teacher.id).count()
    total_students = sum(len(c.students) for c in teacher.classes)

    stats = {
        "total_students": total_students,
        "total_classes": total_classes,
        # You can calculate pending assignments and upcoming deadlines dynamically later
        "pending_assignments": 12,
        "upcoming_deadlines": 3
    }

    # Recent classes
    recent_classes = teacher.classes[:5]  # first 5 classes
    # Each class has 'name' and 'students'
    recent_classes_data = [
        {"name": c.name, "student_count": len(c.students)} for c in recent_classes]

    return render_template(
        "teacher/dashboard.html",
        teacher=teacher,
        stats=stats,
        recent_classes=recent_classes_data,
        recent_assignments=[],  # later you can make this dynamic too
        recent_students=[]      # later you can make this dynamic too
    )



# -------------------------
# My Students
# -------------------------
@teacher_bp.route("/students")
@login_required
def teacher_students():
    # Fetch teacher students from DB
    return render_template("teacher/students.html")


# -------------------------
# Classes
# -------------------------
@teacher_bp.route("/classes")
@login_required
def teacher_classes():
    # Fetch teacher classes from DB
    return render_template("teacher/classes.html")


# -------------------------
# Assignments
# -------------------------
@teacher_bp.route("/assignments")
@login_required
def teacher_assignments():
    # Fetch assignments for teacher from DB
    return render_template("teacher/assignments.html")


# -------------------------
# Grades
# -------------------------
@teacher_bp.route("/grades")
@login_required
def teacher_grades():
    # Fetch grades for teacher's students
    return render_template("teacher/grades.html")


# -------------------------
# Profile
# -------------------------
@teacher_bp.route("/profile")
@login_required
def teacher_profile():
    # Fetch & update teacher profile
    return render_template("teacher/profile.html")


# -------------------------
# View a Student
# -------------------------
@teacher_bp.route("/student/<int:id>")
@login_required
def view_student(id):
    # Fetch student by ID
    student = Student.query.get_or_404(id)
    return render_template("teacher/view_student.html", student=student)
