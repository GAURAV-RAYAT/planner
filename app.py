from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone
from config import Config
from models import db, User, Task

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

scheduler = BackgroundScheduler()
scheduler.start()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



def check_deadlines():
    with app.app_context():
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)

        tasks = Task.query.filter(Task.deadline <= now, Task.notified == False).all()

        for task in tasks:
            user = User.query.get(task.user_id)

            msg = Message(
                subject="Deadline Reminder",
                sender=app.config["MAIL_USERNAME"],
                recipients=[user.email],
                body=f"Your deadline for '{task.title}' has arrived!"
            )

            mail.send(msg)
            task.notified = True
            db.session.commit()


scheduler.add_job(check_deadlines, "interval", minutes=1)


# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered. Please login.")
            return redirect(url_for("login"))

        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful!")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid credentials!")

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        title = request.form["title"]
        deadline = datetime.strptime(request.form["deadline"], "%Y-%m-%dT%H:%M")

        task = Task(title=title, deadline=deadline, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()

    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", tasks=tasks)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# Create database tables automatically on startup
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
