from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from extensions import db
from models.user import User
from models.student import Student
from models.teacher import Teacher

auth_bp = Blueprint("auth_bp", __name__)

# -------------------------
# REGISTER
# -------------------------


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role", "student")

        # 🧠 Validate form fields
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth_bp.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth_bp.register"))

        # 🧠 Check if user/email already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("auth_bp.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("auth_bp.register"))

        # 🧂 Hash password
        hashed_pw = generate_password_hash(password)

        # 💾 Create new user
        new_user = User(username=username, email=email,
                        password=hashed_pw, role=role)
        db.session.add(new_user)
        db.session.commit()

        # 🔗 Automatically create related profile
        if role == "student":
            student_profile = Student(user_id=new_user.id)
            db.session.add(student_profile)
        elif role == "teacher":
            teacher_profile = Teacher(user_id=new_user.id)
            db.session.add(teacher_profile)

        db.session.commit()

        flash("✅ Account created successfully! Please log in.", "success")
        return redirect(url_for("auth_bp.login"))

    return render_template("register.html")


# -------------------------
# LOGIN
# -------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")

            # Redirect based on role
            if user.role == "admin":
                return redirect(url_for("admin_bp.dashboard"))
            elif user.role == "teacher":
                return redirect(url_for("teacher_bp.dashboard"))
            else:
                return redirect(url_for("student_bp.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


# -------------------------
# LOGOUT
# -------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth_bp.login"))


# -------------------------
# DEBUG — View all users
# -------------------------
@auth_bp.route("/debug/check-users")
def check_users():
    users = User.query.all()

    if not users:
        return "<h2>No users in database yet</h2>"

    html = "<h2>Users in Database:</h2><ul>"
    for user in users:
        html += f"<li><strong>{user.username}</strong> - {user.email} - Role: {user.role} (ID: {user.id})</li>"
    html += "</ul>"
    html += f"<p>Total users: {len(users)}</p>"

    return html
