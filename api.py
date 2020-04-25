from flask import Flask
from flask_cors import CORS
from flask import jsonify, request
from requests import get

import uuid

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

contracts = {
    "123": {
        "name": "otzhora",
        "repos": [{"name": "image annotator", "url": "https://github.com/otzhora/face_annotator", "description": ""},
                  {"name": "HackUniversity hac", "url": "https://github.com/otzhora/HackUniversity", "description": "", "premium": True}]
    },
    "34241": {
        "name": "fastai",
        "repos": [{"name": "fastai library", "url": "https://github.com/fastai/fastai", "description": "The fastai deep learning library, plus lessons and tutorials", "verified": True},
                  {"name": "fastai course", "url": "https://github.com/fastai/course-v4", "description": "Pre-release of v4 of course.fast.ai", "verified": True, "premium": True}]
    }
}


users = {
    "otzhora": {
        "profile_link": "https://github.com/otzhora",
        "marked_repos": [{"name": "image annotator", "url": "https://github.com/otzhora/face_annotator"},
                         {"name": "HackUniversity hac", "url": "https://github.com/otzhora/HackUniversity"}],
        "status": "user",
        "marked_pulls": []
    },
    "hoopoe": {
        "profile_link": "https://github.com/hoopoe",
        "marked_repos": [{"name": "gpugpeg", "url": "https://github.com/hoopoe/gpujpeg"}],
        "status": "empl",
        "marked_pulls": []
    }
}


pulls = []


@app.route("/pulls")
def get_pulls():
    return jsonify(pulls)


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start


@app.route("/get_marked_pulls", methods=["POST"])
def get_marked_pulls():
    username = request.json["username"]

    pulls = []
    for pull in users[username]["marked_pulls"]:
        pulls.append(pull)

        html_url = pull["html_url"]
        username = html_url[find_nth(
            html_url, "/", 3)+1:find_nth(html_url, "/", 4)]
        reponame = html_url[find_nth(
            html_url, "/", 4)+1:find_nth(html_url, "/", 5)]
        pull_number = html_url[find_nth(
            html_url, "/", 6) + 1:]

        res = get(
            f"https://api.github.com/repos/{username}/{reponame}/pulls/{pull_number}")
        pulls[-1]["extra"] = res.text
    return jsonify(pulls)


@app.route("/new_pull", methods=["POST"])
def new_pull():
    html_url = request.json["html_url"]
    taskDescription = request.json["taskDescription"]
    price = request.json["price"]
    username = request.json["username"]

    pulls.append(
        {"html_url": html_url, "taskDescription": taskDescription, "price": price, "username": username})
    users[username]["marked_pulls"].append(
        {"html_url": html_url, "taskDescription": taskDescription, "price": price, "username": username})
    return "OK"


@app.route("/users")
def get_users():
    return jsonify(users)


@app.route("/contracts")
def get_contracts():
    return jsonify(contracts)


@app.route("/pulls", methods=['POST'])
def get_prs():
    author = request.json['author']
    res = get(
        f"https://api.github.com/search/issues?q=is:pr+author:{author}+is:open").text
    return jsonify(res)


@app.route("/repos", methods=['POST'])
def get_repos():
    username = request.json['username']
    res = get(
        f"https://api.github.com/users/{username}/repos").text
    return jsonify(res)


@app.route("/marked_repos", methods=['POST'])
def get_marked_repos():
    username = request.json['username']

    if not username in users:
        return jsonify([])
    res = []
    for repo in users[username]['marked_repos']:

        reponame = repo['url'][repo['url'].rfind("/")+1:]
        buf = get(
            f"https://api.github.com/repos/{username}/{reponame}").text
        res.append(buf)

    return jsonify(res)


@app.route("/mark_repo", methods=['POST'])
def mark_repo():
    username = request.json['username']
    repo_name = request.json['repo_name']
    repo_url = request.json['repo_url']

    users[username]['marked_repos'].append(
        {"name": repo_name, "url": repo_url})

    contracts[str(uuid.uuid4())] = {
        "name": username, "repos": {"name": repo_name, "url": repo_url}
    }

    return "OK"
