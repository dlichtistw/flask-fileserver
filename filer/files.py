# -*- coding: utf-8 -*-

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("files", __name__)

@bp.route("/")
def index():
    db = get_db()
    
    cur = db.execute(
        """
SELECT
    p."id",
    "title",
    "body",
    "created",
    "author_id",
    "username"
FROM "post" p
JOIN "user" u
    ON p."author_id" = u."id"
ORDER BY "created" DESC
;
        """
    )
    posts = cur.fetchall()
    cur.close()
    
    return render_template("files/index.html", posts=posts)

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = []
        
        if not title:
            error.append("Title must not be empty.")
        
        if error:
            flash("\n".join(error))
        else:
            db = get_db()
            db.execute(
                """INSERT INTO "post" ("title", "body", "author_id") VALUES (:title, :body, :aid);""",
                {"title": title, "body": body, "aid": g.user["id"]}
            ).close()
            db.commit()
            return redirect(url_for("blog.index"))
    return render_template("files/create.html")

def get_post(id, check_author=True):
    cur = get_db().execute(
        """
SELECT
    p."id",
    "title",
    "body",
    "created",
    "author_id",
    "udername"
FROM "post" p
JOIN "user" u
    ON p."author_id" = u."id"
WHERE p."id" = :aid
;
        """,
        {"aid": id}
    )
    post = cur.fetchone()
    cur.close()
    
    if post is None:
        abort(404, "There is no post with id {:d}".format(id))
    if check_author and post["author_id"] != g.user["id"]:
        abort(403, "You are not allowed to edit this post.")
    
    return post

@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)
    
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = []
        
        if not title:
            error.append("The title must not be empty.")
        
        if error:
            flash("\n".join(error))
        else:
            db = get_db()
            db.execute(
                """UPDATE "post" SET "title" = :title, "body" = :body WHERE "id" = :pid;""",
                {"title": title, "body": body, "pid": id}
            ).close()
            db.commit()
            return redirect(url_for("blog.index"))
    
    return render_template("blog/update.html", post=post)

@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("""DELETE FROM "post" WHERE "id" = :pid;""", {"pid": id}).close()
    db.commit()
    return redirect(url_for("blog.index"))
