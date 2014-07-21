from flask import *
from datetime import datetime
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
		return render_template("index.html", username=user["username"], hours=str(user["today"][0]).zfill(2), minutes=str(user["today"][1]).zfill(2), seconds=str(user["today"][2]).zfill(2))
	else:
		return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template("login.html")
	else:
		username = request.form["username"]
		password = request.form["password"]
		user = get_user(username)
		if user and user["password"] == password:
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
		username = request.form["username"]
		password = request.form["password"]
		users_list.append({"username": username, "password": password, "times": [(1, 0) for i in range(7)], "today": [1, 0, 0], "running": False, "last_request": datetime.now()})
		with open('users.txt', 'wb') as handle:
  			pickle.dump(users_list, handle)
		return render_template("complete_registration.html", new_user=username)

@app.route("/users")
def users():
	return jsonify(users=users_list)

def is_logged_in():
	return "username" in session

def get_logged_in_user():
	return get_user(session.get("username"))

def get_user(name):
	for user in users_list:
		if user["username"] == name:
			return user

if __name__ == '__main__':
	app.run(debug=True)