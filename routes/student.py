from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models.student import Student
from models.assignment import Assignment
from models.submission import Submission
from models.class_model import Class
from models.user import User
from extensions import db
from sqlalchemy import func

student_bp = Blueprint("student_bp", __name__, url_prefix="/student")


def get_student_or_redirect():
    """Helper function to get student profile or redirect if not found"""
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash("Student profile not found. Please contact administrator.", "danger")
        return None
    return student


def calculate_letter_grade(percentage):
    """Convert percentage to letter grade"""
    if percentage >= 97:
        return "A+"
    elif percentage >= 93:
        return "A"
    elif percentage >= 90:
        return "A-"
    elif percentage >= 87:
        return "B+"
    elif percentage >= 83:
        return "B"
    elif percentage >= 80:
        return "B-"
    elif percentage >= 77:
        return "C+"
    elif percentage >= 73:
        return "C"
    elif percentage >= 70:
        return "C-"
    elif percentage >= 67:
        return "D+"
    elif percentage >= 63:
        return "D"
    elif percentage >= 60:
        return "D-"
    else:
        return "F"


# -------------------------
# Dashboard
# -------------------------
@student_bp.route("/dashboard")
@login_required
def dashboard():
    student = get_student_or_redirect()
    if not student:
        return redirect(url_for('auth_bp.login'))

    # Calculate actual stats
    enrolled_classes = student.classes.count() if student.classes else 0

    # Get all assignments and submissions
    pending_assignments = 0
    submitted_assignments = 0
    total_grades = []

    for cls in (student.classes.all() if student.classes else []):
        for assignment in cls.assignments.all():
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()
            if submission:
                submitted_assignments += 1
                if submission.grade is not None:
                    total_grades.append(submission.grade)
            else:
                pending_assignments += 1

    average_grade = sum(total_grades) / \
        len(total_grades) if total_grades else 0

    stats = {
        "enrolled_classes": enrolled_classes,
        "pending_assignments": pending_assignments,
        "submitted_assignments": submitted_assignments,
        "average_grade": round(average_grade, 1)
    }

    # Get recent assignments
    recent_assignments = []
    all_cls_assignments = []
    for cls in (student.classes.all() if student.classes else []):
        for assignment in cls.assignments.all():
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()
            all_cls_assignments.append({
                'assignment': assignment,
                'submission': submission,
                'class_name': cls.name,
                'due_date': assignment.due_date or datetime.utcnow()
            })
    # Sort by due_date descending and take top 5
    recent_assignments = sorted(
        all_cls_assignments, key=lambda x: x['due_date'], reverse=True)[:5]
    # Remove the helper key
    for a in recent_assignments:
        a.pop('due_date', None)

    # Get recent grades
    recent_grades = []
    all_submissions = list(student.submissions.all()
                           ) if student.submissions else []
    # Sort by submitted_at descending
    all_submissions.sort(
        key=lambda s: s.submitted_at if s.submitted_at else datetime.utcnow(), reverse=True)
    for submission in all_submissions[:5]:
        if submission.grade is not None:
            recent_grades.append({
                'assignment_title': submission.assignment.title if submission.assignment else 'Unknown',
                'grade': submission.grade,
                'submitted_at': submission.submitted_at
            })

    return render_template(
        "student/dashboard.html",
        student=student,
        stats=stats,
        assignments=recent_assignments[:5],
        grades=recent_grades,
    )


# -------------------------
# Assignments
# -------------------------
@student_bp.route("/assignments")
@login_required
def assignments():
    student = get_student_or_redirect()
    if not student:
        return redirect(url_for('auth_bp.login'))

    # Get assignments from student's classes
    all_assignments = []
    for cls in (student.classes.all() if student.classes else []):
        for assignment in cls.assignments.all():
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()
            all_assignments.append({
                'assignment': assignment,
                'submission': submission,
                'class_name': cls.name
            })

    # Calculate stats
    total_assignments = len(all_assignments)
    today = datetime.utcnow()
    week_from_now = today + timedelta(days=7)
    due_this_week = sum(1 for a in all_assignments
                        if a['assignment'].due_date and today <= a['assignment'].due_date <= week_from_now)
    pending_assignments = sum(
        1 for a in all_assignments if not a['submission'])

    stats = {
        "total_assignments": total_assignments,
        "due_this_week": due_this_week,
        "pending_assignments": pending_assignments
    }

    return render_template(
        "student/assignments.html",
        student=student,
        stats=stats,
        assignments=all_assignments
    )


