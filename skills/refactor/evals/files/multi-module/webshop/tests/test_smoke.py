import unittest

from webshop import db
from webshop.app import handle


class WebshopSmokeTest(unittest.TestCase):
    def setUp(self):
        db.clear()

    def test_create_user_ok(self):
        res = handle(
            "POST",
            "/users",
            {"name": "Ada", "email": "ada@example.com", "phone": "010-1234-5678"},
        )
        self.assertEqual(res["status"], 201)
        self.assertEqual(res["data"]["name"], "Ada")

    def test_create_user_rejects_bad_email(self):
        res = handle("POST", "/users", {"name": "Ada", "email": "not-an-email"})
        self.assertEqual(res["status"], 400)
        self.assertIn("email invalid", res["errors"])

    def test_get_user_not_found(self):
        res = handle("GET", "/users", 999)
        self.assertEqual(res["status"], 404)

    def test_create_product_and_list(self):
        res = handle("POST", "/products", {"name": "Pen", "price": 1500, "stock": 10})
        self.assertEqual(res["status"], 201)
        listing = handle("GET", "/products")
        self.assertEqual(listing["status"], 200)
        self.assertEqual(len(listing["data"]), 1)

    def test_create_order_ok(self):
        product = handle(
            "POST", "/products", {"name": "Pen", "price": 1500, "stock": 10}
        )["data"]
        res = handle(
            "POST",
            "/orders",
            {
                "email": "ada@example.com",
                "items": [{"product_id": product["id"], "qty": 2}],
            },
        )
        self.assertEqual(res["status"], 201)
        self.assertEqual(res["data"]["total"], 3000)

    def test_create_order_bulk_discount(self):
        product = handle(
            "POST", "/products", {"name": "Pen", "price": 1000, "stock": 100}
        )["data"]
        res = handle(
            "POST",
            "/orders",
            {
                "email": "ada@example.com",
                "items": [{"product_id": product["id"], "qty": 10}],
            },
        )
        self.assertEqual(res["status"], 201)
        self.assertEqual(res["data"]["total"], 9700.0)

    def test_create_order_out_of_stock(self):
        product = handle(
            "POST", "/products", {"name": "Pen", "price": 1500, "stock": 1}
        )["data"]
        res = handle(
            "POST",
            "/orders",
            {
                "email": "ada@example.com",
                "items": [{"product_id": product["id"], "qty": 5}],
            },
        )
        self.assertEqual(res["status"], 409)

    def test_order_total_volume_discount(self):
        product = handle(
            "POST", "/products", {"name": "Laptop", "price": 30000, "stock": 5}
        )["data"]
        res = handle(
            "POST",
            "/orders",
            {"email": "a@b.co", "items": [{"product_id": product["id"], "qty": 1}]},
        )
        self.assertEqual(res["data"]["total"], 29400.0)


if __name__ == "__main__":
    unittest.main()
