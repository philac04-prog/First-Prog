from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os
load_dotenv()
app = Flask(__name__)
app.secret_key = "mysecretkey"
database_url = os.getenv("DATABASE_URL")

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
def login_required ():
    return "user" in session
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
def login_required():
    if "user" not in session:
        return False
    return True
@app.route("/", methods=["GET", "POST"])
def home():
    if not login_required():
        return redirect("/login")
    users = User.query.all()
    return render_template("index.html", users=users)
    if request.method == "POST":
        name = request.form["username"]
        if not name:
            flash("Ten Khong Duoc De Trong!")
        else:
            user = User(name=name)
            db.session.add(user)
            db.session.commit()
            flash("Da Them User!")
    users = User.query.all()
    return render_template("index.html", users=users)
@app.route("/delete/<int:user_id>")
def delete_user(user_id):
    if not login_required():
        return redirect("/login")
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect("/")
@app.route("/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if not login_required():
        return redirect("/login")
    user = User.query.get(user_id)
    if not user:
        return redirect("/")
    if request.method == "POST":
        new_name = request.form["username"]
        if new_name:
            user.name = new_name
            db.session.commit()
        return redirect("/")
    return render_template("edit.html", user=user)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user"] = user.username
            return redirect("/")
        else:
            flash("Sai Tài Khoản Hoặc Mật Khẩu")
    return render_template("login.html")
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")
@app.route("/register", methods=["GET", "POSt"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Đăng Ký Thành Công")
        return redirect("/login")
    return render_template("register.html")
if __name__ == "__main__":
    app.run(debug=False)
with app.app_context():
    db.create_all()