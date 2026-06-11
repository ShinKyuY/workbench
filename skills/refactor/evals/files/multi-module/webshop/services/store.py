"""Single service object backing every endpoint."""

import hashlib

from webshop import db


class StoreService:
    """Handles users, products, pricing, email, logging, and sessions."""

    def __init__(self):
        self.outbox = []
        self.logs = []
        self.sessions = {}

    def register_user(self, name, email, phone):
        user = {
            "id": db.next_id("users"),
            "name": name,
            "email": email,
            "phone": phone,
        }
        db.save("users", user)
        self.log("user registered: %s" % user["id"])
        self.send_email(email, "Welcome, %s!" % name)
        return user

    def get_user(self, user_id):
        return db.find("users", user_id)

    def open_session(self, user_id):
        raw = "%s:%s" % (user_id, len(self.sessions))
        token = hashlib.sha1(raw.encode()).hexdigest()
        self.sessions[token] = user_id
        self.log("session opened for %s" % user_id)
        return token

    def verify_session(self, token):
        return self.sessions.get(token)

    def close_session(self, token):
        if token in self.sessions:
            user_id = self.sessions.pop(token)
            self.log("session closed for %s" % user_id)
            return True
        return False

    def add_product(self, name, price, stock):
        product = {
            "id": db.next_id("products"),
            "name": name,
            "price": price,
            "stock": stock,
        }
        db.save("products", product)
        self.log("product added: %s" % product["id"])
        return product

    def list_products(self):
        return db.all_records("products")

    def quote(self, items):
        total = 0
        for item in items:
            product = db.find("products", item["product_id"])
            if product is None:
                continue
            qty = item.get("qty", 1)
            line = product["price"] * qty
            if qty >= 10:
                line = line * 0.97
            total += line
        if total > 50000:
            total = total * 0.95
        elif total > 20000:
            total = total * 0.98
        return round(total, 2)

    def send_email(self, to, subject):
        self.outbox.append({"to": to, "subject": subject})
        self.log("email sent to %s" % to)

    def log(self, message):
        self.logs.append("[store] " + message)
