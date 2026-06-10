"""API 라우터 모듈.

users / products / orders 세 리소스의 CRUD 핸들러가 거의 동일한 형태로
복사-붙여넣기 되어 있다.
"""

import time

USERS = {}
PRODUCTS = {}
ORDERS = {}

_NEXT_USER_ID = [1]
_NEXT_PRODUCT_ID = [1]
_NEXT_ORDER_ID = [1]


# ===================================================== users
def list_users(params=None):
    params = params or {}
    page = int(params.get("page", 1))
    size = int(params.get("size", 20))
    if page < 1:
        page = 1
    if size < 1 or size > 100:
        size = 20
    items = sorted(USERS.values(), key=lambda r: r["id"])
    start = (page - 1) * size
    chunk = items[start : start + size]
    return {"status": 200, "body": {"items": chunk, "total": len(items), "page": page}}


def get_user(user_id):
    record = USERS.get(user_id)
    if record is None:
        return {"status": 404, "body": {"error": "user not found"}}
    return {"status": 200, "body": record}


def create_user(body):
    if not body.get("name"):
        return {"status": 400, "body": {"error": "name is required"}}
    if not body.get("email") or "@" not in body["email"]:
        return {"status": 400, "body": {"error": "valid email is required"}}
    new_id = _NEXT_USER_ID[0]
    _NEXT_USER_ID[0] += 1
    record = {
        "id": new_id,
        "name": body["name"],
        "email": body["email"],
        "created_at": time.time(),
    }
    USERS[new_id] = record
    return {"status": 201, "body": record}


def update_user(user_id, body):
    record = USERS.get(user_id)
    if record is None:
        return {"status": 404, "body": {"error": "user not found"}}
    for field in ("name", "email"):
        if field in body:
            record[field] = body[field]
    record["updated_at"] = time.time()
    return {"status": 200, "body": record}


def delete_user(user_id):
    if user_id not in USERS:
        return {"status": 404, "body": {"error": "user not found"}}
    del USERS[user_id]
    return {"status": 204, "body": None}


# ===================================================== products
def list_products(params=None):
    params = params or {}
    page = int(params.get("page", 1))
    size = int(params.get("size", 20))
    if page < 1:
        page = 1
    if size < 1 or size > 100:
        size = 20
    items = sorted(PRODUCTS.values(), key=lambda r: r["id"])
    start = (page - 1) * size
    chunk = items[start : start + size]
    return {"status": 200, "body": {"items": chunk, "total": len(items), "page": page}}


def get_product(product_id):
    record = PRODUCTS.get(product_id)
    if record is None:
        return {"status": 404, "body": {"error": "product not found"}}
    return {"status": 200, "body": record}


def create_product(body):
    if not body.get("name"):
        return {"status": 400, "body": {"error": "name is required"}}
    if body.get("price") is None or body["price"] < 0:
        return {"status": 400, "body": {"error": "valid price is required"}}
    new_id = _NEXT_PRODUCT_ID[0]
    _NEXT_PRODUCT_ID[0] += 1
    record = {
        "id": new_id,
        "name": body["name"],
        "price": body["price"],
        "created_at": time.time(),
    }
    PRODUCTS[new_id] = record
    return {"status": 201, "body": record}


def update_product(product_id, body):
    record = PRODUCTS.get(product_id)
    if record is None:
        return {"status": 404, "body": {"error": "product not found"}}
    for field in ("name", "price"):
        if field in body:
            record[field] = body[field]
    record["updated_at"] = time.time()
    return {"status": 200, "body": record}


def delete_product(product_id):
    if product_id not in PRODUCTS:
        return {"status": 404, "body": {"error": "product not found"}}
    del PRODUCTS[product_id]
    return {"status": 204, "body": None}


# ===================================================== orders
def list_orders(params=None):
    params = params or {}
    page = int(params.get("page", 1))
    size = int(params.get("size", 20))
    if page < 1:
        page = 1
    if size < 1 or size > 100:
        size = 20
    items = sorted(ORDERS.values(), key=lambda r: r["id"])
    start = (page - 1) * size
    chunk = items[start : start + size]
    return {"status": 200, "body": {"items": chunk, "total": len(items), "page": page}}


def get_order(order_id):
    record = ORDERS.get(order_id)
    if record is None:
        return {"status": 404, "body": {"error": "order not found"}}
    return {"status": 200, "body": record}


def create_order(body):
    if not body.get("user_id"):
        return {"status": 400, "body": {"error": "user_id is required"}}
    if not body.get("items"):
        return {"status": 400, "body": {"error": "items is required"}}
    new_id = _NEXT_ORDER_ID[0]
    _NEXT_ORDER_ID[0] += 1
    record = {
        "id": new_id,
        "user_id": body["user_id"],
        "items": body["items"],
        "created_at": time.time(),
    }
    ORDERS[new_id] = record
    return {"status": 201, "body": record}


def update_order(order_id, body):
    record = ORDERS.get(order_id)
    if record is None:
        return {"status": 404, "body": {"error": "order not found"}}
    for field in ("items",):
        if field in body:
            record[field] = body[field]
    record["updated_at"] = time.time()
    return {"status": 200, "body": record}


def delete_order(order_id):
    if order_id not in ORDERS:
        return {"status": 404, "body": {"error": "order not found"}}
    del ORDERS[order_id]
    return {"status": 204, "body": None}


# ===================================================== 라우팅 테이블
ROUTES = {
    ("GET", "/users"): list_users,
    ("GET", "/users/{id}"): get_user,
    ("POST", "/users"): create_user,
    ("PATCH", "/users/{id}"): update_user,
    ("DELETE", "/users/{id}"): delete_user,
    ("GET", "/products"): list_products,
    ("GET", "/products/{id}"): get_product,
    ("POST", "/products"): create_product,
    ("PATCH", "/products/{id}"): update_product,
    ("DELETE", "/products/{id}"): delete_product,
    ("GET", "/orders"): list_orders,
    ("GET", "/orders/{id}"): get_order,
    ("POST", "/orders"): create_order,
    ("PATCH", "/orders/{id}"): update_order,
    ("DELETE", "/orders/{id}"): delete_order,
}
