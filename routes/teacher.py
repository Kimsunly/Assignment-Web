from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.teacher import Teacher
from models.models import Class
from models.assignment import Assignment
from models.student import Student
from models.submission import Submission
from datetime import datetime, timedelta

teacher_bp = Blueprint("teacher_bp", __name__, url_prefix="/teacher")

# -------------------------
# Dashboard
# -------------------------
@teacher_bp.route("/dashboard")
@login_required
def dashboard():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    if not teacher:
        flash("Teacher profile not found. Please contact administrator.", "danger")
        return redirect(url_for('auth_bp.login'))

    # Dynamic stats - use .count() for lazy='dynamic' relationships
    total_classes = Class.query.filter_by(teacher_id=teacher.id).count()
    total_students = sum(c.students.count() for c in teacher.classes) if teacher.classes else 0
    
    # Get assignments needing grading
    pending_assignments = 0
    upcoming_deadlines = 0
    
    for cls in teacher.classes or []:
        for assignment in cls.assignments.all():
            # Count submissions that need grading
            pending_assignments += assignment.submissions.filter(Submission.grade.is_(None)).count()
            # Count assignments due in next 7 days
            if assignment.due_date:
                days_until_due = (assignment.due_date - datetime.utcnow()).days
                if 0 <= days_until_due <= 7:
                    upcoming_deadlines += 1

    stats = {
        "total_students": total_students,
        "total_classes": total_classes,
        "pending_assignments": pending_assignments,
        "upcoming_deadlines": upcoming_deadlines
    }

    # Recent classes - teacher.classes is a list, not dynamic
    recent_classes = (teacher.classes or [])[:5]
    recent_classes_data = [
        {"name": c.name, "student_count": c.students.count()} for c in recent_classes
    ]

    # Recent assignments
    all_assignments = []
    for cls in teacher.classes or []:
        for assignment in cls.assignments.all():
            graded_count = assignment.submissions.filter(Submission.grade.isnot(None)).count()
            total_count = assignment.submissions.count()
            all_assignments.append({
                'title': assignment.title,
                'due_date': assignment.due_date.strftime('%b %d, %Y') if assignment.due_date else 'No due date',
                'sort_date': assignment.due_date or datetime.utcnow(),
                'status': 'graded' if total_count > 0 and graded_count == total_count else 'pending'
            })
    recent_assignments = sorted(all_assignments, key=lambda x: x['sort_date'], reverse=True)[:5]
    # Remove sort_date before passing to template
    for a in recent_assignments:
        a.pop('sort_date', None)

    # Recent students with activity
    recent_students = []
    for cls in teacher.classes or []:
        for student in cls.students.limit(5).all():
            recent_students.append({
                'id': student.id,
                'first_name': student.first_name or '',
                'last_name': student.last_name or '',
                'full_name': student.full_name,
                'class_name': cls.name,
                'last_assignment': 'N/A',  # Could be enhanced to track last assignment
                'grade': None  # Could be enhanced to calculate average grade
            })

    return render_template(
        "teacher/dashboard.html",
        teacher=teacher,
        stats=stats,
        recent_classes=recent_classes_data,
        recent_assignments=recent_assignments,
        recent_students=recent_students
    )


# -------------------------
# My Students
# -------------------------
@teacher_bp.route("/students")
@login_required
def teacher_students():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    if not teacher:
        flash("Teacher profile not found. Please contact administrator.", "danger")
        return redirect(url_for('auth_bp.login'))
    
    # Get all students from teacher's classes
    all_students = []
    for cls in teacher.classes or []:
        for student in cls.students.all():
            all_students.append({
                'id': student.id,
                'first_name': student.first_name or '',
                'last_name': student.last_name or '',
                'full_name': student.full_name,
                'email': student.user.email if student.user else 'N/A',
                'class_name': cls.name,
                'enrollment_date': student.created_at.strftime('%b %d, %Y') if student.created_at else 'N/A',
                'status': 'Active'
            })
    
    return render_template("teacher/students.html", teacher=teacher, students=all_students)


# -------------------------
# Classes
# -------------------------
@teacher_bp.route("/classes")
@login_required
def teacher_classes():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    if not teacher:
        flash("Teacher profile not found. Please contact administrator.", "danger")
        return redirect(url_for('auth_bp.login'))
    
    classes_data = []
    for cls in teacher.classes or []:
        classes_data.append({
            'id': cls.id,
            'name': cls.name,
            'description': cls.description or 'No description',
            'student_count': cls.students.count(),
            'assignment_count': cls.assignments.count(),
            'created_at': cls.created_at.strftime('%b %d, %Y') if cls.created_at else 'N/A'
        })
    
    return render_template("teacher/classes.html", teacher=teacher, classes=classes_data)


