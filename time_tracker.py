from flask import *
from datetime import datetime, timedelta, date
import pickle
import os.path

app = Flask(__name__)
app.secret_key = "Apfelkuchen"
users_list = []
if os.path.isfile("users.txt"):
	with open("users.txt", "rb") as handle:
		users_list = pickle.loads(handle.read())

@app.route("/")
def index():
	if is_logged_in():
		user = get_logged_in_user()
		refresh_time_left(user["username"])
		time_left = get_time_left(user["username"])
		return render_template("index.html", username=user["username"], running=user["running"], hours=str(time_left["hours"]).zfill(2), minutes=str(time_left["minutes"]).zfill(2), seconds=str(time_left["seconds"]).zfill(2))
	else:
		return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template("login.html")
	else:
		username = request.form.get("username")
		password = request.form.get("password")
		user = get_user(username)
		if is_login_valid(username, password):
			session["username"] = username
			return redirect(url_for("index"))
		else:
			return render_template("invalid_login.html")

@app.route("/logout")
def logout():
	session.pop("username", None)
	return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "GET":
		return render_template("register.html")
	else:
		username = request.form.get("username")
		password = request.form.get("password")
		users_list.append({"username": username, "password": password, "times": [timedelta(minutes=10) for i in range(7)], "today": timedelta(minutes=10), "running": False, "last_request": datetime.now()})
		save_users()
		return render_template("complete_registration.html", new_user=username)

@app.route("/users")
def users():
	return str(users_list)

@app.route("/start", methods=["POST"])
def start():
	username = request.form.get("username")
	password = request.form.get("password")
	if is_login_valid(username, password):
		user = get_user(username)
		if not user["last_request"].date() == date.today():
			reset_time_left(username)
		user["last_request"] = datetime.now()
		user["running"] = True
		return "Session for " + username + " started"
	return "Invalid login"

@app.route("/stop", methods=["POST"])
def stop():
	username = request.form.get("username")
	password = request.form.get("password")
	if is_login_valid(username, password):
		user = get_user(username)
		refresh_time_left(username)
		user["last_request"] = datetime.now()
		user["running"] = False
		return "Session for " + username + " stopped"
	return "Invalid login"

@app.route("/reset", methods=["GET", "POST"])
def reset():
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")
		if username:
			if is_login_valid(username, password):
				reset_time_left(username)
				get_user(username)["last_request"] = datetime.now()
				return "Session for " + username + " reset"
		return "Invalid login"
	else:
		if is_logged_in():
			reset_time_left(get_logged_in_user()["username"])
			get_logged_in_user()["last_request"] = datetime.now()
			return redirect(url_for("index"))
		else:
			return render_template("invalid_login.html")

@app.route("/time", methods=["POST"])
def time():
	username = request.form.get("username")
	user = get_user(username)
	if not user:
		return
	refresh_time_left(username)
	return jsonify(**get_time_left(username))

def refresh_time_left(username):
	user = get_user(username)
	if user["running"]:
		last_request = user["last_request"]
		now = datetime.now()
		delta = now - last_request

		user["today"] -= delta

		if user["today"] < timedelta(0):
			user["today"] = timedelta(0)

		if not last_request.date() == now.date():
				reset_time_left(username)

		user["last_request"] = now

def get_time_left(username):
	user = get_user(username)
	total_seconds = user["today"].seconds
	hours = total_seconds // 3600
	minutes = (total_seconds % 3600) // 60
	seconds = total_seconds % 60
	return {"hours": hours, "minutes": minutes, "seconds": seconds}

def reset_time_left(username):
	user = get_user(username)
	user["today"] = +user["times"][datetime.now().weekday()]

def is_login_valid(username, password):
	if get_user(username) is None:
		return False
	else:
		return get_user(username)["password"] == password

def is_logged_in():
	return "username" in session and not (get_logged_in_user() is None)

def get_logged_in_user():
	return get_user(session.get("username"))

def get_user(name):
	for user in users_list:
		if user["username"] == name:
			return user

def save_users():
	with open('users.txt', 'wb') as handle:
  		pickle.dump(users_list, handle)

if __name__ == '__main__':
	app.run(debug=True)

import atexit
atexit.register(save_users)