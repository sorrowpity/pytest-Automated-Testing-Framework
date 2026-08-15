# -*- coding: utf-8 -*-
"""电商 Mock 后端（Flask）。

业务模块：
- 认证      POST /login（管理员 + 买家双角色）
- 商品      GET /goods、GET /goods/:id（公开）；POST/PUT/DELETE /goods（管理员）
- 分类      GET /categories（公开）
- 购物车    POST/GET/PUT/DELETE /cart（买家）
- 订单      POST/GET/PUT /orders（买家，含库存扣减/回滚、支付幂等、越权校验）
- 用户管理  GET/POST/PUT /users（管理员）
- 上传      POST /upload

统一响应格式：{"meg": "...", "data": {...}}
"""
import os
import time
from datetime import datetime

from flask import Flask, request, jsonify

from mock_database import (
    execute,
    query_one,
    query_all,
    init_db,
    _is_mysql,
)

app = Flask(__name__)

BASE_PREFIX = "/api/private/v1"


# ==================== 通用工具 ====================

def _payload():
    p = request.get_json(silent=True)
    if not p:
        p = request.form.to_dict() or {}
    return p


def _ok(meg, data=None):
    return jsonify({"meg": meg, "data": data or {}})


def _err(meg, code=400):
    return jsonify({"meg": meg, "data": {}}), code


def _rows(rows):
    return [dict(r) for r in rows]


def _auth_info(auth):
    """解析 Authorization 头，返回 ("admin", id) / ("buyer", id) / None。"""
    if not auth:
        return None
    if auth.startswith("admin-token-"):
        try:
            return "admin", int(auth.split("-")[-1])
        except ValueError:
            return None
    if auth.startswith("token-"):
        try:
            return "buyer", int(auth.split("-")[-1])
        except ValueError:
            return None
    return None


def _admin_id(auth):
    info = _auth_info(auth)
    return info[1] if info and info[0] == "admin" else None


def _buyer_id(auth):
    info = _auth_info(auth)
    return info[1] if info and info[0] == "buyer" else None


# ==================== 认证 ====================

@app.route(f"{BASE_PREFIX}/login", methods=["POST"])
def login():
    payload = _payload()
    username = payload.get("username")
    password = payload.get("password")

    # 先查管理员
    mgr = query_one(
        "SELECT * FROM sp_manager WHERE mg_name = ? AND mg_pwd = ?", (username, password)
    )
    if mgr:
        return _ok("登录成功", {
            "token": f"admin-token-{mgr['id']}",
            "id": mgr["id"],
            "username": mgr["mg_name"],
            "role": "admin",
        })

    # 再查买家
    user = query_one(
        "SELECT * FROM sp_user WHERE username = ? AND password = ? AND state = 1",
        (username, password),
    )
    if user:
        return _ok("登录成功", {
            "token": f"token-{user['id']}",
            "id": user["id"],
            "username": user["username"],
            "role": "buyer",
        })

    return _err("用户名或密码错误", 401)


# ==================== 商品 ====================

@app.route(f"{BASE_PREFIX}/goods", methods=["GET"])
def goods_list():
    query = request.args.get("query", "")
    pagenum = int(request.args.get("pagenum", 1))
    pagesize = int(request.args.get("pagesize", 10))
    offset = (pagenum - 1) * pagesize

    total = query_one(
        "SELECT COUNT(*) AS c FROM sp_goods WHERE is_del = 0 AND goods_name LIKE ?",
        (f"%{query}%",),
    )["c"]
    goods = query_all(
        "SELECT * FROM sp_goods WHERE is_del = 0 AND goods_name LIKE ? ORDER BY id LIMIT ? OFFSET ?",
        (f"%{query}%", pagesize, offset),
    )
    return _ok("获取商品列表成功", {"goods": _rows(goods), "total": total})


@app.route(f"{BASE_PREFIX}/goods/<int:goods_id>", methods=["GET"])
def goods_detail(goods_id):
    goods = query_one("SELECT * FROM sp_goods WHERE id = ? AND is_del = 0", (goods_id,))
    if not goods:
        return _err("商品不存在", 404)
    return _ok("获取商品详情成功", {"goods": dict(goods)})


