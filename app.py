import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_socketio import SocketIO, join_room, leave_room, send
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from PIL import Image
import base64
import io
import datetime

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog

from helpers import apology, login_required

# Configure application
app = Flask(__name__)
app.config["SECRET_KEY"] = "vnkdjnfjknfl1232#"
socketio = SocketIO(app)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///dance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    if request.method == "GET":
        user_id = session["user_id"]
        username = db.execute("SELECT username FROM users WHERE id = ?", user_id)

        if len(username) > 0:
            username_value = username[0]["username"]

        dance_videos = db.execute("SELECT username, video_link, title FROM dances")
        print(dance_videos)


        return render_template("index.html", videos=dance_videos)


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        name = request.form.get("name")
        position = request.form.get("position")
        experience = request.form.get("experience")
        description = request.form.get("description")
        dance_styles = request.form.get("dance_styles")

        # Ensure position was submitted
        if not position:
            return apology("must provide position", 400)

        # Ensure experience was submitted
        if not experience:
            return apology("must provide password", 400)

        # Ensure dance_styles was submitted
        if not description:
            return apology("must enter description", 400)

        if not dance_styles:
            return apology("must enter dance_styles", 400)

        user_id = session["user_id"]

        db.execute(
            "UPDATE users SET name = ?, position = ?, experience = ?, description = ?, dance_styles = ? WHERE id = ?",
            name,
            position,
            experience,
            description,
            dance_styles,
            user_id,
        )

        # Redirect user to home page
        return render_template(
            "profile2.html",
            name=name,
            position=position,
            experience=experience,
            description=description,
            dance_styles=dance_styles,
        )

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("edit.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    # Get profile data from users table and pass it into profile
    if request.method == "GET":
        user_id = session["user_id"]
        username = db.execute("SELECT username FROM users WHERE id = ?", user_id)
        username_value = username[0]["username"]
        print("Username:", username_value)

        profile_info = db.execute(
            "SELECT name, position, experience, description, dance_styles FROM users WHERE id = ?",
            user_id,
        )
        name = profile_info[0]["name"]
        position = profile_info[0]["position"]
        experience = profile_info[0]["experience"]
        description = profile_info[0]["description"]
        dance_styles = profile_info[0]["dance_styles"]

        your_videos = db.execute(
            "SELECT video_link FROM dances WHERE username = ?", username_value
        )
        print(your_videos)


        return render_template(
            "profile2.html",
            name=name,
            position=position,
            experience=experience,
            description=description,
            dance_styles=dance_styles,
            videos=your_videos,
        )


@app.route("/collab", methods=["GET", "POST"])
@login_required
def collab():
    if request.method == "GET":
        user_id = session["user_id"]
        following = db.execute(
            "SELECT follows_name FROM follows WHERE user_id = ?", user_id
        )
        names = [row["follows_name"] for row in following]
        print(names)
        return render_template("collab.html", names=names)
    if request.method == "POST":
        flash("Sent!")
        user_id = session["user_id"]
        sender_name = request.form.get("firstname")
        print(sender_name)
        receiver_name = request.form.get("receiver")
        print(receiver_name)
        content = request.form.get("subject")
        print(content)
        db.execute(
            "INSERT INTO messages (sender, receiver, content) VALUES(?, ?, ?)",
            sender_name,
            receiver_name,
            content,
        )

        return redirect("/collab")


@app.route("/messages", methods=["GET", "POST"])
@login_required
def messages():
    if request.method == "GET":
        user_id = session["user_id"]
        username = db.execute("SELECT name FROM users WHERE id = ?", user_id)
        username_value = username[0]["name"]
        messages = db.execute(
            "SELECT sender, receiver, content FROM messages WHERE sender = ? OR receiver = ?",
            username_value,
            username_value,
        )
        return render_template("messages.html", messages=messages)
    return render_template("messages.html")


@app.route("/share", methods=["GET", "POST"])
@login_required
def share():
    """Allow users to share videos"""
    # Upload Videos
    if request.method == "POST":
        user_id = session["user_id"]
        youtube_link = request.form.get("link")
        title = request.form.get("title")
        genre = request.form.get("genre")
        if not genre:
            return apology("must provide genre", 403)

        username = db.execute("SELECT username FROM users WHERE id = ?", user_id)
        username_value = username[0]["username"]

        db.execute(
            "INSERT INTO dances (username, video_link, genre, title) VALUES (?, ?, ?, ?)",
            username_value,
            youtube_link,
            genre,
            title
        )
        return redirect("/profile")
    else:
        return render_template("share.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to edit profile
        profile_proof = db.execute(
            "SELECT profile FROM users WHERE username = ?", request.form.get("username")
        )
        if profile_proof[0]["profile"] == 0:
            db.execute(
                "UPDATE users SET profile = 1 WHERE username = ?",
                request.form.get("username"),
            )
            return redirect("/edit_profile")

        else:
            # Redirect user to home page
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/feed", methods=["GET", "POST"])
@login_required
def feed():
    if request.method == "GET":
        return render_template("genres.html")

    else:
        user_id = session["user_id"]
        genre = request.form.get("genre")

        videos = db.execute(
            "SELECT video_link, username, title FROM dances WHERE genre = ?", genre
        )

        return render_template("feed.html", videos=videos, genre=genre)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        for row in rows:
            if row["username"] == username:
                return apology("username already exists", 400)

        # Ensure password was submitted
        if not password:
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not confirmation:
            return apology("must confirm password", 400)

        # Ensure same password was submitted
        elif not password == confirmation:
            return apology("passwords must match", 400)

        # Insert info into database
        if username and password:
            db.execute(
                "Insert INTO users (username, hash) VALUES (?,?)",
                username,
                generate_password_hash(password),
            )

        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/playlist", methods=["GET", "POST"])
@login_required
def playlist():
    if request.method == "GET":
        return render_template("playlists.html")


@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    if request.method == "POST":
        flash("Removed!")
        user_id = session["user_id"]
        video_link = request.form.get("video_link")
        genre = request.form.get("genre")
        db.execute(
            "DELETE FROM playlists WHERE video_link = ? AND genre = ?",
            video_link,
            genre,
        )
        playlist_videos = db.execute(
            "SELECT video_link FROM playlists WHERE user_id = ? AND genre = ?",
            user_id,
            genre,
        )

        return render_template("playlist.html", genre=genre, videos=playlist_videos)


@app.route("/build", methods=["GET", "POST"])
@login_required
def build():
    if request.method == "GET":
        # Use request.args.get() for GET request parameters
        user_id = session["user_id"]
        video_index = request.args.get("video_index")
        video_link = request.args.get("video_link")
        print("Video Index:", video_index)
        print("Video Link:", video_link)
        db.execute(
            "INSERT INTO playlists (video_link, user_id) VALUES (?, ?)",
            video_link,
            user_id,
        )

        return render_template("addvideo.html", video_link=video_link)

    if request.method == "POST":
        user_id = session["user_id"]
        video_link = request.form.get("video_link")
        print(video_link)
        genre = request.form.get("genre")
        db.execute(
            "UPDATE playlists SET genre = ? WHERE user_id = ? AND video_link = ?",
            genre,
            user_id,
            video_link,
        )
        playlist_videos = db.execute(
            "SELECT video_link FROM playlists WHERE user_id = ? AND genre = ?",
            user_id,
            genre,
        )
        return render_template("playlist.html", genre=genre, videos=playlist_videos)


@app.route("/follow", methods=["GET", "POST"])
@login_required
def follow():
    if request.method == "POST":
        user_id = session.get("user_id")

        username_to_follow = request.form.get("name")

        is_following = (
            db.execute(
                "SELECT COUNT(*) FROM follows WHERE user_id = ? AND follows_name = ?",
                user_id,
                username_to_follow,
            )[0]["COUNT(*)"]
            > 0
        )

        if not is_following:
            db.execute(
                "INSERT INTO follows (user_id, follows_name) VALUES (?, ?)",
                user_id,
                username_to_follow,
            )

        profile_info = db.execute(
            "SELECT position, experience, description, dance_styles FROM users WHERE name = ?",
            username_to_follow,
        )

        your_videos = db.execute(
            "SELECT video_link FROM dances WHERE username = ?", username_to_follow
        )


        position = profile_info[0]["position"]
        experience = profile_info[0]["experience"]
        description = profile_info[0]["description"]
        dance_styles = profile_info[0]["dance_styles"]

        return render_template(
            "profile.html",
            is_following=True,
            name=username_to_follow,
            position=position,
            experience=experience,
            description=description,
            dance_styles=dance_styles,
            videos = your_videos,
        )


@app.route("/<artist_username>", methods=["GET", "POST"])
@login_required
def artist_profile(artist_username):
    if request.method == "POST":
        user_id = session.get("user_id")

        if user_id is None:
            return jsonify({"error": "User not logged in"}), 403

        username = db.execute("SELECT name FROM users WHERE id = ?", user_id)
        username_value = username[0]["name"]

        artist_username = request.form.get("username")
        print(artist_username)

        # Use the 'artist_username' variable directly
        profile_info = db.execute(
            "SELECT name, position, experience, description, dance_styles FROM users WHERE username = ?",
            artist_username,
        )


        is_following = False  # Assume initially that the user is not following

        follows = db.execute("SELECT follows_name FROM follows WHERE user_id = ?", user_id)

        for person in follows:
            print(person["follows_name"])
            if person["follows_name"] == artist_username:
                is_following = True
                break  # Break out of the loop once a match is found

        print(is_following)


        your_videos = db.execute(
            "SELECT video_link FROM dances WHERE username = ?", artist_username
        )

        name = profile_info[0]["name"]
        position = profile_info[0]["position"]
        experience = profile_info[0]["experience"]
        description = profile_info[0]["description"]
        dance_styles = profile_info[0]["dance_styles"]
        return render_template(
            "profile.html",
            is_following=is_following,
            name=name,
            position=position,
            experience=experience,
            description=description,
            dance_styles=dance_styles,
            videos=your_videos,
        )
