"""routes 동작 보존 테스트. python3 -m unittest 로 실행."""

import unittest

import routes


class RoutesTest(unittest.TestCase):
    def setUp(self):
        routes.USERS.clear()
        routes.PRODUCTS.clear()
        routes.ORDERS.clear()
        routes._NEXT_USER_ID[0] = 1
        routes._NEXT_PRODUCT_ID[0] = 1
        routes._NEXT_ORDER_ID[0] = 1

    # ---------------- users ----------------
    def test_user_crud_cycle(self):
        created = routes.create_user({"name": "kim", "email": "kim@example.com"})
        self.assertEqual(created["status"], 201)
        uid = created["body"]["id"]

        got = routes.get_user(uid)
        self.assertEqual(got["status"], 200)
        self.assertEqual(got["body"]["name"], "kim")

        updated = routes.update_user(uid, {"name": "kim2"})
        self.assertEqual(updated["body"]["name"], "kim2")
        self.assertIn("updated_at", updated["body"])

        deleted = routes.delete_user(uid)
        self.assertEqual(deleted["status"], 204)
        self.assertEqual(routes.get_user(uid)["status"], 404)

    def test_create_user_validation(self):
        self.assertEqual(routes.create_user({"email": "a@b.c"})["status"], 400)
        self.assertEqual(
            routes.create_user({"name": "x", "email": "nope"})["status"], 400
        )

    def test_list_users_pagination(self):
        for i in range(25):
            routes.create_user({"name": "u%d" % i, "email": "u%d@x.com" % i})
        page1 = routes.list_users({"page": 1, "size": 20})
        page2 = routes.list_users({"page": 2, "size": 20})
        self.assertEqual(len(page1["body"]["items"]), 20)
        self.assertEqual(len(page2["body"]["items"]), 5)
        self.assertEqual(page1["body"]["total"], 25)
        bad = routes.list_users({"page": 0, "size": 999})
        self.assertEqual(bad["body"]["page"], 1)
        self.assertEqual(len(bad["body"]["items"]), 20)

    # ---------------- products ----------------
    def test_product_crud_cycle(self):
        created = routes.create_product({"name": "pen", "price": 1000})
        self.assertEqual(created["status"], 201)
        pid = created["body"]["id"]
        self.assertEqual(routes.get_product(pid)["body"]["price"], 1000)
        updated = routes.update_product(pid, {"price": 1500})
        self.assertEqual(updated["body"]["price"], 1500)
        self.assertEqual(routes.delete_product(pid)["status"], 204)
        self.assertEqual(routes.get_product(pid)["status"], 404)

    def test_create_product_validation(self):
        self.assertEqual(routes.create_product({"price": 10})["status"], 400)
        self.assertEqual(
            routes.create_product({"name": "x", "price": -1})["status"], 400
        )

    # ---------------- orders ----------------
    def test_order_crud_cycle(self):
        created = routes.create_order({"user_id": 1, "items": [{"sku": "A"}]})
        self.assertEqual(created["status"], 201)
        oid = created["body"]["id"]
        self.assertEqual(routes.get_order(oid)["status"], 200)
        updated = routes.update_order(oid, {"items": [{"sku": "B"}]})
        self.assertEqual(updated["body"]["items"], [{"sku": "B"}])
        self.assertEqual(routes.delete_order(oid)["status"], 204)
        self.assertEqual(routes.get_order(oid)["status"], 404)

    def test_create_order_validation(self):
        self.assertEqual(routes.create_order({"items": [1]})["status"], 400)
        self.assertEqual(routes.create_order({"user_id": 1})["status"], 400)

    def test_not_found_responses(self):
        self.assertEqual(routes.get_user(99)["status"], 404)
        self.assertEqual(routes.update_product(99, {})["status"], 404)
        self.assertEqual(routes.delete_order(99)["status"], 404)

    # ---------------- 라우팅 테이블 ----------------
    def test_routes_table_complete(self):
        self.assertEqual(len(routes.ROUTES), 15)
        for resource in ("users", "products", "orders"):
            for method, path in (
                ("GET", "/%s" % resource),
                ("GET", "/%s/{id}" % resource),
                ("POST", "/%s" % resource),
                ("PATCH", "/%s/{id}" % resource),
                ("DELETE", "/%s/{id}" % resource),
            ):
                self.assertIn((method, path), routes.ROUTES)
        self.assertTrue(all(callable(f) for f in routes.ROUTES.values()))


if __name__ == "__main__":
    unittest.main()