@app.route(f"{BASE_PREFIX}/goods", methods=["POST"])
def goods_add():
    if _admin_id(request.headers.get("Authorization")) is None:
        return _err("无效token", 401)
    payload = _payload()
    goods_name = payload.get("goods_name")
    goods_price = payload.get("goods_price")
    goods_number = payload.get("goods_number")

    if not goods_name or goods_price is None or goods_number is None:
        return _err("参数错误", 400)

    try:
        goods_price = float(goods_price)
        goods_number = int(goods_number)
    except (TypeError, ValueError):
        return _err("参数错误", 400)

    if goods_price < 0 or goods_number < 0:
        return _err("参数错误", 400)

    goods_id = execute(
        "INSERT INTO sp_goods (goods_name, goods_price, goods_number, cat_id, goods_state, add_time) "
        "VALUES (?, ?, ?, ?, 1, ?)",
        (goods_name, goods_price, goods_number, payload.get("cat_id", 0), int(time.time())),
    )
    return _ok("添加商品成功", {"goods_id": goods_id})


@app.route(f"{BASE_PREFIX}/goods/<int:goods_id>", methods=["PUT"])
def goods_update(goods_id):
    if _admin_id(request.headers.get("Authorization")) is None:
        return _err("无效token", 401)
    goods = query_one("SELECT * FROM sp_goods WHERE id = ? AND is_del = 0", (goods_id,))
    if not goods:
        return _err("商品不存在", 404)
    payload = _payload()
    goods_name = payload.get("goods_name", goods["goods_name"])
    goods_price = payload.get("goods_price", goods["goods_price"])
    goods_number = payload.get("goods_number", goods["goods_number"])
    execute(
        "UPDATE sp_goods SET goods_name = ?, goods_price = ?, goods_number = ?, upd_time = ? WHERE id = ?",
        (goods_name, goods_price, goods_number, int(time.time()), goods_id),
    )
    return _ok("更新商品成功", {"goods_id": goods_id})


@app.route(f"{BASE_PREFIX}/goods/<int:goods_id>", methods=["DELETE"])
def goods_delete(goods_id):
    if _admin_id(request.headers.get("Authorization")) is None:
        return _err("无效token", 401)
    goods = query_one("SELECT * FROM sp_goods WHERE id = ? AND is_del = 0", (goods_id,))
    if not goods:
        return _err("商品不存在", 404)
    execute("UPDATE sp_goods SET is_del = 1, delete_time = ? WHERE id = ?", (int(time.time()), goods_id))
    return _ok("删除商品成功", {"goods_id": goods_id})


# ==================== 分类 ====================

@app.route(f"{BASE_PREFIX}/categories", methods=["GET"])
def category_list():
    rows = query_all("SELECT * FROM sp_category WHERE cat_deleted = 0")
    return _ok("获取分类列表成功", {"categories": _rows(rows)})


# ==================== 购物车 ====================

@app.route(f"{BASE_PREFIX}/cart", methods=["POST"])
def cart_add():
    user_id = _buyer_id(request.headers.get("Authorization"))
    if user_id is None:
        return _err("无效token", 401)
    payload = _payload()
    goods_id = payload.get("goods_id")
    goods_num = payload.get("goods_num", 1)
    if goods_id is None:
        return _err("参数错误", 400)
    try:
        goods_id = int(goods_id)
        goods_num = int(goods_num)
    except (TypeError, ValueError):
        return _err("参数错误", 400)

    goods = query_one("SELECT * FROM sp_goods WHERE id = ? AND is_del = 0", (goods_id,))
    if not goods:
        return _err("商品不存在", 404)

    existing = query_one("SELECT * FROM sp_cart WHERE user_id = ? AND goods_id = ?", (user_id, goods_id))
    if existing:
        execute("UPDATE sp_cart SET goods_num = goods_num + ? WHERE id = ?", (goods_num, existing["id"]))
        cart_id = existing["id"]
    else:
        cart_id = execute(
            "INSERT INTO sp_cart (user_id, goods_id, goods_num, add_time) VALUES (?, ?, ?, ?)",
            (user_id, goods_id, goods_num, int(time.time())),
        )
    return _ok("加入购物车成功", {"cart_id": cart_id})


@app.route(f"{BASE_PREFIX}/cart", methods=["GET"])
def cart_list():
    user_id = _buyer_id(request.headers.get("Authorization"))
    if user_id is None:
        return _err("无效token", 401)
    rows = query_all(
        "SELECT c.id, c.goods_id, c.goods_num, g.goods_name, g.goods_price "
        "FROM sp_cart c JOIN sp_goods g ON c.goods_id = g.id WHERE c.user_id = ?",
        (user_id,),
    )
    return _ok("获取购物车成功", {"cart": _rows(rows)})


