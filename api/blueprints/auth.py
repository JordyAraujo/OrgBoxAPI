from flask import Blueprint, request, redirect, url_for, current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from ..models import db
from ..models.user import User
from flask_login import login_required, login_user, logout_user

auth = Blueprint("auth", __name__)

@auth.route("/signup", methods=["POST"])
def signup():
    username, password, full_name = (
        request.json.get("username").strip(),
        request.json.get("password").strip(),
        request.json.get("full_name").strip(),
    )

    if not username:
        return {"status": "Username required!"}
    if not password:
        return {"status": "Password required!"}
    if not full_name:
        return {"status": "Full name required!"}

    user = User.query.filter_by(username=username).first()

    if user:
        return {"status": "Username already exists!"}

    new_user = User(
        username=username,
        full_name=full_name,
        password=generate_password_hash(password, method="sha256")
    )

    db.session.add(new_user)
    db.session.commit()

    return {"status": "OK"}


@auth.route("/login", methods=["POST"])
def login():
    username, password = (
        request.json.get("username").strip(),
        request.json.get("password").strip()
    )

    if not username:
        return {"status": "Username required!"}
    if not password:
        return {"status": "Password required!"}

    user = User.query.filter_by(username=username).first()

    if not user:
        return {"status": "Username does not exist!"}

    if not check_password_hash(user.password, password):
        return {"status": "Wrong password!"}

    login_user(user)

    return {"status": "OK"}


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return {"status": "OK"}