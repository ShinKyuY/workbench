"""User endpoints."""

import re

from webshop.services.store import StoreService

_service = StoreService()


def create_user(payload):
    errors = []
    email = payload.get("email", "")
    if not email:
        errors.append("email required")
    else:
        if not re.match(r"^[\w.+-]+@[\w-]+\.[\w.]+$", email):
            errors.append("email invalid")
    phone = payload.get("phone", "")
    if phone:
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 9 or len(digits) > 11:
            errors.append("phone invalid")
    name = payload.get("name", "")
    if not name or len(name) < 2:
        errors.append("name too short")
    if errors:
        return {"status": 400, "errors": errors}
    user = _service.register_user(name, email, phone)
    return {"status": 201, "data": user}


def get_user(user_id):
    user = _service.get_user(user_id)
    if user is None:
        return {"status": 404, "errors": ["user not found"]}
    return {"status": 200, "data": user}