@app.route(f"{BASE_PREFIX}/cart/<int:cart_id>", methods=["PUT"])
def cart_update(cart_id):
    user_id = _buyer_id(request.headers.get("Authorization"))
    if user_id is None:
        return _err("无效token", 401)
    cart = query_one("SELECT * FROM sp_cart WHERE id = ? AND user_id = ?", (cart_id, user_id))
    if not cart:
        return _err("购物车项不存在", 404)
    goods_num = _payload().get("goods_num")
    if goods_num is None:
        return _err("参数错误", 400)
    execute("UPDATE sp_cart SET goods_num = ? WHERE id = ?", (int(goods_num), cart_id))
    return _ok("更新购物车成功", {"cart_id": cart_id})


@app.route(f"{BASE_PREFIX}/cart/<int:cart_id>", methods=["DELETE"])
def cart_delete(cart_id):
    user_id = _buyer_id(request.headers.get("Authorization"))
    if user_id is None:
        return _err("无效token", 401)
    cart = query_one("SELECT * FROM sp_cart WHERE id = ? AND user_id = ?", (cart_id, user_id))
    if not cart:
        return _err("购物车项不存在", 404)
    execute("DELETE FROM sp_cart WHERE id = ?", (cart_id,))
    return _ok("删除购物车成功", {"cart_id": cart_id})


# ==================== 订单 ====================

@app.route(f"{BASE_PREFIX}/orders", methods=["POST"])
def order_create():
    user_id = _buyer_id(request.headers.get("Authorization"))
    if user_id is None:
        return _err("无效token", 401)

    cart_items = query_all("SELECT * FROM sp_cart WHERE user_id = ?", (user_id,))
    if not cart_items:
        return _err("购物车为空", 400)

    total = 0.0
    order_items = []
    for item in cart_items:
        goods = query_one("SELECT * FROM sp_goods WHERE id = ? AND is_del = 0", (item["goods_id"],))
        if not goods:
            return _err("商品不存在", 404)
        if goods["goods_number"] < item["goods_num"]:
            return _err("库存不足", 400)
        total += float(goods["goods_price"]) * int(item["goods_num"])
        order_items.append((goods["id"], item["goods_num"], goods["goods_price"]))

    total = round(total, 2)
    now = int(time.time())
    order_number = f"ON{now}{user_id}"

    order_id = execute(
        "INSERT INTO sp_order (order_number, user_id, total_price, pay_status, order_status, create_time) "
        "VALUES (?, ?, ?, 0, 0, ?)",
        (order_number, user_id, total, now),
    )
    for goods_id, num, price in order_items:
        execute(
            "INSERT INTO sp_order_item (order_id, goods_id, goods_num, goods_price) VALUES (?, ?, ?, ?)",
            (order_id, goods_id, num, price),
        )
        execute("UPDATE sp_goods SET goods_number = goods_number - ? WHERE id = ?", (num, goods_id))

    execute("DELETE FROM sp_cart WHERE user_id = ?", (user_id,))

    return _ok("创建订单成功", {"order_id": order_id, "order_number": order_number, "total_price": total})


@app.route(f"{BASE_PREFIX}/orders", methods=["GET"])
def order_list():
    user_id = _buyer_id(request.headers.get("Authorization"))
    if user_id is None:
        return _err("无效token", 401)
    pagenum = int(request.args.get("pagenum", 1))
    pagesize = int(request.args.get("pagesize", 10))
    offset = (pagenum - 1) * pagesize
    total = query_one("SELECT COUNT(*) AS c FROM sp_order WHERE user_id = ?", (user_id,))["c"]
    orders = query_all(
        "SELECT * FROM sp_order WHERE user_id = ? ORDER BY id DESC LIMIT ? OFFSET ?",
        (user_id, pagesize, offset),
    )
    return _ok("获取订单列表成功", {"orders": _rows(orders), "total": total})


@app.route(f"{BASE_PREFIX}/orders/<int:order_id>", methods=["GET"])
def order_detail(order_id):
    user_id = _buyer_id(request.headers.get("Authorization"))
    if user_id is None:
        return _err("无效token", 401)
    order = query_one("SELECT * FROM sp_order WHERE id = ? AND user_id = ?", (order_id, user_id))
    if not order:
        return _err("订单不存在", 404)
    items = query_all("SELECT * FROM sp_order_item WHERE order_id = ?", (order_id,))
    return _ok("获取订单详情成功", {"order": dict(order), "items": _rows(items)})


