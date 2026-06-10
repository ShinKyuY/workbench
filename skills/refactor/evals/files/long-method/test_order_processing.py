"""process_order 동작 보존 테스트. python3 -m unittest 로 실행."""

import unittest

from order_processing import process_order


class FakePayment:
    def __init__(self, status="approved", fail_times=0):
        self.status = status
        self.fail_times = fail_times
        self.calls = []

    def charge_card(self, token, amount):
        if self.fail_times > 0:
            self.fail_times -= 1
            raise ConnectionError("gateway down")
        self.calls.append(("card", token, amount))
        return {"status": self.status, "payment_id": "pay_1", "reason": "limit"}

    def transfer(self, account, amount):
        self.calls.append(("bank", account, amount))
        return {"status": self.status, "payment_id": "pay_2", "reason": None}


class FakeEmail:
    def __init__(self, fail=False):
        self.fail = fail
        self.sent = []

    def send(self, to, subject, body):
        if self.fail:
            raise RuntimeError("smtp error")
        self.sent.append((to, subject, body))


class FakeSms:
    def __init__(self):
        self.sent = []

    def send(self, phone, text):
        self.sent.append((phone, text))


def make_inventory():
    return {
        "A": {"price": 20000, "stock": 10},
        "B": {"price": 5000, "stock": 3},
    }


def make_user(**over):
    user = {
        "email": "kim@example.com",
        "tier": "gold",
        "order_count": 5,
        "card_token": "tok_1",
        "status": "active",
    }
    user.update(over)
    return user


class ProcessOrderTest(unittest.TestCase):
    def setUp(self):
        self.logs = []
        self.payment = FakePayment()
        self.email = FakeEmail()
        self.sms = FakeSms()

    def run_order(self, order, user, inventory=None):
        inv = inventory if inventory is not None else make_inventory()
        result = process_order(
            order, user, inv, self.payment, self.email, self.sms, self.logs.append
        )
        return result, inv

    def test_success_totals(self):
        order = {"id": "o1", "items": [{"sku": "A", "qty": 2}, {"sku": "B", "qty": 1}]}
        result, _ = self.run_order(order, make_user())
        self.assertTrue(result["ok"])
        self.assertEqual(result["subtotal"], 45000)
        self.assertEqual(result["discount"], 2250.0)
        self.assertEqual(result["shipping"], 3000)
        self.assertEqual(result["tax"], 4275)
        self.assertEqual(result["total"], 50025)
        self.assertEqual(result["payment_id"], "pay_1")

    def test_free_shipping_over_threshold(self):
        order = {"id": "o2", "items": [{"sku": "A", "qty": 3}]}
        result, _ = self.run_order(order, make_user())
        self.assertEqual(result["shipping"], 0)
        self.assertEqual(result["total"], 62700)

    def test_first_order_bonus(self):
        order = {"id": "o3", "items": [{"sku": "B", "qty": 1}]}
        result, _ = self.run_order(order, make_user(order_count=0, tier=None))
        self.assertEqual(result["discount"], 2500.0)  # 50% 상한 적용

    def test_percent_coupon_stacks_with_tier(self):
        order = {
            "id": "o4",
            "items": [{"sku": "A", "qty": 2}],
            "coupon": {"type": "percent", "value": 10, "expires": "2099-01-01"},
        }
        result, _ = self.run_order(order, make_user(tier="silver"))
        self.assertEqual(result["discount"], 40000 * 0.03 + 4000)

    def test_validation_errors(self):
        order = {"id": "o5", "items": []}
        result, _ = self.run_order(order, make_user(status="suspended", email="bad"))
        self.assertFalse(result["ok"])
        self.assertIn("주문 항목이 없습니다", result["errors"])
        self.assertIn("이메일 형식 오류", result["errors"])
        self.assertIn("정지된 사용자", result["errors"])

    def test_expired_coupon_rejected(self):
        order = {
            "id": "o6",
            "items": [{"sku": "A", "qty": 1}],
            "coupon": {"type": "percent", "value": 5, "expires": "2020-01-01"},
        }
        result, _ = self.run_order(order, make_user())
        self.assertFalse(result["ok"])
        self.assertIn("만료된 쿠폰", result["errors"])

    def test_payment_declined(self):
        self.payment = FakePayment(status="declined")
        order = {"id": "o7", "items": [{"sku": "A", "qty": 1}]}
        result, inv = self.run_order(order, make_user())
        self.assertFalse(result["ok"])
        self.assertIn("결제 거절", result["errors"])
        self.assertEqual(inv["A"]["stock"], 10)  # 재고 차감 없음

    def test_payment_retry_then_success(self):
        self.payment = FakePayment(fail_times=2)
        order = {"id": "o8", "items": [{"sku": "A", "qty": 1}]}
        result, _ = self.run_order(order, make_user())
        self.assertTrue(result["ok"])

    def test_payment_retry_exhausted(self):
        self.payment = FakePayment(fail_times=3)
        order = {"id": "o9", "items": [{"sku": "A", "qty": 1}]}
        result, _ = self.run_order(order, make_user())
        self.assertFalse(result["ok"])
        self.assertIn("결제 실패: 네트워크 오류", result["errors"])

    def test_stock_decremented_and_notifications(self):
        order = {"id": "o10", "items": [{"sku": "B", "qty": 2}]}
        result, inv = self.run_order(order, make_user(phone="010-1111-2222"))
        self.assertEqual(inv["B"]["stock"], 1)
        self.assertEqual(result["notified"], ["email", "sms"])
        self.assertEqual(len(self.email.sent), 1)
        self.assertEqual(len(self.sms.sent), 1)

    def test_email_failure_does_not_break_order(self):
        self.email = FakeEmail(fail=True)
        order = {"id": "o11", "items": [{"sku": "A", "qty": 1}]}
        result, _ = self.run_order(order, make_user())
        self.assertTrue(result["ok"])
        self.assertNotIn("email", result["notified"])

    def test_missing_card_token(self):
        order = {"id": "o12", "items": [{"sku": "A", "qty": 1}]}
        result, _ = self.run_order(order, make_user(card_token=None))
        self.assertFalse(result["ok"])
        self.assertIn("카드 토큰이 없습니다", result["errors"])


if __name__ == "__main__":
    unittest.main()
