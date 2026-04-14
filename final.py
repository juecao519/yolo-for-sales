#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能饮料贩卖机
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from ttkbootstrap import Style
import os
from PIL import Image, ImageTk
import cv2
from smart_vending_machine import SmartVendingMachine
from payment_system import PaymentSystem
from iot_client import VendingMachineIoTClient
import threading
import time
import datetime
import json

# 饮料英文-中文映射
DRINK_NAME_MAP = {
    "cola": "可乐",
    "pepsi": "百事可乐",
    "sprite": "雪碧",
    "fanta": "芬达",
    "spring": "矿泉水",
    "ice": "冰红茶",
    "scream": "尖叫",
    "milk": "牛奶",
    "red": "红牛",
    "king": "王老吉"
}
PAYMENT_METHOD_MAP = {
    "wechat": "微信支付",
    "alipay": "支付宝",
    "postpaid": "先用后付"
}

class VendingMachineGUI:
    def __init__(self, root, style):
        self.style = style
        self.root = root
        self.root.title("集美大学计算机工程学院饮料机")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # 初始化变量
        self.model_path = ""
        self.vending_machine = None
        self.before_image_path = ""
        self.after_image_path = ""
        self.payment_system = PaymentSystem()
        self.current_order = None
        self.initial_stock = {k: 100 for k in DRINK_NAME_MAP.keys()}  # 每种饮料100瓶
        
        # 创建界面
        self.create_widgets()
        
        # 尝试加载默认模型
        self.load_default_model()
        
        # 初始化IoT客户端
        self.iot_client = VendingMachineIoTClient(
            broker="broker.emqx.io",  
            port=1883,
            client_id="vending001",
            on_command=self.handle_iot_command
        )
        self.iot_client.start()
        self.start_iot_reporting()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主标题
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=10, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🤖 集美大学计算机工程学院饮料机", 
                              font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # 主容器
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 左侧面板
        left_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        theme_label = tk.Label(left_frame, text="主题切换:", bg='white')
        theme_label.pack(anchor='w', padx=10, pady=(10, 0))
        self.theme_var = tk.StringVar(value=self.style.theme.name)
        theme_combo = ttk.Combobox(left_frame, textvariable=self.theme_var, values=self.style.theme_names(), state='readonly')
        theme_combo.pack(fill='x', padx=10, pady=5)
        def on_theme_change(event):
         self.style.theme_use(self.theme_var.get())
        theme_combo.bind("<<ComboboxSelected>>", on_theme_change)
        left_frame.pack(side='left', fill='y', padx=(0, 5))
        
        # 模型设置
        model_frame = tk.LabelFrame(left_frame, text="模型设置", font=('Arial', 10, 'bold'), 
                                   bg='white', padx=10, pady=10)
        model_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(model_frame, text="模型路径:", bg='white').pack(anchor='w')
        
        model_path_frame = tk.Frame(model_frame, bg='white')
        model_path_frame.pack(fill='x', pady=5)
        
        self.model_path_var = tk.StringVar()
        tk.Entry(model_path_frame, textvariable=self.model_path_var, 
                state='readonly', width=30).pack(side='left', fill='x', expand=True)
        
        tk.Button(model_path_frame, text="选择模型", command=self.select_model, 
                 bg='#3498db', fg='white', relief='flat', padx=10).pack(side='right', padx=(5, 0))
        
        tk.Button(model_frame, text="加载模型", command=self.load_model, 
                 bg='#27ae60', fg='white', relief='flat', padx=20, pady=5).pack(fill='x', pady=5)
        
        # 图片选择
        image_frame = tk.LabelFrame(left_frame, text="图片选择", font=('Arial', 10, 'bold'), 
                                   bg='white', padx=10, pady=10)
        image_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(image_frame, text="开门前图片:", bg='white').pack(anchor='w')
        before_frame = tk.Frame(image_frame, bg='white')
        before_frame.pack(fill='x', pady=5)
        
        self.before_path_var = tk.StringVar()
        tk.Entry(before_frame, textvariable=self.before_path_var, state='readonly', width=25).pack(side='left', fill='x', expand=True)
        tk.Button(before_frame, text="选择", command=self.select_before_image, 
                 bg='#e74c3c', fg='white', relief='flat').pack(side='right', padx=(5, 0))
        
        tk.Label(image_frame, text="关门后图片:", bg='white').pack(anchor='w', pady=(10, 0))
        after_frame = tk.Frame(image_frame, bg='white')
        after_frame.pack(fill='x', pady=5)
        
        self.after_path_var = tk.StringVar()
        tk.Entry(after_frame, textvariable=self.after_path_var, state='readonly', width=25).pack(side='left', fill='x', expand=True)
        tk.Button(after_frame, text="选择", command=self.select_after_image, 
                 bg='#e74c3c', fg='white', relief='flat').pack(side='right', padx=(5, 0))
        
        # 支付设置
        payment_frame = tk.LabelFrame(left_frame, text="支付设置", font=('Arial', 10, 'bold'), 
                                     bg='white', padx=10, pady=10)
        payment_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(payment_frame, text="支付方式:", bg='white').pack(anchor='w')
        self.payment_method = tk.StringVar(value="wechat")
        payment_methods = [
            ("微信支付", "wechat"),
            ("支付宝", "alipay"),
            ("先用后付", "postpaid")
        ]
        for text, value in payment_methods:
            tk.Radiobutton(payment_frame, text=text, variable=self.payment_method, 
                          value=value, bg='white').pack(anchor='w')
        
        # 操作按钮
        button_frame = tk.Frame(left_frame, bg='white')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(button_frame, text="开始分析", command=self.analyze_purchase, 
                 bg='#f39c12', fg='white', relief='flat', font=('Arial', 12, 'bold'), 
                 padx=20, pady=10).pack(fill='x', pady=5)
        
        tk.Button(button_frame, text="处理支付", command=self.process_payment, 
                 bg='#e67e22', fg='white', relief='flat', font=('Arial', 12, 'bold'), 
                 padx=20, pady=10).pack(fill='x', pady=5)
        
        tk.Button(button_frame, text="支付管理", command=self.show_payment_management, 
                 bg='#16a085', fg='white', relief='flat', padx=20, pady=5).pack(fill='x', pady=5)
        
        tk.Button(button_frame, text="清空数据", command=self.clear_data, 
                 bg='#95a5a6', fg='white', relief='flat', padx=20, pady=5).pack(fill='x', pady=5)
        
        # 右侧面板
        right_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # 结果显示区域
        result_frame = tk.LabelFrame(right_frame, text="分析结果", font=('Arial', 10, 'bold'), 
                                    bg='white', padx=10, pady=10)
        result_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=30, font=('Consolas', 9))
        self.result_text.pack(fill='both', expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief='sunken', 
                             anchor='w', bg='#34495e', fg='white')
        status_bar.pack(side='bottom', fill='x')
    
    def load_default_model(self):
        """加载默认模型"""
        default_paths = [
            "drink_detection/quick_train_cpu/weights/best.pt",
            "drink_detection/yolov8_drink_model/weights/best.pt",
            "drink_detection/cpu_training/weights/best.pt"
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                self.model_path_var.set(path)
                self.model_path = path
                self.status_var.set(f"找到默认模型: {path}")
                break
    
    def select_model(self):
        """选择模型文件"""
        filename = filedialog.askopenfilename(
            title="选择YOLOv8模型文件",
            filetypes=[("PyTorch模型", "*.pt"), ("所有文件", "*.*")]
        )
        if filename:
            self.model_path_var.set(filename)
            self.model_path = filename
            self.status_var.set(f"已选择模型: {os.path.basename(filename)}")
    
    def select_before_image(self):
        """选择开门前图片"""
        filename = filedialog.askopenfilename(
            title="选择开门前图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        if filename:
            self.before_image_path = filename
            self.before_path_var.set(os.path.basename(filename))
            self.status_var.set(f"已选择开门前图片: {os.path.basename(filename)}")
    
    def select_after_image(self):
        """选择关门后图片"""
        filename = filedialog.askopenfilename(
            title="选择关门后图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        if filename:
            self.after_image_path = filename
            self.after_path_var.set(os.path.basename(filename))
            self.status_var.set(f"已选择关门后图片: {os.path.basename(filename)}")
    
    def load_model(self):
        """加载模型"""
        if not self.model_path:
            messagebox.showerror("错误", "请先选择模型文件")
            return
        
        try:
            self.vending_machine = SmartVendingMachine(self.model_path)
            self.status_var.set(f"模型加载成功: {os.path.basename(self.model_path)}")
            messagebox.showinfo("成功", "模型加载成功！")
        except Exception as e:
            messagebox.showerror("错误", f"模型加载失败: {e}")
            self.status_var.set("模型加载失败")
    
    def analyze_purchase(self):
        """分析购买"""
        if not self.vending_machine:
            messagebox.showerror("错误", "请先加载模型")
            return
        
        if not self.before_image_path or not self.after_image_path:
            messagebox.showerror("错误", "请选择开门前和关门后的图片")
            return
        
        try:
            self.status_var.set("正在分析购买...")
            self.root.update()
            
            # 记录开门前状态
            self.vending_machine.record_before_state(self.before_image_path, save_result=False)
            
            # 记录关门后状态
            self.vending_machine.record_after_state(self.after_image_path, save_result=False)
            
            # 计算购买情况
            purchase = self.vending_machine.calculate_purchase()
            
            # 显示结果
            self.display_result(purchase)
            
            # 创建订单
            if purchase:
                items = []
                total_amount = 0.0
                for drink, details in purchase.items():
                    items.append({
                        'name': drink,
                        'price': details['total_price'],
                        'quantity': details['reduced']
                    })
                    total_amount += details['total_price']
                
                self.current_order = self.payment_system.create_order(
                    items=items,
                    total_amount=total_amount,
                    payment_method=self.payment_method.get()
                )
                self.status_var.set(f"分析完成，订单已创建: {self.current_order['order_id']}")
            else:
                self.current_order = None
                self.status_var.set("分析完成，未检测到购买")
            
        except Exception as e:
            messagebox.showerror("错误", f"分析过程中出错: {e}")
            self.status_var.set("分析失败")
    
    def display_result(self, purchase):
        """显示分析结果"""
        self.result_text.delete(1.0, tk.END)
        
        if purchase:
            output = "🍹 饮料购买分析结果\n"
            output += "=" * 40 + "\n\n"
            
            output += "📦 购买的商品:\n"
            total_amount = 0.0
            for drink, details in purchase.items():
                output += f"   • {drink}: {details['reduced']}瓶 × ¥{details['price_per_unit']:.1f} = ¥{details['total_price']:.1f}\n"
                total_amount += details['total_price']
            
            output += f"\n💰 总金额: ¥{total_amount:.1f}\n"
            output += f"\n📊 详细统计:\n"
            output += f"   开门前饮料总数: {sum(self.vending_machine.before_count.values())}\n"
            output += f"   关门后饮料总数: {sum(self.vending_machine.after_count.values())}\n"
            output += f"   减少数量: {sum(self.vending_machine.before_count.values()) - sum(self.vending_machine.after_count.values())}\n"
            
            if self.vending_machine.before_count:
                output += "\n开门前饮料详情:\n"
                for drink, count in self.vending_machine.before_count.items():
                    output += f"   • {drink}: {count}瓶\n"
            
            if self.vending_machine.after_count:
                output += "\n关门后饮料详情:\n"
                for drink, count in self.vending_machine.after_count.items():
                    output += f"   • {drink}: {count}瓶\n"
        else:
            output = "❌ 未检测到购买的商品\n"
        
        self.result_text.insert(tk.END, output)
    
    def process_payment(self):
        """处理支付"""
        if not self.current_order:
            messagebox.showerror("错误", "没有待支付的订单，请先进行分析")
            return
        
        try:
            payment_method = self.payment_method.get()
            result = self.payment_system.process_payment(
                self.current_order['order_id'], 
                payment_method
            )
            
            if result['success']:
                # 获取当前时间字符串
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # 先推送事件（中文）
                event = {
                    "事件": "购买成功",
                    "订单号": self.current_order['order_id'],
                    "商品": [
                        {
                            "名称": DRINK_NAME_MAP.get(item['name'], item['name']),
                            "单价": item['price'],
                            "数量": item['quantity'],
                            "小计": item['price'] * item['quantity']
                        } for item in self.current_order['items']
                    ],
                    "总金额": result['amount'],
                    "支付方式": PAYMENT_METHOD_MAP.get(payment_method, payment_method),
                    "时间": now_str,
                    "购买地点": "集美大学计算机工程学院"
                }
                self.iot_client.publish_status("vending/purchase", event)
                # 检查库存并推送告警
                self.check_and_alert_stock()
                # 再清空订单
                self.current_order = None
                self.status_var.set("支付成功")
                messagebox.showinfo("支付成功", 
                    f"订单 {event['订单号']} 支付成功！\n"
                    f"支付方式: {event['支付方式']}\n"
                    f"支付金额: ¥{event['总金额']:.2f}")
            else:
                messagebox.showerror("支付失败", f"支付失败: {result['message']}")
                
        except Exception as e:
            messagebox.showerror("错误", f"支付处理失败: {e}")
    
    def show_payment_management(self):
        """显示支付管理界面"""
        try:
            # 创建新窗口
            payment_window = tk.Toplevel(self.root)
            payment_window.title("支付管理")
            payment_window.geometry("800x600")
            payment_window.configure(bg='white')
            
            # 标题
            title_label = tk.Label(payment_window, text="💳 支付管理系统", 
                                  font=('Arial', 14, 'bold'), bg='white')
            title_label.pack(pady=10)
            
            # 创建选项卡
            notebook = ttk.Notebook(payment_window)
            notebook.pack(fill='both', expand=True, padx=20, pady=10)
            
            # 订单管理选项卡
            orders_frame = ttk.Frame(notebook)
            notebook.add(orders_frame, text="订单管理")
            
            # 支付历史选项卡
            payments_frame = ttk.Frame(notebook)
            notebook.add(payments_frame, text="支付历史")
            
            # 统计信息选项卡
            stats_frame = ttk.Frame(notebook)
            notebook.add(stats_frame, text="统计信息")
            
            # 订单管理
            self.create_orders_tab(orders_frame)
            
            # 支付历史
            self.create_payments_tab(payments_frame)
            
            # 统计信息
            self.create_stats_tab(stats_frame)
            
        except Exception as e:
            messagebox.showerror("错误", f"打开支付管理失败: {e}")
    
    def create_orders_tab(self, parent):
        """创建订单管理选项卡"""
        refresh_btn = tk.Button(parent, text="刷新订单列表", 
                               command=lambda: self.refresh_orders_list(orders_text),
                               bg='#3498db', fg='white', relief='flat', padx=10)
        refresh_btn.pack(pady=5)
        
        orders_text = scrolledtext.ScrolledText(parent, height=20, font=('Consolas', 9))
        orders_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.refresh_orders_list(orders_text)
    
    def create_payments_tab(self, parent):
        """创建支付历史选项卡"""
        refresh_btn = tk.Button(parent, text="刷新支付历史", 
                               command=lambda: self.refresh_payments_list(payments_text),
                               bg='#27ae60', fg='white', relief='flat', padx=10)
        refresh_btn.pack(pady=5)
        
        payments_text = scrolledtext.ScrolledText(parent, height=20, font=('Consolas', 9))
        payments_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.refresh_payments_list(payments_text)
    
    def create_stats_tab(self, parent):
        """创建统计信息选项卡"""
        refresh_btn = tk.Button(parent, text="刷新统计", 
                               command=lambda: self.refresh_stats(stats_text),
                               bg='#e67e22', fg='white', relief='flat', padx=10)
        refresh_btn.pack(pady=5)
        
        stats_text = scrolledtext.ScrolledText(parent, height=20, font=('Consolas', 9))
        stats_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.refresh_stats(stats_text)
    
    def refresh_orders_list(self, text_widget):
        """刷新订单列表"""
        try:
            orders = self.payment_system.get_all_orders()
            text_widget.delete(1.0, tk.END)
            
            if orders:
                output = "📋 所有订单:\n" + "=" * 50 + "\n\n"
                for order in orders:
                    output += f"订单ID: {order['order_id']}\n"
                    output += f"创建时间: {order['timestamp']}\n"
                    output += f"状态: {order['status']}\n"
                    output += f"支付方式: {order['payment_method']}\n"
                    output += f"总金额: ¥{order['total_amount']:.2f}\n"
                    output += "商品:\n"
                    for item in order['items']:
                        output += f"  • {item['name']} - ¥{item['price']:.2f}\n"
                    output += "-" * 50 + "\n"
                text_widget.insert(tk.END, output)
            else:
                text_widget.insert(tk.END, "暂无订单记录")
        except Exception as e:
            text_widget.insert(tk.END, f"获取订单失败: {e}")
    
    def refresh_payments_list(self, text_widget):
        """刷新支付历史"""
        try:
            payments = self.payment_system.get_payment_history()
            text_widget.delete(1.0, tk.END)
            
            if payments:
                output = "💳 支付历史:\n" + "=" * 50 + "\n\n"
                for payment in payments:
                    output += f"订单ID: {payment['order_id']}\n"
                    output += f"支付时间: {payment['timestamp']}\n"
                    output += f"支付方式: {payment['payment_method']}\n"
                    output += f"支付金额: ¥{payment['amount']:.2f}\n"
                    output += f"状态: {payment['status']}\n"
                    output += "-" * 50 + "\n"
                text_widget.insert(tk.END, output)
            else:
                text_widget.insert(tk.END, "暂无支付记录")
        except Exception as e:
            text_widget.insert(tk.END, f"获取支付历史失败: {e}")
    
    def refresh_stats(self, text_widget):
        """刷新统计信息"""
        try:
            stats = self.payment_system.get_statistics()
            text_widget.delete(1.0, tk.END)
            
            output = "📊 支付统计信息:\n" + "=" * 50 + "\n\n"
            output += f"总订单数: {stats['total_orders']}\n"
            output += f"已完成订单: {stats['completed_orders']}\n"
            output += f"待支付订单: {stats['pending_orders']}\n"
            output += f"总收入: ¥{stats['total_revenue']:.2f}\n"
            output += f"平均订单金额: ¥{stats['average_order_amount']:.2f}\n"
            output += "\n支付方式统计:\n"
            for method, count in stats['payment_methods'].items():
                output += f"  • {method}: {count}次\n"
            output += "\n热门商品:\n"
            for item, count in stats['popular_items'].items():
                output += f"  • {item}: {count}次\n"
            
            text_widget.insert(tk.END, output)
        except Exception as e:
            text_widget.insert(tk.END, f"获取统计信息失败: {e}")
    
    def clear_data(self):
        """清空数据"""
        if messagebox.askyesno("确认", "确定要清空所有数据吗？此操作不可恢复。"):
            try:
                # 清空交易历史
                if os.path.exists("transaction_history.json"):
                    os.remove("transaction_history.json")
                
                # 清空支付数据
                self.payment_system.clear_all_data()
                
                # 清空界面
                self.before_image_path = ""
                self.after_image_path = ""
                self.before_path_var.set("")
                self.after_path_var.set("")
                self.result_text.delete(1.0, tk.END)
                self.current_order = None
                
                self.status_var.set("数据已清空")
                messagebox.showinfo("成功", "所有数据已清空")
                
            except Exception as e:
                messagebox.showerror("错误", f"清空数据失败: {e}")
    
    def start_iot_reporting(self):
        def report():
            while True:
                status = {
                    "stock": dict(self.vending_machine.after_count) if self.vending_machine and self.vending_machine.after_count else {},
                    "sales": self.payment_system.get_sales_data() if self.payment_system and hasattr(self.payment_system, "get_sales_data") else {},
                    "device_status": "ok"
                }
                self.iot_client.publish_status("vending/status", status)
                time.sleep(60)
        threading.Thread(target=report, daemon=True).start()
    
    def handle_iot_command(self, command):
        action = command.get("action")
        if action == "get_stock":
            stock = dict(self.vending_machine.after_count) if self.vending_machine and self.vending_machine.after_count else {}
            self.iot_client.publish_status("vending/stock_reply", {"stock": stock})
        elif action == "reboot":
            print("收到重启指令，可在此实现重启逻辑")
        elif action == "set_price":
            drink = command.get("drink")
            price = command.get("price")
            # 这里可以调用价格配置接口
            print(f"设置{drink}价格为{price}")
        # 可扩展更多指令

    def get_current_stock(self):
        """计算当前库存（初始-累计售出）"""
        sold = self.payment_system.get_sales_data() if hasattr(self.payment_system, "get_sales_data") else {}
        stock = {k: self.initial_stock.get(k, 0) - sold.get(k, 0) for k in self.initial_stock}
        return stock

    def check_and_alert_stock(self):
        """检查库存并推送告警"""
        stock = self.get_current_stock()
        low_stock = {k: v for k, v in stock.items() if v <= 20}
        if low_stock:
            alert = {
                "事件": "库存告警",
                "低库存饮料": [
                    {"名称": DRINK_NAME_MAP.get(k, k), "剩余数量": v, "建议": "请及时补货"} for k, v in low_stock.items()
                ]
            }
            self.iot_client.publish_status("vending/alert", alert)

def main():
    """主函数"""
    style = Style(theme='sandstone')  # 你可以换成其他主题
    root = style.master
    app = VendingMachineGUI(root, style)
    root.mainloop()

if __name__ == "__main__":
    main() 