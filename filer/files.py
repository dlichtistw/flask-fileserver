# -*- coding: utf-8 -*-

from filer.db import get_db
from os import scandir, stat
from os.path import join as join_path, isdir, basename, getsize
from werkzeug.utils import secure_filename
from re import search
from flask import current_app, Blueprint, request, flash, render_template, redirect, url_for
from filer.auth import user_required

bp = Blueprint("files", __name__)

def get_files(id):
    cur = get_db().cursor()
    files = [BlogFile(
        join_path(current_app.config["UPLOAD_FOLDER"], row["filename"]),
        counter=row["counter"],
        id=row["id"]
    ) for row in cur.execute(
        """SELECT "id", "filename", "counter" FROM "file" WHERE "post_id" = :pid;""",
        {"pid": id}
    )]
    cur.close()
    return files

def init_app(app):
    app.config.from_mapping(
        UPLOAD_FOLDER=join_path(app.instance_path, "files"),
        UPLOAD_EXTENSIONS=set([
            "mp3", "m3u",
            "pdf"
        ])
    )

def allowed_filename(filename):
    m = search(r"\.(?P<ext>[^.]+)$", filename)
    return m and m["ext"].lower() in current_app.config["UPLOAD_EXTENSIONS"]

@bp.route("/files")
@user_required("@admin")
def index():
    uf = current_app.config["UPLOAD_FOLDER"]
    try:
        files = scandir(uf)
    except FileNotFoundError:
        flash("Unable to read upload folder '{:s}'.".format(uf))
        files = []
    
    return render_template("files/index.html", files=files)

@bp.route("/files/upload", methods=("POST",))
@user_required("@admin")
def upload():
    if "file" not in request.files:
        flash("File is missing.")
    file = request.files["file"]
    if file.filename == "":
        flash("File is missing.")
    if file and allowed_filename(file.filename):
        filename = secure_filename(file.filename)
        filepath = join_path(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
    else:
        flash("Bad file or filename '{:s}'.".format(file.filename))

    return redirect(url_for("files.index"))

class BlogFile:
    
    def __init__(self, path, counter=None, id=None):
        self._path = path
        self._id = id
        self._counter = counter

    @property
    def name(self):
        return basename(self._path)
    
    @property
    def id(self):
        return self._id
    
    @property
    def counter(self):
        return self._counter
    
    @property
    def size(self):
        return getsize(self._path)
    