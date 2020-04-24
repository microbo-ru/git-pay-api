from flask import Flask
from flask_cors import CORS
from flask import jsonify, request
from requests import get

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

contracts = {
    "123": {
        "name": "otzhora",
        "repos": [{"name": "image annotator", "url": "https://github.com/otzhora/face_annotator"},
                  {"name": "HackUniversity hac", "url": "https://github.com/otzhora/HackUniversity"}]
    },
    "34241": {
        "name": "fastai",
        "repos": [{"name": "fastai library", "url": "https://github.com/fastai/fastai"},
                  {"name": "fastai course", "url": "https://github.com/fastai/course-v4"}]
    }
}


users = {
    "otzhora": {
        "profile_link": "https://github.com/otzhora",
        "marked_repos": [{"name": "image annotator", "url": "https://github.com/otzhora/face_annotator"},
                         {"name": "HackUniversity hac", "url": "https://github.com/otzhora/HackUniversity"}]
    }
}


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
