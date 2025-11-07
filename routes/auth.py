from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from flask_login import login_user, logout_user, login_required
from models.models import User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == "admin":
                return redirect(url_for("admin_bp.dashboard"))
            elif user.role == "teacher":
                return redirect(url_for("teacher_bp.dashboard"))
            else:
                return redirect(url_for("student_bp.dashboard"))
        flash("Invalid credentials.")
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]

        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully!")
        return redirect(url_for("auth_bp.login"))

    return render_template("register.html")
