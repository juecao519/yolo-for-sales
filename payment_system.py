#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
支付系统模块
支持微信支付、支付宝和先用后付功能
"""

import json
import os
from datetime import datetime, timedelta
import uuid
import random

class PaymentSystem:
    def __init__(self, config_file="payment_config.json"):
        self.config_file = config_file
        self.orders_file = "orders.json"
        self.payments_file = "payments.json"
        self.load_config()
        self.ensure_files_exist()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "wechat": {"enabled": True, "auto_pay": True, "success_rate": 0.95},
                "alipay": {"enabled": True, "auto_pay": True, "success_rate": 0.98},
                "postpaid": {"enabled": True, "max_debt": 100.0, "payment_deadline_days": 7}
            }
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def ensure_files_exist(self):
        for file in [self.orders_file, self.payments_file]:
            if not os.path.exists(file):
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)

    def create_order(self, items, total_amount, payment_method="wechat"):
        order = {
            "order_id": str(uuid.uuid4())[:8].upper(),
            "timestamp": datetime.now().isoformat(),
            "items": items,
            "total_amount": total_amount,
            "payment_method": payment_method,
            "status": "pending"
        }
        orders = self.load_orders()
        orders.append(order)
        self.save_orders(orders)
        return order

    def process_payment(self, order_id, payment_method):
        orders = self.load_orders()
        order = next((o for o in orders if o["order_id"] == order_id), None)
        if not order:
            return {"success": False, "message": "订单不存在"}
        if order["status"] != "pending":
            return {"success": False, "message": "订单状态不正确"}
        if payment_method == "wechat":
            result = self.process_wechat_payment(order)
        elif payment_method == "alipay":
            result = self.process_alipay_payment(order)
        elif payment_method == "postpaid":
            result = self.process_postpaid_payment(order)
        else:
            return {"success": False, "message": "不支持的支付方式"}
        if result["success"]:
            order["status"] = "completed"
            order["payment_timestamp"] = datetime.now().isoformat()
            self.save_orders(orders)
            self.record_payment(order, result)
        return result

    def process_wechat_payment(self, order):
        if random.random() < self.config.get("wechat", {}).get("success_rate", 0.95):
            return {"success": True, "amount": order["total_amount"], "payment_id": f"WX{str(uuid.uuid4())[:8].upper()}", "message": "微信支付成功"}
        else:
            return {"success": False, "message": "微信支付失败，请重试"}

    def process_alipay_payment(self, order):
        if random.random() < self.config.get("alipay", {}).get("success_rate", 0.98):
            return {"success": True, "amount": order["total_amount"], "payment_id": f"ALI{str(uuid.uuid4())[:8].upper()}", "message": "支付宝支付成功"}
        else:
            return {"success": False, "message": "支付宝支付失败，请重试"}

    def process_postpaid_payment(self, order):
        current_debt = self.get_current_debt()
        max_debt = self.config.get("postpaid", {}).get("max_debt", 100.0)
        if current_debt + order["total_amount"] > max_debt:
            return {"success": False, "message": f"超过最大欠款额度 ¥{max_debt}"}
        return {"success": True, "amount": order["total_amount"], "payment_id": f"POST{str(uuid.uuid4())[:8].upper()}", "message": "后付费订单创建成功", "due_date": self.calculate_due_date()}

    def get_current_debt(self):
        payments = self.load_payments()
        return sum(p["amount"] for p in payments if p["payment_method"] == "postpaid" and p["status"] == "pending")

    def calculate_due_date(self):
        deadline_days = self.config.get("postpaid", {}).get("payment_deadline_days", 7)
        due_date = datetime.now() + timedelta(days=deadline_days)
        return due_date.isoformat()

    def record_payment(self, order, payment_result):
        payment_record = {
            "order_id": order["order_id"],
            "timestamp": datetime.now().isoformat(),
            "payment_method": order["payment_method"],
            "amount": payment_result["amount"],
            "status": "completed" if payment_result["success"] else "failed",
            "payment_id": payment_result.get("payment_id", ""),
            "message": payment_result.get("message", "")
        }
        payments = self.load_payments()
        payments.append(payment_record)
        self.save_payments(payments)

    def load_orders(self):
        try:
            with open(self.orders_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def save_orders(self, orders):
        with open(self.orders_file, 'w', encoding='utf-8') as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)

    def load_payments(self):
        try:
            with open(self.payments_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def save_payments(self, payments):
        with open(self.payments_file, 'w', encoding='utf-8') as f:
            json.dump(payments, f, ensure_ascii=False, indent=2)

    def get_all_orders(self):
        return self.load_orders()

    def get_payment_history(self):
        return self.load_payments()

    def get_statistics(self):
        orders = self.load_orders()
        payments = self.load_payments()
        total_orders = len(orders)
        completed_orders = len([o for o in orders if o["status"] == "completed"])
        pending_orders = len([o for o in orders if o["status"] == "pending"])
        total_revenue = sum([p["amount"] for p in payments if p["status"] == "completed"])
        average_order_amount = total_revenue / completed_orders if completed_orders > 0 else 0
        payment_methods = {}
        for payment in payments:
            method = payment["payment_method"]
            payment_methods[method] = payment_methods.get(method, 0) + 1
        popular_items = {}
        for order in orders:
            for item in order["items"]:
                name = item["name"]
                popular_items[name] = popular_items.get(name, 0) + 1
        return {
            "total_orders": total_orders,
            "completed_orders": completed_orders,
            "pending_orders": pending_orders,
            "total_revenue": total_revenue,
            "average_order_amount": average_order_amount,
            "payment_methods": payment_methods,
            "popular_items": popular_items
        }

    def refund_order(self, order_id, reason=""):
        orders = self.load_orders()
        payments = self.load_payments()
        order = next((o for o in orders if o["order_id"] == order_id), None)
        if not order:
            return {"success": False, "message": "订单不存在"}
        if order["status"] != "completed":
            return {"success": False, "message": "订单状态不正确，无法退款"}
        refund_record = {
            "order_id": order_id,
            "timestamp": datetime.now().isoformat(),
            "type": "refund",
            "amount": order["total_amount"],
            "reason": reason,
            "status": "completed"
        }
        payments.append(refund_record)
        self.save_payments(payments)
        order["status"] = "refunded"
        order["refund_timestamp"] = datetime.now().isoformat()
        order["refund_reason"] = reason
        self.save_orders(orders)
        return {"success": True, "message": f"退款成功，金额: ¥{order['total_amount']:.2f}", "refund_amount": order["total_amount"]}

    def clear_all_data(self):
        with open(self.orders_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        with open(self.payments_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return True 