@app.route(f"{BASE_PREFIX}/orders/<int:order_id>/pay", methods=["PUT"])
def order_pay(order_id):
    user_id = _buyer_id(request.headers.get("Authorization"))
    if user_id is None:
        return _err("无效token", 401)
    order = query_one("SELECT * FROM sp_order WHERE id = ? AND user_id = ?", (order_id, user_id))
    if not order:
        return _err("订单不存在", 404)
    if order["pay_status"] == 1:
        return _err("订单已支付", 400)
    execute(
        "UPDATE sp_order SET pay_status = 1, order_status = 1, pay_time = ? WHERE id = ?",
        (int(time.time()), order_id),
    )
    return _ok("支付成功", {"order_id": order_id})


@app.route(f"{BASE_PREFIX}/orders/<int:order_id>/cancel", methods=["PUT"])
def order_cancel(order_id):
    user_id = _buyer_id(request.headers.get("Authorization"))
    if user_id is None:
        return _err("无效token", 401)
    order = query_one("SELECT * FROM sp_order WHERE id = ? AND user_id = ?", (order_id, user_id))
    if not order:
        return _err("订单不存在", 404)
    if order["order_status"] == 3:
        return _err("订单已取消", 400)

    items = query_all("SELECT * FROM sp_order_item WHERE order_id = ?", (order_id,))
    for item in items:
        execute("UPDATE sp_goods SET goods_number = goods_number + ? WHERE id = ?", (item["goods_num"], item["goods_id"]))

    execute("UPDATE sp_order SET order_status = 3 WHERE id = ?", (order_id,))
    return _ok("取消订单成功", {"order_id": order_id})


# ==================== 用户管理（管理员） ====================

@app.route(f"{BASE_PREFIX}/users", methods=["GET"])
def users_list():
    if _admin_id(request.headers.get("Authorization")) is None:
        return _err("无效token", 401)
    pagenum = int(request.args.get("pagenum", 1))
    pagesize = int(request.args.get("pagesize", 10))
    offset = (pagenum - 1) * pagesize
    total = query_one("SELECT COUNT(*) AS c FROM sp_user", ())["c"]
    users = query_all("SELECT * FROM sp_user ORDER BY id LIMIT ? OFFSET ?", (pagesize, offset))
    return _ok("获取用户列表成功", {"users": _rows(users), "total": total})


@app.route(f"{BASE_PREFIX}/users", methods=["POST"])
def users_add():
    if _admin_id(request.headers.get("Authorization")) is None:
        return _err("无效token", 401)
    payload = _payload()
    username = payload.get("username")
    password = payload.get("password")
    if not username or not password:
        return _err("参数错误", 400)
    user_id = execute(
        "INSERT INTO sp_user (username, password, state) VALUES (?, ?, 1)", (username, password)
    )
    return _ok("创建成功", {"id": user_id, "username": username})


@app.route(f"{BASE_PREFIX}/users/<int:user_id>/state/<state>", methods=["PUT"])
def users_update_state(user_id, state):
    if _admin_id(request.headers.get("Authorization")) is None:
        return _err("无效token", 401)
    user = query_one("SELECT * FROM sp_user WHERE id = ?", (user_id,))
    if not user:
        return _err("用户不存在", 404)
    new_state = 1 if state in ("true", "1") else 0
    execute("UPDATE sp_user SET state = ? WHERE id = ?", (new_state, user_id))
    return _ok("设置状态成功", {"id": user_id, "state": new_state})


# ==================== 上传 ====================

@app.route(f"{BASE_PREFIX}/upload", methods=["POST"])
def upload_file():
    if _auth_info(request.headers.get("Authorization")) is None:
        return _err("无效token", 401)
    if "file" not in request.files:
        return _err("文件未上传", 400)
    file_obj = request.files["file"]
    upload_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file_obj.filename)
    file_obj.save(file_path)
    return _ok("上传成功", {
        "url": f"/uploads/{file_obj.filename}",
        "filename": file_obj.filename,
        "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })


if __name__ == "__main__":
    if not _is_mysql():
        init_db()
    app.run(host="0.0.0.0", port=8888, debug=False)
