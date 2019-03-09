# -*- coding: utf-8 -*-

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from functools import wraps

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = []
        
        if not username:
            error.append("Username must not be empty")
        if not password:
            error.append("Password must not be empty")
        
        cur = db.execute(
            """SELECT "id" FROM "user" WHERE "username" = :user;""",
            {"user": username}
        )
        if cur.fetchone() is not None:
            error.append("User {:s} is already registered.".format(username))
        cur.close()
        
        if error:
            flash("\n".join(error))
        else:
            db.execute(
                """INSERT INTO "user" ("username", "password") VALUES (:user, :pass);""",
                {"user": username, "pass": generate_password_hash(password)}
            ).close()
            db.commit()
            return redirect(url_for("auth.login"))
    
    return render_template("auth/register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = []
        
        cur = db.execute(
            """SELECT "id", "password" FROM "user" WHERE "username" = :user;""",
            {"user": username}
        )
        user = cur.fetchone()
        cur.close()
        
        if user is None:
            error.append("User '{:s}' does not exist.".format(username))
        elif not check_password_hash(user["password"], password):
            error.append("Bad password for user '{:s}'.".format(username))
        else:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
        
        flash("\n".join(error))
    
    return render_template("auth/login.html")

@bp.before_app_request
def load_authed_user():
    user_id = session.get("user_id")
    
    if user_id is None:
        g.user = None
    else:
        cur = get_db().execute(
            """SELECT "id", "username" FROM "user" WHERE "id" = :uid;""",
            {"uid": user_id}
        )
        g.user = cur.fetchone()
        cur.close()

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view
