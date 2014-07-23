from flask import *
from datetime import datetime, timedelta, date
import pickle
import os.path
from apscheduler.scheduler import Scheduler
from user import User

app = Flask(__name__)
app.secret_key = "Apfelkuchen"
users_list = []
if os.path.isfile("users"):
	users_list = pickle.load(open("users", "rb"))

sched = Scheduler()
sched.start()

@app.route("/")
def index():
	if is_logged_in():
		u = get_logged_in_user()
		time_left = u.get_time_left()
		return render_template("index.html", username=u.username, running=u.running, hours=str(time_left["hours"]).zfill(2), minutes=str(time_left["minutes"]).zfill(2), seconds=str(time_left["seconds"]).zfill(2))
	else:
		return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template("login.html")
	else:
		username = request.form.get("username")
		password = request.form.get("password")
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
		users_list.append(User(username, password))
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
		get_user(username).start()
		return "Session for " + username + " started"
	return "Invalid login"

@app.route("/stop", methods=["POST"])
def stop():
	username = request.form.get("username")
	password = request.form.get("password")
	if is_login_valid(username, password):
		get_user(username).stop()
		return "Session for " + username + " stopped"
	return "Invalid login"

@app.route("/reset", methods=["GET", "POST"])
def reset():
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")
		if username:
			if is_login_valid(username, password):
				get_user(username).reset_time_left()
				return "Session for " + username + " reset"
		return "Invalid login"
	else:
		if is_logged_in():
			get_logged_in_user().reset_time_left()
			return redirect(url_for("index"))
		else:
			return render_template("invalid_login.html")

@app.route("/time", methods=["POST"])
def time():
	username = request.form.get("username")
	u = get_user(username)
	if not u:
		return "Invalid username"
	u.ping()
	time_left = u.get_time_left()
	time_left_string = str(time_left["hours"]) + " " + str(time_left["minutes"]) + " " + str(time_left["seconds"])
	return time_left_string

@app.route("/config", methods=["GET", "POST"])
def config():
	if request.method == "GET":
		if is_logged_in():
			return render_template("config.html", username=get_logged_in_user().username, weekdays=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], times=get_logged_in_user().get_times())
		else:
			return render_template("invalid_login.html")
	else:
		if is_logged_in:
			u = get_logged_in_user()
			for i in range(7):
				u.times[i] = timedelta(hours=int(request.form[str(i) + " hours"]), minutes=int(request.form[str(i) + " minutes"]))
			save_users()
			return redirect(url_for("index"))
		else:
			return render_template("invalid_login.html")

@app.route("/settime", methods=["GET", "POST"])
def settime():
	if request.method == "GET":
		if is_logged_in():
			return render_template("settime.html", username=get_logged_in_user().username)
		else:
			return render_template("invalid_login.html")
	else:
		if is_logged_in():
			u = get_logged_in_user()
			hours = int(request.form["hours"])
			minutes = int(request.form["minutes"])
			u.today = timedelta(hours=hours, minutes=minutes)
			u.last_calc = datetime.now()
			return redirect(url_for("index"))
		else:
			return render_template("invalid_login.html")

def check_for_timeout(u):
	if datetime.now() - u.last_ping > timedelta(minutes=2):
		print("Session for " + u.username + " timed out")
		u.calc()
		u.running = False

def is_login_valid(username, password):
	if get_user(username) is None:
		return False
	else:
		return get_user(username).password == password

def is_logged_in():
	return "username" in session and not (get_logged_in_user() is None)

def get_logged_in_user():
	return get_user(session.get("username"))

def get_user(name):
	for u in users_list:
		if u.username == name:
			return u

def save_users():
  	pickle.dump(users_list, open("users", "wb"))

if __name__ == '__main__':
	app.run(debug=True)