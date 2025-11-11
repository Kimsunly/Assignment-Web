# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from extensions import db
from models.user import User

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form['confirm_password']
        role = request.form["role"]

        # Check if passwords match FIRST
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth_bp.register'))

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", 'danger')
            return redirect(url_for("auth_bp.register"))

        # Create new user
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully!", 'success')
        return redirect(url_for("auth_bp.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", 'success')
            if user.role == "admin":
                return redirect(url_for("admin_bp.dashboard"))
            elif user.role == "teacher":
                return redirect(url_for("teacher_bp.dashboard"))
            else:
                return redirect(url_for("student_bp.dashboard"))
        flash("Invalid username or password.", 'danger')
    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", 'success')
    return redirect(url_for("auth_bp.login"))


# Add this at the end of your auth.py file
@auth_bp.route("/debug/check-users")
def check_users():
    from models.user import User
    users = User.query.all()

    if not users:
        return "<h2>No users in database yet</h2>"

    html = "<h2>Users in Database:</h2><ul>"
    for user in users:
        html += f"<li><strong>{user.username}</strong> - Role: {user.role} (ID: {user.id})</li>"
    html += "</ul>"
    html += f"<p>Total users: {len(users)}</p>"

    return html
