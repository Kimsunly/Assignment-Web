# routes/teacher.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user

teacher_bp = Blueprint('teacher_bp', __name__,
                       url_prefix='/teacher', template_folder='templates')


@teacher_bp.route('/dashboard')
@login_required
def dashboard():
    # optionally check role
    if current_user.role != 'teacher':
        return "Unauthorized", 403
    # fetch teacher's assignments from DB as needed
    return render_template('teacher/dashboard.html')
