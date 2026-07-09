from flask import Flask, redirect, url_for
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from datetime import date
import os
from models import db, User, Trek

from routes.auth_routes import auth_blueprint
from routes.admin_routes import admin_blueprint
from routes.staff_routes import staff_blueprint
from routes.trekker_routes import trekker_blueprint

app = Flask(__name__)
app.config["SECRET_KEY"] = "trekking-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "trekking.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

os.makedirs(app.instance_path, exist_ok=True)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)
@login_manager.user_loader

def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(staff_blueprint)
app.register_blueprint(trekker_blueprint)
@app.route("/")

def home_page():
    return redirect(url_for("trekker.browse_treks"))

def create_seed_data():
    if User.query.filter_by(email="aditya@gmail.com").first() is None:
        admin_account = User(
            full_name="Aditya",
            email="aditya@gmail.com",
            password_hash=generate_password_hash("adi123"),
            phone_number="9999999999",
            role="admin",
            approval_status="approved",
            blacklist_status=False,
        )
        db.session.add(admin_account)

    if Trek.query.count() == 0:
        sample_treks = [
            Trek(
                trek_title="Kedarkantha Winter Trek",
                destination="Uttarakhand",
                difficulty_level="Moderate",
                duration_days=6,
                start_date=date(2026, 12, 20),
                end_date=date(2026, 12, 25),
                remaining_slots=15,
                current_status="Open",
                description="A beautiful snow trek through pine forests in Uttarakhand.",
            ),
            Trek(
                trek_title="Hampta Pass Crossing",
                destination="Himachal Pradesh",
                difficulty_level="Moderate",
                duration_days=5,
                start_date=date(2026, 8, 10),
                end_date=date(2026, 8, 15),
                remaining_slots=12,
                current_status="Open",
                description="A dramatic crossover trek from green valleys to a cold desert.",
            ),
            Trek(
                trek_title="Kudremukh Green Trail",
                destination="Karnataka",
                difficulty_level="Easy",
                duration_days=2,
                start_date=date(2026, 9, 5),
                end_date=date(2026, 9, 6),
                remaining_slots=20,
                current_status="Open",
                description="Rolling grasslands and thick forests in the Western Ghats.",
            ),
            Trek(
                trek_title="Kumara Parvatha Climb",
                destination="Karnataka",
                difficulty_level="Difficult",
                duration_days=2,
                start_date=date(2026, 10, 1),
                end_date=date(2026, 10, 2),
                remaining_slots=10,
                current_status="Open",
                description="One of the toughest treks in South India with steep climbs.",
            ),
            Trek(
                trek_title="Rajmachi Fort Trail",
                destination="Maharashtra",
                difficulty_level="Easy",
                duration_days=2,
                start_date=date(2026, 7, 20),
                end_date=date(2026, 7, 21),
                remaining_slots=25,
                current_status="Open",
                description="A monsoon favorite trek near Lonavala with fort ruins.",
            ),
            Trek(
                trek_title="Triund Ridge Walk",
                destination="Himachal Pradesh",
                difficulty_level="Easy",
                duration_days=2,
                start_date=date(2026, 11, 12),
                end_date=date(2026, 11, 13),
                remaining_slots=18,
                current_status="Open",
                description="A short scenic trek with views of the Dhauladhar range.",
            ),
        ]
        db.session.add_all(sample_treks)

    db.session.commit()


with app.app_context():
    db.create_all()
    create_seed_data()


if __name__ == "__main__":
    app.run(debug=True)
