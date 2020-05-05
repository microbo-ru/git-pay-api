from flask import Flask, redirect, url_for
from flask_cors import CORS
from flask import jsonify, request
from flask_dance.contrib.github import make_github_blueprint, github


from requests import get
import os

import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
app.config["GITHUB_OAUTH_CLIENT_ID"] = os.environ.get("GITHUB_OAUTH_CLIENT_ID")
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.environ.get(
    "GITHUB_OAUTH_CLIENT_SECRET")
CORS(app, resources={r"/*": {"origins": "*"}})

github_bp = make_github_blueprint()
app.register_blueprint(github_bp, url_prefix="/login", redirect_to="/")

users = {}
all_pulls = []


def find_user_by_username(username):
    # TODO change this to db request
    found_user = False
    found_user_id = 0
    for id in users:
        if users[id]["username"] == username:
            found_user_id = id
            found_user = True
            break
    return (found_user, found_user_id)


def get_user_info_from_github(username=None):
    if username:
        resp = github.get(f"/users/{username}")
    else:
        resp = github.get(f"/user")

    if not resp.ok:
        return False, False, 0

    user_data = resp.json()
    username = user_data["login"]
    avatar_url = user_data["avatar_url"]
    user = {"username": username, "avatar_url": avatar_url}

    found_user, found_user_id = find_user_by_username(username)
    return True, found_user, found_user_id, user


@app.route("/github_login")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))

    ok, found_user, found_user_id, user = get_user_info_from_github()
    if not ok:
        return "There is problem with github"

    username = user["username"]
    avatar_url = user["avatar_url"]

    # TODO change this to insertion to db
    if not found_user:
        id = str(uuid.uuid4())
        users[id] = {
            "username": username,
            "avatar_url": avatar_url,
            "user_status": "user",  # this would be default but i think we should change this
            "assigned_pulls": []
        }
        return jsonify({"status": "new_user", "user": users[id]}
                       )
    # TODO change this to updating avatar_url in db
    if found_user:
        users[found_user_id]["avatar_url"] = avatar_url  # updating avatar url
        return jsonify({"status": "found_user", "user": users[found_user_id]})

    return jsonify({"status": "somthing went wrong"})


@app.route("/user")
def user():
    if not github.authorized:
        return redirect(url_for("github.login"))

    ok, found_user, found_user_id, user = get_user_info_from_github()
    username = user["username"]
    if not ok:
        return "There is problem with github"

    if not found_user:
        return f"There is no user in db with login: {username}"

    return jsonify({"status": "found_user", "user": users[found_user_id], "user_id": found_user_id})


@app.route("/users/<username>")
def user_by_username(username):
    if not github.authorized:
        return redirect(url_for("github.login"))

    ok, found_user, found_user_id, _ = get_user_info_from_github(username)
    if not ok:
        return "There is problem with github"

    if not found_user:
        return f"There is no user in db with login: {username}"

    return jsonify({"status": "found_user", "user": users[found_user_id], "user_id": found_user_id})


@app.route("/change_user_status")
def change_user_status():
    if not github.authorized:
        return redirect(url_for("github.login"))

    ok, found_user, found_user_id, user = get_user_info_from_github()
    username = user["username"]
    if not ok:
        return "There is problem with github"

    if not found_user:
        return f"There is no user in db with login: {username}"

    user_status = users[found_user_id]["user_status"]

    if user_status == "empl":
        users[found_user_id]["user_status"] = "user"
        del users[found_user_id]["marked_pulls"]
        users[found_user_id]["assigned_pulls"] = []
    else:
        users[found_user_id]["user_status"] = "empl"
        del users[found_user_id]["assigned_pulls"]
        users[found_user_id]["marked_pulls"] = []

    return f"You changed your status to {users[found_user_id]['user_status']}"


@app.route("/mark_pull", methods=["POST"])
def mark_pull():
    if not github.authorized:
        return redirect(url_for("github.login"))

    json = request.json
    pull_url = json["pull_url"]
    descr = json["descr"]
    price = json["price"]
    markee_id = json["markee_id"]

    # TODO change to db
    if not markee_id in users:
        return "You are not in our db"

    pull = {
        "url": pull_url,
        "markee_id": markee_id,
        "price": price,
        "descr": descr
    }
    all_pulls.append({"pull": pull, "assigned_users": []})
    users[markee_id]["marked_pulls"].append(pull)

    return "Added new pull to list"


@app.route("/assign_pull", methods=["POST"])
def assign_pull():
    if not github.authorized:
        return redirect(url_for("github.login"))

    json = request.json
    pull_url = json["pull_url"]
    assignee_id = json["assignee_id"]

    if not assignee_id in users or users[assignee_id]["user_status"] == "empl":
        return f"There is no user with id {assignee_id} or user with this id is empl"

    # TODO db
    found_pull = False
    found_pull_idx = -1
    for idx, pull in enumerate(all_pulls):
        if pull["pull"]["url"] == pull_url:
            found_pull = True
            found_pull_idx = idx
            break

    if not found_pull:
        return f"There is no pull with {pull_url}"

    all_pulls[found_pull_idx]["assigned_users"].append(assignee_id)
    users[assignee_id]["assigned_pulls"].append(
        all_pulls[found_pull_idx]["pull"])
    print(all_pulls)
    print(users)
    return "You are assigned to this pull"


@app.route("/pulls", methods=["POST", "GET"])
def get_pulls():
    if not github.authorized:
        return redirect(url_for("github.login"))

    if request.method == "POST":
        json = request.json
        pull_url = json["pull_url"]

        # TODO db
        for idx, pull in enumerate(all_pulls):
            if pull["pull"]["url"] == pull_url:
                return jsonify(pull["pull"])

        return f"There is no pull with url {pull_url}"

    if request.method == "GET":
        return jsonify(all_pulls)


@app.route("/user_pulls", methods=["POST"])
def get_user_pulls_from_github():
    if not github.authorized:
        return redirect(url_for("github.login"))

    json = request.json
    username = json["username"]

    resp = github.get(f"/search/issues?q=is:pr+author:{username}+is:open")
    if not resp.ok:
        return f"There is somthing wrong with github or username: {username} is invalid"

    json = resp.json()
    pulls = []
    for item in json["items"]:
        pulls.append({"url": item["url"], "title": item["title"]})
    return jsonify(pulls)
