from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Trek, Booking

staff_blueprint = Blueprint("staff", __name__, url_prefix="/staff")
def staff_only(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "staff":
            flash("Staff access required.")
            return redirect(url_for("auth.login"))
        if current_user.approval_status != "approved" or current_user.blacklist_status:
            flash("Your account cannot access the staff dashboard.")
            return redirect(url_for("auth.login"))
        return view_function(*args, **kwargs)
    return wrapper

@staff_blueprint.route("/dashboard")
@login_required
@staff_only
def dashboard():
    assigned_treks = Trek.query.filter_by(guide_id=current_user.id).all()
    return render_template("staff/dashboard.html", assigned_treks=assigned_treks)


@staff_blueprint.route("/trek/<int:trek_id>")
@login_required
@staff_only
def trek_detail(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.guide_id != current_user.id:
        flash("You are not assigned to this trek.")
        return redirect(url_for("staff.dashboard"))
    participants = Booking.query.filter_by(trek_id=trek.id, booking_status="Confirmed").all()
    return render_template("staff/trek_detail.html", trek=trek, participants=participants)


@staff_blueprint.route("/trek/<int:trek_id>/update_slots", methods=["POST"])
@login_required
@staff_only
def update_slots(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.guide_id != current_user.id:
        flash("You are not assigned to this trek.")
        return redirect(url_for("staff.dashboard"))
    trek.remaining_slots = int(request.form.get("remaining_slots"))
    db.session.commit()
    flash("Slots updated.")
    return redirect(url_for("staff.trek_detail", trek_id=trek.id))


@staff_blueprint.route("/trek/<int:trek_id>/set_status/<string:new_status>")
@login_required
@staff_only
def set_status(trek_id, new_status):
    trek = Trek.query.get_or_404(trek_id)
    if trek.guide_id != current_user.id:
        flash("You are not assigned to this trek.")
        return redirect(url_for("staff.dashboard"))
    trek.current_status = new_status
    db.session.commit()
    flash(f"Trek marked as {new_status}.")
    return redirect(url_for("staff.trek_detail", trek_id=trek.id))
