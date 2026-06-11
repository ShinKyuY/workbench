"""Product endpoints."""

from webshop.services.store import StoreService

_service = StoreService()


def create_product(payload):
    errors = []
    name = payload.get("name", "")
    if not name or len(name) < 2:
        errors.append("name too short")
    price = payload.get("price")
    if price is None or price <= 0:
        errors.append("price must be positive")
    if errors:
        return {"status": 400, "errors": errors}
    product = _service.add_product(name, price, payload.get("stock", 0))
    return {"status": 201, "data": product}


def list_products(_payload=None):
    products = _service.list_products()
    return {"status": 200, "data": products}
