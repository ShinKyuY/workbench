"""Entry point: maps (method, path) to handler functions."""

from webshop.api import orders, products, users

ROUTES = {
    ("POST", "/users"): users.create_user,
    ("GET", "/users"): users.get_user,
    ("POST", "/products"): products.create_product,
    ("GET", "/products"): products.list_products,
    ("POST", "/orders"): orders.create_order,
    ("GET", "/orders"): orders.get_order,
}


def handle(method, path, payload=None):
    handler = ROUTES.get((method, path))
    if handler is None:
        return {"status": 404, "errors": ["no such route"]}
    return handler(payload)
