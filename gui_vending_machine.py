#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能饮料贩卖机图形界面
基于Tkinter的GUI界面
废弃了，因为做了新的gui
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
from datetime import datetime
from PIL import Image, ImageTk
import cv2
import numpy as np
from smart_vending_machine import SmartVendingMachine

class VendingMachineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("智能饮料贩卖机系统")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # 初始化变量
        self.model_path = ""
        self.vending_machine = None
        self.before_image_path = ""
        self.after_image_path = ""
        self.before_image_tk = None
        self.after_image_tk = None
        
        # 创建界面
        self.create_widgets()
        
        # 尝试加载默认模型
        self.load_default_model()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主标题
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=10, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🤖 智能饮料贩卖机系统", 
                              font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # 主容器
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 左侧面板 - 模型和图片选择
        left_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        left_frame.pack(side='left', fill='y', padx=(0, 5))
        
        # 模型选择区域
        model_frame = tk.LabelFrame(left_frame, text="模型设置", font=('Arial', 10, 'bold'), 
                                   bg='white', padx=10, pady=10)
        model_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(model_frame, text="模型路径:", bg='white').pack(anchor='w')
        
        model_path_frame = tk.Frame(model_frame, bg='white')
        model_path_frame.pack(fill='x', pady=5)
        
        self.model_path_var = tk.StringVar()
        self.model_path_entry = tk.Entry(model_path_frame, textvariable=self.model_path_var, 
                                        state='readonly', width=30)
        self.model_path_entry.pack(side='left', fill='x', expand=True)
        
        tk.Button(model_path_frame, text="选择模型", command=self.select_model, 
                 bg='#3498db', fg='white', relief='flat', padx=10).pack(side='right', padx=(5, 0))
        
        tk.Button(model_frame, text="加载模型", command=self.load_model, 
                 bg='#27ae60', fg='white', relief='flat', padx=20, pady=5).pack(fill='x', pady=5)
        
        # 图片选择区域
        image_frame = tk.LabelFrame(left_frame, text="图片选择", font=('Arial', 10, 'bold'), 
                                   bg='white', padx=10, pady=10)
        image_frame.pack(fill='x', padx=10, pady=5)
        
        # 开门前图片
        tk.Label(image_frame, text="开门前图片:", bg='white').pack(anchor='w')
        before_frame = tk.Frame(image_frame, bg='white')
        before_frame.pack(fill='x', pady=5)
        
        self.before_path_var = tk.StringVar()
        tk.Entry(before_frame, textvariable=self.before_path_var, state='readonly', width=25).pack(side='left', fill='x', expand=True)
        tk.Button(before_frame, text="选择", command=self.select_before_image, 
                 bg='#e74c3c', fg='white', relief='flat').pack(side='right', padx=(5, 0))
        
        # 关门后图片
        tk.Label(image_frame, text="关门后图片:", bg='white').pack(anchor='w', pady=(10, 0))
        after_frame = tk.Frame(image_frame, bg='white')
        after_frame.pack(fill='x', pady=5)
        
        self.after_path_var = tk.StringVar()
        tk.Entry(after_frame, textvariable=self.after_path_var, state='readonly', width=25).pack(side='left', fill='x', expand=True)
        tk.Button(after_frame, text="选择", command=self.select_after_image, 
                 bg='#e74c3c', fg='white', relief='flat').pack(side='right', padx=(5, 0))
        
        # 操作按钮
        button_frame = tk.Frame(left_frame, bg='white')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(button_frame, text="开始分析", command=self.analyze_purchase, 
                 bg='#f39c12', fg='white', relief='flat', font=('Arial', 12, 'bold'), 
                 padx=20, pady=10).pack(fill='x', pady=5)
        
        tk.Button(button_frame, text="查看交易历史", command=self.show_history, 
                 bg='#9b59b6', fg='white', relief='flat', padx=20, pady=5).pack(fill='x', pady=5)
        
        tk.Button(button_frame, text="清空数据", command=self.clear_data, 
                 bg='#95a5a6', fg='white', relief='flat', padx=20, pady=5).pack(fill='x', pady=5)
        
        # 右侧面板 - 图片显示和结果
        right_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # 图片显示区域
        image_display_frame = tk.LabelFrame(right_frame, text="图片预览", font=('Arial', 10, 'bold'), 
                                           bg='white', padx=10, pady=10)
        image_display_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 图片显示
        self.image_canvas = tk.Canvas(image_display_frame, bg='#ecf0f1', height=300)
        self.image_canvas.pack(fill='both', expand=True, pady=5)
        
        # 结果显示区域
        result_frame = tk.LabelFrame(right_frame, text="分析结果", font=('Arial', 10, 'bold'), 
                                    bg='white', padx=10, pady=10)
        result_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, font=('Consolas', 9))
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
            self.display_image(filename, 'before')
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
            self.display_image(filename, 'after')
            self.status_var.set(f"已选择关门后图片: {os.path.basename(filename)}")
    
    def display_image(self, image_path, image_type):
        """显示图片"""
        try:
            # 读取图片
            image = cv2.imread(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 调整图片大小
            height, width = image.shape[:2]
            max_size = 200
            if height > max_size or width > max_size:
                scale = max_size / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
            
            # 转换为PIL图片
            pil_image = Image.fromarray(image)
            tk_image = ImageTk.PhotoImage(pil_image)
            
            # 保存引用并显示
            if image_type == 'before':
                self.before_image_tk = tk_image
            else:
                self.after_image_tk = tk_image
            
            # 清空画布并显示图片
            self.image_canvas.delete("all")
            self.image_canvas.create_image(100, 150, image=tk_image, anchor='center')
            
            # 添加标签
            label_text = "开门前" if image_type == 'before' else "关门后"
            self.image_canvas.create_text(100, 20, text=label_text, font=('Arial', 12, 'bold'), fill='#2c3e50')
            
        except Exception as e:
            messagebox.showerror("错误", f"无法显示图片: {str(e)}")
    
    def load_model(self):
        """加载模型"""
        if not self.model_path:
            messagebox.showerror("错误", "请先选择模型文件")
            return
        
        try:
            self.status_var.set("正在加载模型...")
            self.root.update()
            
            self.vending_machine = SmartVendingMachine(self.model_path)
            
            self.status_var.set("模型加载成功")
            messagebox.showinfo("成功", "模型加载成功！")
            
        except Exception as e:
            self.status_var.set("模型加载失败")
            messagebox.showerror("错误", f"模型加载失败: {str(e)}")
    
    def analyze_purchase(self):
        """分析购买情况"""
        if not self.vending_machine:
            messagebox.showerror("错误", "请先加载模型")
            return
        
        if not self.before_image_path or not self.after_image_path:
            messagebox.showerror("错误", "请选择开门前和关门后的图片")
            return
        
        try:
            self.status_var.set("正在分析...")
            self.root.update()
            
            # 清空结果显示
            self.result_text.delete(1.0, tk.END)
            
            # 记录开门前状态
            self.result_text.insert(tk.END, "📸 记录开门前状态...\n")
            self.vending_machine.record_before_state(self.before_image_path, save_result=False)
            
            # 记录关门后状态
            self.result_text.insert(tk.END, "\n📸 记录关门后状态...\n")
            self.vending_machine.record_after_state(self.after_image_path, save_result=False)
            
            # 计算购买情况
            self.result_text.insert(tk.END, "\n🛒 购买分析:\n")
            self.result_text.insert(tk.END, "=" * 40 + "\n")
            
            purchase = self.vending_machine.calculate_purchase()
            
            if purchase:
                # 生成账单
                self.result_text.insert(tk.END, "\n🧾 智能贩卖机账单\n")
                self.result_text.insert(tk.END, "=" * 50 + "\n")
                self.result_text.insert(tk.END, f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                self.result_text.insert(tk.END, "=" * 50 + "\n")
                
                total_amount = 0.0
                for drink, details in purchase.items():
                    line = f"{drink:12} {details['reduced']:2d} 瓶 × ¥{details['price_per_unit']:4.1f} = ¥{details['total_price']:6.1f}\n"
                    self.result_text.insert(tk.END, line)
                    total_amount += details['total_price']
                
                self.result_text.insert(tk.END, "=" * 50 + "\n")
                self.result_text.insert(tk.END, f"{'总计':12} {'':2} {'':4} {'':6} ¥{total_amount:6.1f}\n")
                self.result_text.insert(tk.END, "=" * 50 + "\n")
                self.result_text.insert(tk.END, "感谢使用智能贩卖机！\n")
                
                # 保存交易历史
                self.vending_machine.save_transaction_history()
                
                self.status_var.set("分析完成")
                messagebox.showinfo("成功", "购买分析完成！")
            else:
                self.result_text.insert(tk.END, "   - 没有检测到购买行为\n")
                self.status_var.set("分析完成 - 无购买")
                messagebox.showinfo("提示", "没有检测到购买行为")
            
        except Exception as e:
            self.status_var.set("分析失败")
            messagebox.showerror("错误", f"分析过程中出现错误: {str(e)}")
    
    def show_history(self):
        """显示交易历史"""
        if not self.vending_machine:
            messagebox.showerror("错误", "请先加载模型")
            return
        
        try:
            # 加载交易历史
            self.vending_machine.load_transaction_history()
            
            if not self.vending_machine.transaction_history:
                messagebox.showinfo("提示", "暂无交易记录")
                return
            
            # 创建历史窗口
            history_window = tk.Toplevel(self.root)
            history_window.title("交易历史")
            history_window.geometry("600x400")
            history_window.configure(bg='white')
            
            # 历史记录显示
            history_text = scrolledtext.ScrolledText(history_window, font=('Consolas', 10))
            history_text.pack(fill='both', expand=True, padx=10, pady=10)
            
            history_text.insert(tk.END, "📂 交易历史记录\n")
            history_text.insert(tk.END, "=" * 60 + "\n\n")
            
            for i, transaction in enumerate(self.vending_machine.transaction_history, 1):
                history_text.insert(tk.END, f"{i}. {transaction['timestamp']} - ¥{transaction['total_amount']:.1f}\n")
                for drink, details in transaction['purchase'].items():
                    history_text.insert(tk.END, f"    - {drink}: {details['reduced']} 瓶\n")
                history_text.insert(tk.END, "\n")
            
        except Exception as e:
            messagebox.showerror("错误", f"显示交易历史时出现错误: {str(e)}")
    
    def clear_data(self):
        """清空数据"""
        if messagebox.askyesno("确认", "确定要清空所有数据吗？"):
            self.before_image_path = ""
            self.after_image_path = ""
            self.before_path_var.set("")
            self.after_path_var.set("")
            self.result_text.delete(1.0, tk.END)
            self.image_canvas.delete("all")
            self.status_var.set("数据已清空")

def main():
    """主函数"""
    root = tk.Tk()
    app = VendingMachineGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 