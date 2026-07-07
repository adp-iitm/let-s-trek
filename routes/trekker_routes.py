from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Trek, Booking

trekker_blueprint = Blueprint("trekker", __name__)

def trekker_only(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "trekker":
            flash("Please log in as a trekker to continue.")
            return redirect(url_for("auth.login"))
        return view_function(*args, **kwargs)
    return wrapper

@trekker_blueprint.route("/treks")
def browse_treks():
    search_term = request.args.get("search_term", "")
    location_filter = request.args.get("location_filter", "")
    difficulty_filter = request.args.get("difficulty_filter", "")

    query = Trek.query.filter_by(current_status="Open")

    if search_term:
        query = query.filter(Trek.trek_title.ilike(f"%{search_term}%"))
    if location_filter:
        query = query.filter(Trek.destination.ilike(f"%{location_filter}%"))
    if difficulty_filter:
        query = query.filter_by(difficulty_level=difficulty_filter)

    treks = query.all()
    return render_template(
        "trekker/browse.html",
        treks=treks,
        search_term=search_term,
        location_filter=location_filter,
        difficulty_filter=difficulty_filter,
    )


@trekker_blueprint.route("/treks/<int:trek_id>/book", methods=["POST"])
@login_required
@trekker_only
def book_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    if trek.current_status != "Open":
        flash("This trek is not open for booking.")
        return redirect(url_for("trekker.browse_treks"))

    if trek.remaining_slots <= 0:
        flash("No slots remaining for this trek.")
        return redirect(url_for("trekker.browse_treks"))

    new_booking = Booking(trekker_id=current_user.id, trek_id=trek.id, booking_status="Confirmed")
    trek.remaining_slots -= 1
    db.session.add(new_booking)
    db.session.commit()
    flash("Trek booked successfully.")
    return redirect(url_for("trekker.my_bookings"))


@trekker_blueprint.route("/my-bookings")
@login_required
@trekker_only
def my_bookings():
    bookings = Booking.query.filter_by(trekker_id=current_user.id).all()
    return render_template("trekker/my_bookings.html", bookings=bookings)


@trekker_blueprint.route("/profile", methods=["GET", "POST"])
@login_required
@trekker_only
def edit_profile():
    if request.method == "POST":
        current_user.full_name = request.form.get("full_name")
        current_user.phone_number = request.form.get("phone_number")
        db.session.commit()
        flash("Profile updated.")
        return redirect(url_for("trekker.edit_profile"))
    return render_template("trekker/profile.html")
