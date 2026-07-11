from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        phone_number = request.form.get("phone_number")
        role = request.form.get("role")
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists.")
            return redirect(url_for("auth.register"))

        approval_status = "pending" if role == "staff" else "approved"
        new_user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password),
            phone_number=phone_number,
            role=role,
            approval_status=approval_status,
            blacklist_status=False,
        )
        db.session.add(new_user)
        db.session.commit()

        if role == "staff":
            flash("Registration submitted. Please wait for admin approval.")
        else:
            flash("Registration successful. You can now log in.")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        account = User.query.filter_by(email=email).first()

        if not account or not check_password_hash(account.password_hash, password):
            flash("Invalid email or password.")
            return redirect(url_for("auth.login"))

        if account.blacklist_status:
            flash("This account has been blacklisted.")
            return redirect(url_for("auth.login"))

        if account.role == "staff" and account.approval_status != "approved":
            flash("Your staff account is not yet approved by admin.")
            return redirect(url_for("auth.login"))

        login_user(account)

        if account.role == "admin":
            return redirect(url_for("admin.dashboard"))
        elif account.role == "staff":
            return redirect(url_for("staff.dashboard"))
        else:
            return redirect(url_for("trekker.browse_treks"))

    return render_template("login.html")

@auth_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
