from flask import Flask
from flask_cors import CORS
from flask import jsonify

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
        "profile_link": "https://github.com/otzhora"
    }
}


@app.route("/users")
def get_users():
    return jsonify(users)


@app.route("/contracts")
def get_contracts():
    return jsonify(contracts)
