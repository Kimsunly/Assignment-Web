from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from models.user import User
from models.student import Student
from models.teacher import Teacher
from models.assignment import Assignment
from models.class_model import Class
from models.submission import Submission
from werkzeug.security import generate_password_hash
from datetime import datetime

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")


def admin_required(f):
    """Decorator to ensure user is authenticated and is an admin"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    # Get admin user info
    admin_user = current_user
    admin = {
        'id': admin_user.id,
        'first_name': 'Admin',
        'last_name': 'User',
        'email': admin_user.email,
        'username': admin_user.username
    }

    # Calculate actual stats from database
    total_users = User.query.count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_students = User.query.filter_by(role='student').count()
    total_assignments = Assignment.query.count()

    stats = {
        'total_users': total_users,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_assignments': total_assignments
    }

    # Get recent users (last 5 registered)
    recent_users_data = User.query.order_by(
        User.created_at.desc()).limit(5).all()
    recent_users = [{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'status': u.status,
        'created_at': u.created_at.strftime('%b %d, %Y') if u.created_at else 'N/A'
    } for u in recent_users_data]

    # Get recent activities (simplified - could be enhanced with activity log)
    recent_activities = []

    # Get all users for management
    all_users_data = User.query.all()
    all_users = [{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'status': u.status
    } for u in all_users_data]

    # Calculate assignment stats
    total_assignment_count = Assignment.query.count()
    pending_count = Assignment.query.filter_by(status='pending').count()
    graded_count = Submission.query.filter(
        Submission.grade.isnot(None)).count()

    # Count late assignments (past due date)
    now = datetime.utcnow()
    late_count = Assignment.query.filter(Assignment.due_date < now).count()

    assignment_stats = {
        'total': total_assignment_count,
        'pending': pending_count,
        'graded': graded_count,
        'late': late_count
    }

    system_health = {
        'active_sessions': 0,  # Could be tracked with session management
        'last_backup': 'N/A'   # Could be tracked with backup system
    }

    return render_template(
        "admin/dashboard.html",
        admin=admin,
        stats=stats,
        recent_users=recent_users,
        recent_activities=recent_activities,
        all_users=all_users,
        assignment_stats=assignment_stats,
        system_health=system_health
    )


@admin_bp.route("/users")
@admin_required
def manage_users():
    users_data = User.query.all()
    users = []
    for u in users_data:
        # Try to get profile names from related profiles (student/teacher)
        first_name = ''
        last_name = ''
        if hasattr(u, 'student_profile') and u.student_profile:
            first_name = u.student_profile.first_name or ''
            last_name = u.student_profile.last_name or ''
        elif hasattr(u, 'teacher_profile') and u.teacher_profile:
            first_name = u.teacher_profile.first_name or ''
            last_name = u.teacher_profile.last_name or ''
        else:
            # Fallback to username split
            parts = (u.username or '').split('.')
            first_name = parts[0].capitalize(
            ) if parts and parts[0] else u.username
            last_name = ''

        users.append({
            'id': u.id,
            'username': u.username,
            'first_name': first_name,
            'last_name': last_name,
            'email': u.email,
            'role': u.role,
            'status': u.status,
            'created_at': u.created_at
        })

    return render_template("admin/manage_users.html", users=users)


@admin_bp.route("/teachers")
@admin_required
def manage_teachers():
    teachers_data = Teacher.query.all()
    teachers = [{
        'id': t.id,
        'first_name': t.first_name or '',
        'last_name': t.last_name or '',
        'full_name': t.full_name,
        'email': t.user.email if t.user else 'N/A',
        'department': t.department or 'N/A',
        'subject': t.subject or 'N/A',
        'username': t.user.username if t.user else 'N/A'
    } for t in teachers_data]
    return render_template("admin/manage_teachers.html", teachers=teachers)


@admin_bp.route("/students")
@admin_required
def manage_students():
    students_data = Student.query.all()
    students = [{
        'id': s.id,
        'first_name': s.first_name or '',
        'last_name': s.last_name or '',
        'full_name': s.full_name,
        'email': s.user.email if s.user else 'N/A',
        'major': s.major or 'N/A',
        'year': s.year or 'N/A',
        'section': s.section or 'N/A',
        'username': s.user.username if s.user else 'N/A'
    } for s in students_data]
    return render_template("admin/manage_students.html", students=students)


@admin_bp.route("/assignments")
@admin_required
def manage_assignments():
    assignments_data = Assignment.query.all()
    assignments = [{
        'id': a.id,
        'title': a.title,
        'description': a.description[:100] + '...' if len(a.description) > 100 else a.description,
        'due_date': a.due_date.strftime('%b %d, %Y') if a.due_date else 'N/A',
        'status': a.status,
        'teacher': a.teacher.full_name if a.teacher else 'N/A',
        'class': a.class_obj.name if a.class_obj else 'N/A',
        'submissions_count': a.submissions.count()
    } for a in assignments_data]
    return render_template("admin/manage_assignments.html", assignments=assignments)


@admin_bp.route("/roles")
@admin_required
def manage_roles():
    users_data = User.query.all()
    users = []
    for u in users_data:
        first_name = ''
        last_name = ''
        if hasattr(u, 'student_profile') and u.student_profile:
            first_name = u.student_profile.first_name or ''
            last_name = u.student_profile.last_name or ''
        elif hasattr(u, 'teacher_profile') and u.teacher_profile:
            first_name = u.teacher_profile.first_name or ''
            last_name = u.teacher_profile.last_name or ''
        else:
            parts = (u.username or '').split('.')
            first_name = parts[0].capitalize(
            ) if parts and parts[0] else u.username
            last_name = parts[1].capitalize() if len(parts) > 1 else ''

        users.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'role': u.role,
            'status': u.status,
            'first_name': first_name,
            'last_name': last_name,
            'created_at': u.created_at,
            'last_login': u.last_login.strftime('%b %d, %Y') if getattr(u, 'last_login', None) else None
        })

    return render_template("admin/manage_roles.html", users=users)


@admin_bp.route("/profile", methods=['GET', 'POST'])
@admin_required
def edit_profile():
    admin_user = current_user

    if request.method == 'POST':
        admin_user.email = request.form.get('email', admin_user.email)

        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'danger')

        return redirect(url_for('admin_bp.edit_profile'))

    admin = {
        'id': admin_user.id,
        'first_name': 'Admin',
        'last_name': 'User',
        'email': admin_user.email,
        'username': admin_user.username
    }
    return render_template("admin/edit_profile.html", admin=admin)


@admin_bp.route("/users/add", methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student')

        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('admin_bp.add_user'))

        # Check if user already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('admin_bp.add_user'))

        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role=role
        )

        try:
            db.session.add(new_user)
            db.session.commit()

            # Create profile based on role
            if role == 'student':
                student = Student(user_id=new_user.id)
                db.session.add(student)
            elif role == 'teacher':
                teacher = Teacher(user_id=new_user.id)
                db.session.add(teacher)

            db.session.commit()
            flash('User added successfully!', 'success')
            return redirect(url_for('admin_bp.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'danger')

    return render_template("admin/add_user.html")


@admin_bp.route("/teachers/add", methods=['GET', 'POST'])
@admin_required
def add_teacher():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        department = request.form.get('department')
        subject = request.form.get('subject')

        if not username or not email or not password:
            flash('Username, email, and password are required.', 'danger')
            return redirect(url_for('admin_bp.add_teacher'))

        # Check if user already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('admin_bp.add_teacher'))

        try:
            # Create user
            new_user = User(
                username=username,
                email=email,
                password=generate_password_hash(password),
                role='teacher'
            )
            db.session.add(new_user)
            db.session.flush()

            # Create teacher profile
            teacher = Teacher(
                user_id=new_user.id,
                first_name=first_name,
                last_name=last_name,
                department=department,
                subject=subject
            )
            db.session.add(teacher)
            db.session.commit()
            flash('Teacher added successfully!', 'success')
            return redirect(url_for('admin_bp.manage_teachers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating teacher: {str(e)}', 'danger')

    return render_template("admin/add_teacher.html")


@admin_bp.route("/students/add", methods=['GET', 'POST'])
@admin_required
def add_student():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        major = request.form.get('major')
        year = request.form.get('year')
        section = request.form.get('section')

        if not username or not email or not password:
            flash('Username, email, and password are required.', 'danger')
            return redirect(url_for('admin_bp.add_student'))

        # Check if user already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('admin_bp.add_student'))

        try:
            # Create user
            new_user = User(
                username=username,
                email=email,
                password=generate_password_hash(password),
                role='student'
            )
            db.session.add(new_user)
            db.session.flush()

            # Create student profile
            student = Student(
                user_id=new_user.id,
                first_name=first_name,
                last_name=last_name,
                major=major,
                year=year,
                section=section
            )
            db.session.add(student)
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('admin_bp.manage_students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating student: {str(e)}', 'danger')

    return render_template("admin/add_student.html")


@admin_bp.route("/settings")
@admin_required
def system_settings():
    return render_template("admin/system_settings.html")


@admin_bp.route("/activity-log")
@admin_required
def activity_log():
    # Simplified activity log - could be enhanced with actual activity tracking
    activities = []

    # Get recent user registrations
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    for user in recent_users:
        activities.append({
            'type': 'user_registered',
            'description': f'New {user.role} registered: {user.username}',
            'timestamp': user.created_at if user.created_at else datetime.utcnow()
        })

    # Sort by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)

    return render_template("admin/activity_log.html", activities=activities)


@admin_bp.route("/users/<int:user_id>")
@admin_required
def view_user(user_id):
    user_data = User.query.get_or_404(user_id)
    user = {
        'id': user_data.id,
        'username': user_data.username,
        'email': user_data.email,
        'role': user_data.role,
        'status': user_data.status,
        'created_at': user_data.created_at.strftime('%b %d, %Y') if user_data.created_at else 'N/A'
    }

    # Get profile info based on role
    if user_data.role == 'student' and user_data.student_profile:
        profile = user_data.student_profile
        user['profile'] = {
            'first_name': profile.first_name or '',
            'last_name': profile.last_name or '',
            'major': profile.major or 'N/A',
            'year': profile.year or 'N/A',
            'section': profile.section or 'N/A'
        }
    elif user_data.role == 'teacher' and user_data.teacher_profile:
        profile = user_data.teacher_profile
        user['profile'] = {
            'first_name': profile.first_name or '',
            'last_name': profile.last_name or '',
            'department': profile.department or 'N/A',
            'subject': profile.subject or 'N/A'
        }

    return render_template("admin/view_user.html", user=user)


@admin_bp.route("/users/<int:user_id>/change-role", methods=['GET', 'POST'])
@admin_required
def change_role(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        new_role = request.form.get('role')
        if new_role not in ['admin', 'teacher', 'student']:
            flash('Invalid role.', 'danger')
            return redirect(url_for('admin_bp.change_role', user_id=user_id))

        old_role = user.role
        user.role = new_role

        try:
            # If role changed, update profile
            if old_role != new_role:
                # Remove old profile
                if old_role == 'student' and user.student_profile:
                    db.session.delete(user.student_profile)
                elif old_role == 'teacher' and user.teacher_profile:
                    db.session.delete(user.teacher_profile)

                # Create new profile
                if new_role == 'student' and not user.student_profile:
                    student = Student(user_id=user.id)
                    db.session.add(student)
                elif new_role == 'teacher' and not user.teacher_profile:
                    teacher = Teacher(user_id=user.id)
                    db.session.add(teacher)

            db.session.commit()
            flash('Role changed successfully!', 'success')
            return redirect(url_for('admin_bp.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error changing role: {str(e)}', 'danger')

    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    }
    return render_template("admin/manage_role.html", user=user_data)


@admin_bp.route("/users/<int:user_id>/delete", methods=['POST', 'DELETE'])
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'You cannot delete your own account'}), 400

    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'User deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