# -------------------------
# Assignments
# -------------------------
@teacher_bp.route("/assignments")
@login_required
def teacher_assignments():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    if not teacher:
        flash("Teacher profile not found. Please contact administrator.", "danger")
        return redirect(url_for('auth_bp.login'))
    
    assignments_data = []
    for cls in teacher.classes or []:
        for assignment in cls.assignments.all():
            total_submissions = assignment.submissions.count()
            graded = assignment.submissions.filter(Submission.grade.isnot(None)).count()
            
            assignments_data.append({
                'id': assignment.id,
                'title': assignment.title,
                'class_name': cls.name,
                'due_date': assignment.due_date.strftime('%b %d, %Y') if assignment.due_date else 'No due date',
                'total_submissions': total_submissions,
                'graded': graded,
                'status': 'Completed' if graded == total_submissions and total_submissions > 0 else 'Pending'
            })
    
    return render_template("teacher/assignment.html", teacher=teacher, assignments=assignments_data)


# -------------------------
# Grades
# -------------------------
@teacher_bp.route("/grades")
@login_required
def teacher_grades():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    if not teacher:
        flash("Teacher profile not found. Please contact administrator.", "danger")
        return redirect(url_for('auth_bp.login'))
    
    grades_data = []
    for cls in teacher.classes or []:
        for assignment in cls.assignments.all():
            for submission in assignment.submissions.all():
                student_name = submission.student.full_name if submission.student else 'Unknown'
                grades_data.append({
                    'student_name': student_name,
                    'class_name': cls.name,
                    'assignment_title': assignment.title,
                    'submission_date': submission.submitted_at.strftime('%b %d, %Y') if submission.submitted_at else 'Not submitted',
                    'grade': submission.grade if submission.grade else 'Not graded',
                    'status': 'Graded' if submission.grade else 'Pending'
                })
    
    return render_template("teacher/grades.html", teacher=teacher, grades=grades_data)


# -------------------------
# Profile
# -------------------------
@teacher_bp.route("/profile", methods=['GET', 'POST'])
@login_required
def teacher_profile():
    from extensions import db
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    if not teacher:
        flash("Teacher profile not found. Please contact administrator.", "danger")
        return redirect(url_for('auth_bp.login'))
    
    if request.method == 'POST':
        # Handle profile update
        teacher.first_name = request.form.get('first_name')
        teacher.last_name = request.form.get('last_name')
        teacher.department = request.form.get('department')
        teacher.subject = request.form.get('subject')
        
        if teacher.user:
            teacher.user.email = request.form.get('email', teacher.user.email)
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'danger')
        
        return redirect(url_for('teacher_bp.teacher_profile'))
    
    return render_template("teacher/profile.html", teacher=teacher)


# -------------------------
# View a Student
# -------------------------
@teacher_bp.route("/student/<int:id>")
@login_required
def view_student(id):
    student = Student.query.get_or_404(id)
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    if not teacher:
        flash("Teacher profile not found.", "danger")
        return redirect(url_for('teacher_bp.dashboard'))
    
    # Get student's classes and assignments
    student_data = {
        'id': student.id,
        'first_name': student.first_name or '',
        'last_name': student.last_name or '',
        'full_name': student.full_name,
        'email': student.user.email if student.user else 'N/A',
        'classes': [],
        'assignments': []
    }
    
    # Get classes this student is in that are taught by this teacher
    # student.classes is a dynamic relationship, so we can use filter
    for cls in (student.classes.filter(Class.teacher_id == teacher.id).all() if student.classes else []):
        student_data['classes'].append({
            'name': cls.name,
            'description': cls.description or ''
        })
    
    # Get student's assignment submissions for this teacher's classes
    for submission in student.submissions.all():
        if submission.assignment and submission.assignment.class_obj and submission.assignment.class_obj.teacher_id == teacher.id:
            student_data['assignments'].append({
                'title': submission.assignment.title,
                'class_name': submission.assignment.class_obj.name,
                'submission_date': submission.submitted_at.strftime('%b %d, %Y') if submission.submitted_at else 'Not submitted',
                'grade': submission.grade if submission.grade else 'Not graded',
                'status': 'Graded' if submission.grade else 'Pending'
            })
    
    return render_template("teacher/view_student.html", student=student_data)