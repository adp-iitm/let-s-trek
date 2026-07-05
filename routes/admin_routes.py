from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from models import db, User, Trek, Booking

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


def admin_only(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Admin access required.")
            return redirect(url_for("auth.login"))
        return view_function(*args, **kwargs)
    return wrapper


@admin_blueprint.route("/dashboard")
@login_required
@admin_only
def dashboard():
    total_treks = Trek.query.count()
    total_trekkers = User.query.filter_by(role="trekker").count()
    total_staff = User.query.filter_by(role="staff").count()
    total_bookings = Booking.query.count()
    pending_staff = User.query.filter_by(role="staff", approval_status="pending").count()
    return render_template(
        "admin/dashboard.html",
        total_treks=total_treks,
        total_trekkers=total_trekkers,
        total_staff=total_staff,
        total_bookings=total_bookings,
        pending_staff=pending_staff,
    )


@admin_blueprint.route("/treks")
@login_required
@admin_only
def manage_treks():
    search_term = request.args.get("search_term", "")
    if search_term:
        treks = Trek.query.filter(Trek.trek_title.ilike(f"%{search_term}%")).all()
    else:
        treks = Trek.query.all()
    return render_template("admin/treks.html", treks=treks, search_term=search_term)


@admin_blueprint.route("/treks/add", methods=["GET", "POST"])
@login_required
@admin_only
def add_trek():
    if request.method == "POST":
        new_trek = Trek(
            trek_title=request.form.get("trek_title"),
            destination=request.form.get("destination"),
            difficulty_level=request.form.get("difficulty_level"),
            duration_days=int(request.form.get("duration_days")),
            start_date=datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date(),
            end_date=datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date(),
            remaining_slots=int(request.form.get("remaining_slots")),
            current_status="Open",
            description=request.form.get("description"),
        )
        db.session.add(new_trek)
        db.session.commit()
        flash("Trek added successfully.")
        return redirect(url_for("admin.manage_treks"))
    return render_template("admin/add_trek.html")


@admin_blueprint.route("/treks/edit/<int:trek_id>", methods=["GET", "POST"])
@login_required
@admin_only
def edit_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if request.method == "POST":
        trek.trek_title = request.form.get("trek_title")
        trek.destination = request.form.get("destination")
        trek.difficulty_level = request.form.get("difficulty_level")
        trek.duration_days = int(request.form.get("duration_days"))
        trek.start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
        trek.end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()
        trek.remaining_slots = int(request.form.get("remaining_slots"))
        trek.current_status = request.form.get("current_status")
        trek.description = request.form.get("description")
        db.session.commit()
        flash("Trek updated successfully.")
        return redirect(url_for("admin.manage_treks"))
    return render_template("admin/edit_trek.html", trek=trek)


@admin_blueprint.route("/treks/delete/<int:trek_id>")
@login_required
@admin_only
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    flash("Trek deleted.")
    return redirect(url_for("admin.manage_treks"))


@admin_blueprint.route("/treks/assign/<int:trek_id>", methods=["GET", "POST"])
@login_required
@admin_only
def assign_staff(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    approved_staff = User.query.filter_by(role="staff", approval_status="approved", blacklist_status=False).all()
    if request.method == "POST":
        trek.guide_id = int(request.form.get("staff_id"))
        db.session.commit()
        flash("Staff assigned to trek.")
        return redirect(url_for("admin.manage_treks"))
    return render_template("admin/assign_staff.html", trek=trek, approved_staff=approved_staff)


@admin_blueprint.route("/staff")
@login_required
@admin_only
def view_staff():
    search_term = request.args.get("search_term", "")
    query = User.query.filter_by(role="staff")
    if search_term:
        query = query.filter(User.full_name.ilike(f"%{search_term}%"))
    staff_list = query.all()
    return render_template("admin/staff.html", staff_list=staff_list, search_term=search_term)


@admin_blueprint.route("/staff/approve/<int:user_id>")
@login_required
@admin_only
def approve_staff(user_id):
    staff_member = User.query.get_or_404(user_id)
    staff_member.approval_status = "approved"
    db.session.commit()
    flash("Staff approved.")
    return redirect(url_for("admin.view_staff"))


@admin_blueprint.route("/staff/reject/<int:user_id>")
@login_required
@admin_only
def reject_staff(user_id):
    staff_member = User.query.get_or_404(user_id)
    staff_member.approval_status = "rejected"
    db.session.commit()
    flash("Staff rejected.")
    return redirect(url_for("admin.view_staff"))


@admin_blueprint.route("/users")
@login_required
@admin_only
def view_users():
    search_term = request.args.get("search_term", "")
    query = User.query.filter_by(role="trekker")
    if search_term:
        query = query.filter(User.full_name.ilike(f"%{search_term}%"))
    users_list = query.all()
    return render_template("admin/users.html", users_list=users_list, search_term=search_term)


@admin_blueprint.route("/bookings")
@login_required
@admin_only
def view_bookings():
    bookings = Booking.query.all()
    return render_template("admin/bookings.html", bookings=bookings)


@admin_blueprint.route("/blacklist/<int:user_id>")
@login_required
@admin_only
def toggle_blacklist(user_id):
    account = User.query.get_or_404(user_id)
    account.blacklist_status = not account.blacklist_status
    db.session.commit()
    flash("Blacklist status updated.")
    return redirect(request.referrer or url_for("admin.dashboard"))
