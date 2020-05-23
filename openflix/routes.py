from . import socket, app
from flask import render_template, send_from_directory


@app.route("/")
def index():
    return render_template("index.html", debug=app.debug)

@app.route("/movie")
def movie():
    return render_template("movie.html", debug=app.debug)

@app.route("/show")
def show():
    return render_template("show.html", debug=app.debug)

@app.route("/js/<path:path>")
def send_js(path):
    return send_from_directory("js", path)

# @socket.on("connect", namespace="/test")
# def test_connect():
#     print("Client connected")


# @socket.on("disconnect", namespace="/test")
# def test_disconnect():
#     print("Client disconnected")
