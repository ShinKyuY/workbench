"""주문 처리 모듈.

process_order 하나가 검증/할인/배송비/결제/재고/알림을 전부 처리한다.
"""

import datetime


def process_order(order, user, inventory, payment_client, email_client, sms_client, log):
    # ------------------------------------------------------------------
    # 1) 검증
    # ------------------------------------------------------------------
    errors = []
    if order is None:
        raise ValueError("order is required")
    if "items" not in order or not order["items"]:
        errors.append("주문 항목이 없습니다")
    else:
        for item in order["items"]:
            if "sku" not in item or not item["sku"]:
                errors.append("sku 누락")
            else:
                if item["sku"] not in inventory:
                    errors.append("존재하지 않는 상품: " + item["sku"])
                else:
                    if item.get("qty", 0) <= 0:
                        errors.append("수량 오류: " + item["sku"])
                    else:
                        if inventory[item["sku"]]["stock"] < item["qty"]:
                            errors.append("재고 부족: " + item["sku"])
    if user is None:
        errors.append("사용자 정보가 없습니다")
    else:
        if "email" not in user or "@" not in user.get("email", ""):
            errors.append("이메일 형식 오류")
        if user.get("status") == "suspended":
            errors.append("정지된 사용자")
    method = order.get("payment_method", "card")
    if method == "card":
        if user is not None and not user.get("card_token"):
            errors.append("카드 토큰이 없습니다")
    elif method == "bank":
        if not order.get("bank_account"):
            errors.append("계좌 정보가 없습니다")
    else:
        errors.append("지원하지 않는 결제 수단: " + str(method))
    if order.get("coupon"):
        c = order["coupon"]
        if c.get("expires"):
            exp = datetime.date.fromisoformat(c["expires"])
            if exp < datetime.date.today():
                errors.append("만료된 쿠폰")
        if c.get("type") not in ("percent", "fixed"):
            errors.append("알 수 없는 쿠폰 타입")
    if errors:
        log("[WARN] 주문 검증 실패 order_id=%s errors=%s" % (order.get("id"), errors))
        return {"ok": False, "order_id": order.get("id"), "errors": errors}

    # ------------------------------------------------------------------
    # 2) 소계 계산
    # ------------------------------------------------------------------
    subtotal = 0.0
    for item in order["items"]:
        price = inventory[item["sku"]]["price"]
        subtotal = subtotal + price * item["qty"]

    # ------------------------------------------------------------------
    # 3) 할인 계산
    # ------------------------------------------------------------------
    discount = 0.0
    if user.get("tier") == "gold":
        if subtotal >= 100000:
            discount = subtotal * 0.1
        else:
            discount = subtotal * 0.05
    elif user.get("tier") == "silver":
        if subtotal >= 100000:
            discount = subtotal * 0.07
        else:
            discount = subtotal * 0.03
    elif user.get("tier") == "bronze":
        if subtotal >= 100000:
            discount = subtotal * 0.05
        else:
            discount = subtotal * 0.01
    if order.get("coupon"):
        c = order["coupon"]
        if c.get("type") == "percent":
            coupon_discount = subtotal * (c.get("value", 0) / 100.0)
            if coupon_discount > 30000:
                coupon_discount = 30000
            discount = discount + coupon_discount
        elif c.get("type") == "fixed":
            discount = discount + c.get("value", 0)
    if user.get("order_count", 0) == 0:
        # 첫 주문 보너스
        discount = discount + 5000
    if discount > subtotal * 0.5:
        discount = subtotal * 0.5

    # ------------------------------------------------------------------
    # 4) 배송비 / 세금 / 총액
    # ------------------------------------------------------------------
    after_discount = subtotal - discount
    if after_discount >= 50000:
        shipping = 0
    else:
        if order.get("region") == "jeju":
            shipping = 6000
        elif order.get("region") == "island":
            shipping = 8000
        else:
            shipping = 3000
    tax = round(after_discount * 0.1)
    total = int(round(after_discount + shipping + tax))

    # ------------------------------------------------------------------
    # 5) 결제 (네트워크 오류 시 3회 재시도)
    # ------------------------------------------------------------------
    attempts = 0
    payment_result = None
    while True:
        try:
            if method == "card":
                payment_result = payment_client.charge_card(user["card_token"], total)
            else:
                payment_result = payment_client.transfer(order["bank_account"], total)
            break
        except ConnectionError:
            attempts = attempts + 1
            log("[WARN] 결제 게이트웨이 연결 실패 (시도 %d/3)" % attempts)
            if attempts >= 3:
                log("[ERROR] 결제 최종 실패 order_id=%s" % order.get("id"))
                return {"ok": False, "order_id": order.get("id"), "errors": ["결제 실패: 네트워크 오류"]}
    if payment_result.get("status") != "approved":
        log("[WARN] 결제 거절 order_id=%s reason=%s" % (order.get("id"), payment_result.get("reason")))
        return {"ok": False, "order_id": order.get("id"), "errors": ["결제 거절"]}

    # ------------------------------------------------------------------
    # 6) 재고 차감
    # ------------------------------------------------------------------
    for item in order["items"]:
        inventory[item["sku"]]["stock"] = inventory[item["sku"]]["stock"] - item["qty"]
        if inventory[item["sku"]]["stock"] <= 2:
            log("[INFO] 재고 부족 임박 sku=%s 남은수량=%d" % (item["sku"], inventory[item["sku"]]["stock"]))

    # ------------------------------------------------------------------
    # 7) 알림 전송
    # ------------------------------------------------------------------
    notified = []
    try:
        body_lines = []
        body_lines.append("주문이 완료되었습니다.")
        body_lines.append("주문번호: %s" % order.get("id"))
        body_lines.append("결제금액: %d원" % total)
        if discount > 0:
            body_lines.append("할인금액: %d원" % int(discount))
        email_client.send(user["email"], "주문 완료 안내", "\n".join(body_lines))
        notified.append("email")
    except Exception as e:
        log("[ERROR] 이메일 전송 실패: %s" % e)
    if user.get("phone"):
        try:
            sms_client.send(user["phone"], "[주문완료] %s원 결제되었습니다" % total)
            notified.append("sms")
        except Exception as e:
            log("[ERROR] SMS 전송 실패: %s" % e)

    log("[INFO] 주문 완료 order_id=%s total=%d" % (order.get("id"), total))
    return {
        "ok": True,
        "order_id": order.get("id"),
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "tax": tax,
        "total": total,
        "payment_id": payment_result.get("payment_id"),
        "notified": notified,
    }
