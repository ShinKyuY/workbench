"""Order endpoints."""

import re

from webshop import db
from webshop.services.store import StoreService

_service = StoreService()


def create_order(payload):
    errors = []
    email = payload.get("email", "")
    if not email:
        errors.append("email required")
    else:
        if not re.match(r"^[\w.+-]+@[\w-]+\.[\w.]+$", email):
            errors.append("email invalid")
    items = payload.get("items")
    if not items:
        errors.append("items required")
    if errors:
        return {"status": 400, "errors": errors}

    total = 0
    for item in items:
        product = db.find("products", item.get("product_id"))
        if product is not None:
            qty = item.get("qty", 1)
            if qty > 0:
                if product["stock"] >= qty:
                    line = product["price"] * qty
                    if qty >= 10:
                        line = line * 0.97
                    total += line
                else:
                    return {
                        "status": 409,
                        "errors": ["out of stock: %s" % product["name"]],
                    }
            else:
                return {"status": 400, "errors": ["qty must be positive"]}
        else:
            return {"status": 404, "errors": ["product not found"]}

    if total > 50000:
        total = total * 0.95
    elif total > 20000:
        total = total * 0.98

    order = {
        "id": db.next_id("orders"),
        "email": email,
        "items": items,
        "total": round(total, 2),
    }
    db.save("orders", order)
    _service.log("order created: %s" % order["id"])
    _service.send_email(email, "Order #%s confirmed" % order["id"])
    return {"status": 201, "data": order}


def get_order(order_id):
    order = db.find("orders", order_id)
    if order is None:
        return {"status": 404, "errors": ["order not found"]}
    return {"status": 200, "data": order}
