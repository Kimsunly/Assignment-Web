from flask import Blueprint, render_template

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
def dashboard():
    return render_template("admin/dashboard.html")


@admin_bp.route("/manage-users")
def manage_users():
    return render_template("admin/manage_users.html")
