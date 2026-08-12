import os
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

BASE_PREFIX = "/api/private/v1"
TOKEN = "mock-token-123"

users = [
    {
        "id": 1,
        "username": "admin",
        "password": "123456",
        "state": True,
    }
]


@app.route(f"{BASE_PREFIX}/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    if not payload:
        payload = request.form.to_dict() or {}

    username = payload.get("username")
    password = payload.get("password")

    if username == "admin" and password == "123456":
        return jsonify({
            "meg": "登陆成功",
            "data": {
                "token": TOKEN,
                "id": 1,
                "username": username,
            }
        })

    return jsonify({
        "meg": "用户名或密码错误",
        "data": {}
    }), 401


@app.route(f"{BASE_PREFIX}/users", methods=["GET"])
def get_users():
    auth = request.headers.get("Authorization")
    if auth != TOKEN:
        return jsonify({
            "meg": "无效token",
            "data": {}
        }), 401

    return jsonify({
        "meg": "获取管理员列表成功",
        "data": {
            "users": users
        }
    })


@app.route(f"{BASE_PREFIX}/users", methods=["POST"])
def create_user():
    auth = request.headers.get("Authorization")
    if auth != TOKEN:
        return jsonify({
            "meg": "无效token",
            "data": {}
        }), 401

    payload = request.get_json(silent=True) or {}
    if not payload:
        payload = request.form.to_dict() or {}
    username = payload.get("username")
    password = payload.get("password")

    if not username or not password:
        return jsonify({
            "meg": "参数错误",
            "data": {}
        }), 400

    new_id = max([user["id"] for user in users]) + 1
    new_user = {
        "id": new_id,
        "username": username,
        "password": password,
        "state": True,
    }
    users.append(new_user)

    return jsonify({
        "meg": "创建成功",
        "data": {
            "id": new_id,
            "username": username,
            "password": password,
        }
    })


@app.route(f"{BASE_PREFIX}/users/<int:user_id>/state/<state>", methods=["PUT"])
def update_user_state(user_id, state):
    auth = request.headers.get("Authorization")
    if auth != TOKEN:
        return jsonify({
            "meg": "无效token",
            "data": {}
        }), 401

    found = False
    for user in users:
        if user["id"] == user_id:
            user["state"] = True if state == "true" else False
            found = True
            break

    if not found:
        return jsonify({
            "meg": "用户不存在",
            "data": {}
        }), 404

    return jsonify({
        "meg": "设置状态成功",
        "data": {
            "id": user_id,
            "state": state
        }
    })


@app.route(f"{BASE_PREFIX}/upload", methods=["POST"])
def upload_file():
    auth = request.headers.get("Authorization")
    if auth != TOKEN:
        return jsonify({
            "meg": "无效token",
            "data": {}
        }), 401

    if "file" not in request.files:
        return jsonify({
            "meg": "文件未上传",
            "data": {}
        }), 400

    file_obj = request.files["file"]
    upload_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file_obj.filename)
    file_obj.save(file_path)

    return jsonify({
        "meg": "上传成功",
        "data": {
            "url": f"/uploads/{file_obj.filename}",
            "filename": file_obj.filename,
            "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=False)