# -------------------------
# Grades
# -------------------------
@student_bp.route("/grades")
@login_required
def grades():
    student = get_student_or_redirect()
    if not student:
        return redirect(url_for('auth_bp.login'))

    # Get all graded submissions
    all_submissions = []
    total_grades = []

    for cls in (student.classes.all() if student.classes else []):
        for assignment in cls.assignments.all():
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()
            if submission and submission.grade is not None:
                all_submissions.append({
                    'assignment': assignment,
                    'submission': submission,
                    'class': cls,
                    'teacher': cls.teacher
                })
                total_grades.append(submission.grade)

    # Calculate overall stats
    overall_average = sum(total_grades) / \
        len(total_grades) if total_grades else 0
    overall_letter = calculate_letter_grade(
        overall_average) if total_grades else "N/A"
    graded_count = len(all_submissions)

    # Count pending grades (submitted but not graded)
    pending_grades = 0
    for cls in (student.classes.all() if student.classes else []):
        for assignment in cls.assignments.all():
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()
            if submission and submission.grade is None:
                pending_grades += 1

    overall_stats = {
        'average': round(overall_average, 1),
        'letter_grade': overall_letter,
        'graded_count': graded_count,
        'pending_count': pending_grades
    }

    # Calculate performance by subject (class)
    subjects_performance = []
    for cls in (student.classes.all() if student.classes else []):
        class_grades = []
        class_submissions = []

        for assignment in cls.assignments.all():
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()
            if submission and submission.grade is not None:
                class_grades.append(submission.grade)
                class_submissions.append(submission)

        if class_grades:
            avg = sum(class_grades) / len(class_grades)
            subjects_performance.append({
                'class': cls,
                'teacher': cls.teacher,
                'average': round(avg, 1),
                'letter_grade': calculate_letter_grade(avg),
                'assignments_count': len(class_submissions),
                'highest': max(class_grades),
                'lowest': min(class_grades)
            })

    # Sort submissions by date (most recent first)
    all_submissions.sort(
        key=lambda x: x['submission'].graded_at or x['submission'].submitted_at, reverse=True)

    # Calculate grade distribution
    grade_distribution = {
        'A': sum(1 for g in total_grades if g >= 90),
        'B': sum(1 for g in total_grades if 80 <= g < 90),
        'C': sum(1 for g in total_grades if 70 <= g < 80),
        'D': sum(1 for g in total_grades if 60 <= g < 70),
        'F': sum(1 for g in total_grades if g < 60)
    }

    total = sum(grade_distribution.values())
    if total > 0:
        grade_distribution_percent = {
            'A': round((grade_distribution['A'] / total) * 100),
            'B': round((grade_distribution['B'] / total) * 100),
            'C': round((grade_distribution['C'] / total) * 100),
            'D': round((grade_distribution['D'] / total) * 100),
            'F': round((grade_distribution['F'] / total) * 100)
        }
    else:
        grade_distribution_percent = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}

    return render_template(
        "student/grades.html",
        student=student,
        overall_stats=overall_stats,
        subjects_performance=subjects_performance,
        all_submissions=all_submissions,
        grade_distribution=grade_distribution_percent
    )


# -------------------------
# Profile
# -------------------------
@student_bp.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    student = get_student_or_redirect()
    if not student:
        return redirect(url_for('auth_bp.login'))

    if request.method == 'POST':
        # Handle profile update
        student.first_name = request.form.get('first_name', student.first_name)
        student.last_name = request.form.get('last_name', student.last_name)
        student.major = request.form.get('major', student.major)
        student.year = request.form.get('year', student.year)
        student.section = request.form.get('section', student.section)

        # Update user email if provided
        if student.user:
            new_email = request.form.get('email')
            if new_email and new_email != student.user.email:
                # Check if email is already taken
                if not User.query.filter(User.email == new_email, User.id != student.user.id).first():
                    student.user.email = new_email
                else:
                    flash('Email is already registered to another user.', 'danger')

        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'danger')

        return redirect(url_for('student_bp.profile'))

    # Calculate stats for profile
    enrolled_classes = student.classes.count() if student.classes else 0

    # Get all graded submissions for average
    total_grades = []
    total_assignments = 0

    for cls in (student.classes.all() if student.classes else []):
        for assignment in cls.assignments.all():
            total_assignments += 1
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()
            if submission and submission.grade is not None:
                total_grades.append(submission.grade)

    average_grade = round(sum(total_grades) /
                          len(total_grades), 1) if total_grades else 0

    profile_stats = {
        'courses': enrolled_classes,
        'average_grade': average_grade,
        'total_assignments': total_assignments
    }

    # Get current courses with grades
    current_courses = []
    for cls in (student.classes.all() if student.classes else []):
        class_grades = []

        for assignment in cls.assignments.all():
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()
            if submission and submission.grade is not None:
                class_grades.append(submission.grade)

        course_average = round(sum(class_grades) /
                               len(class_grades), 1) if class_grades else None

        current_courses.append({
            'class': cls,
            'teacher': cls.teacher,
            'average': course_average,
            'letter_grade': calculate_letter_grade(course_average) if course_average else 'N/A'
        })

    return render_template(
        "student/profile.html",
        student=student,
        profile_stats=profile_stats,
        current_courses=current_courses
    )
