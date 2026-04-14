#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能饮料贩卖机系统
基于YOLOv8的饮料检测和数量统计
废弃，训练模型而已
"""

from ultralytics import YOLO
import cv2
import os
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import time

class SmartVendingMachine:
    def __init__(self, model_path, price_config=None):
        """
        初始化智能饮料贩卖机
        
        Args:
            model_path: YOLOv8模型路径
            price_config: 价格配置字典
        """
        self.model_path = model_path
        self.model = None
        self.class_names = ['cola', 'pepsi', 'sprite', 'fanta', 'spring', 'ice', 'scream', 'milk', 'red', 'king']
        
        # 默认价格配置（元/瓶）
        self.price_config = price_config or {
            'cola': 3.0,      # 可口可乐
            'pepsi': 3.0,     # 百事可乐
            'sprite': 3.0,    # 雪碧
            'fanta': 3.0,     # 芬达
            'spring': 2.0,    # 矿泉水
            'ice': 3.5,       # 冰红茶
            'scream': 4.0,    # 尖叫
            'milk': 4.5,      # 旺仔牛奶
            'red': 6.0,       # 红牛
            'king': 4.0       # 王老吉
        }
        
        # 状态变量
        self.before_count = {}  # 开门前的饮料数量
        self.after_count = {}   # 关门后的饮料数量
        self.transaction_history = []  # 交易历史
        
        # 加载模型
        self.load_model()
    
    def load_model(self):
        """加载YOLOv8模型"""
        try:
            self.model = YOLO(self.model_path)
            print(f"✅ 模型加载成功: {self.model_path}")
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            raise
    
    def detect_drinks(self, image_path, conf_threshold=0.25):
        """
        检测图片中的饮料
        
        Args:
            image_path: 图片路径
            conf_threshold: 置信度阈值
            
        Returns:
            dict: 饮料类别及其数量
        """
        if not os.path.exists(image_path):
            print(f"❌ 错误: 找不到图片文件 {image_path}")
            return {}
        
        try:
            # 执行推理
            results = self.model(image_path, conf=conf_threshold, iou=0.45)
            
            # 统计各类饮料数量
            drink_count = {}
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # 获取类别
                        cls = int(box.cls[0].cpu().numpy())
                        class_name = self.class_names[cls] if cls < len(self.class_names) else f"class_{cls}"
                        
                        # 统计数量
                        drink_count[class_name] = drink_count.get(class_name, 0) + 1
            
            return drink_count
            
        except Exception as e:
            print(f"❌ 检测过程中出现错误: {e}")
            return {}
    
    def save_detection_result(self, image_path, drink_count, save_dir="detection_results"):
        """
        保存检测结果图片
        
        Args:
            image_path: 原始图片路径
            drink_count: 检测结果
            save_dir: 保存目录
        """
        try:
            os.makedirs(save_dir, exist_ok=True)
            
            # 执行推理并保存结果图片
            results = self.model(image_path, conf=0.25, iou=0.45)
            
            # 保存标注后的图片
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(save_dir, f"detection_{timestamp}_{Path(image_path).name}")
            
            for result in results:
                annotated_img = result.plot()
                cv2.imwrite(output_path, annotated_img)
                print(f"💾 检测结果图片已保存: {output_path}")
            
            # 保存检测数据
            data_path = os.path.join(save_dir, f"detection_data_{timestamp}.json")
            detection_data = {
                'timestamp': timestamp,
                'image_path': image_path,
                'drink_count': drink_count,
                'total_drinks': sum(drink_count.values())
            }
            
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(detection_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 检测数据已保存: {data_path}")
            
        except Exception as e:
            print(f"⚠️ 保存检测结果时出现错误: {e}")
    
    def record_before_state(self, image_path, save_result=True):
        """
        记录开门前的状态
        
        Args:
            image_path: 开门前的图片路径
            save_result: 是否保存检测结果
        """
        print("📸 记录开门前状态...")
        
        # 检测饮料
        self.before_count = self.detect_drinks(image_path)
        
        if save_result:
            self.save_detection_result(image_path, self.before_count, "before_state")
        
        print("📊 开门前饮料统计:")
        for drink, count in self.before_count.items():
            print(f"   - {drink}: {count} 瓶")
        
        print(f"   总计: {sum(self.before_count.values())} 瓶")
    
    def record_after_state(self, image_path, save_result=True):
        """
        记录关门后的状态
        
        Args:
            image_path: 关门后的图片路径
            save_result: 是否保存检测结果
        """
        print("📸 记录关门后状态...")
        
        # 检测饮料
        self.after_count = self.detect_drinks(image_path)
        
        if save_result:
            self.save_detection_result(image_path, self.after_count, "after_state")
        
        print("📊 关门后饮料统计:")
        for drink, count in self.after_count.items():
            print(f"   - {drink}: {count} 瓶")
        
        print(f"   总计: {sum(self.after_count.values())} 瓶")
    
    def calculate_purchase(self):
        """
        计算购买情况
        
        Returns:
            dict: 购买详情
        """
        if not self.before_count or not self.after_count:
            print("❌ 错误: 需要先记录开门前和关门后的状态")
            return {}
        
        purchase = {}
        total_amount = 0.0
        
        print("\n🛒 购买分析:")
        print("=" * 40)
        
        # 计算每种饮料的减少数量
        for drink in set(self.before_count.keys()) | set(self.after_count.keys()):
            before_num = self.before_count.get(drink, 0)
            after_num = self.after_count.get(drink, 0)
            reduced = before_num - after_num
            
            if reduced > 0:
                price = self.price_config.get(drink, 0)
                amount = reduced * price
                total_amount += amount
                
                purchase[drink] = {
                    'reduced': reduced,
                    'price_per_unit': price,
                    'total_price': amount
                }
                
                print(f"   - {drink}: 减少 {reduced} 瓶 × ¥{price:.1f} = ¥{amount:.1f}")
        
        if purchase:
            print("=" * 40)
            print(f"💰 总消费: ¥{total_amount:.1f}")
            
            # 记录交易历史
            transaction = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'purchase': purchase,
                'total_amount': total_amount
            }
            self.transaction_history.append(transaction)
            
            return purchase
        else:
            print("   - 没有检测到购买行为")
            return {}
    
    def generate_bill(self, purchase):
        """
        生成账单
        
        Args:
            purchase: 购买详情
        """
        if not purchase:
            return
        
        print("\n🧾 智能贩卖机账单")
        print("=" * 50)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        total_amount = 0.0
        for drink, details in purchase.items():
            print(f"{drink:12} {details['reduced']:2d} 瓶 × ¥{details['price_per_unit']:4.1f} = ¥{details['total_price']:6.1f}")
            total_amount += details['total_price']
        
        print("=" * 50)
        print(f"{'总计':12} {'':2} {'':4} {'':6} ¥{total_amount:6.1f}")
        print("=" * 50)
        print("感谢使用智能贩卖机！")
    
    def save_transaction_history(self, filename="transaction_history.json"):
        """保存交易历史"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.transaction_history, f, ensure_ascii=False, indent=2)
            print(f"💾 交易历史已保存: {filename}")
        except Exception as e:
            print(f"⚠️ 保存交易历史时出现错误: {e}")
    
    def load_transaction_history(self, filename="transaction_history.json"):
        """加载交易历史"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    self.transaction_history = json.load(f)
                print(f"📂 已加载 {len(self.transaction_history)} 条交易记录")
        except Exception as e:
            print(f"⚠️ 加载交易历史时出现错误: {e}")
    
    def show_transaction_history(self, limit=10):
        """显示交易历史"""
        if not self.transaction_history:
            print("📂 暂无交易记录")
            return
        
        print(f"\n📂 最近 {min(limit, len(self.transaction_history))} 条交易记录:")
        print("=" * 60)
        
        for i, transaction in enumerate(self.transaction_history[-limit:]):
            print(f"{i+1}. {transaction['timestamp']} - ¥{transaction['total_amount']:.1f}")
            for drink, details in transaction['purchase'].items():
                print(f"    - {drink}: {details['reduced']} 瓶")
            print()

def main():
    """
    主函数 - 智能贩卖机演示
    """
    print("🤖 智能饮料贩卖机系统")
    print("=" * 50)
    
    # 获取模型路径
    model_path = input("请输入模型权重路径: ").strip()
    if not model_path:
        print("❌ 请输入模型路径")
        return
    
    if not os.path.exists(model_path):
        print(f"❌ 模型文件不存在: {model_path}")
        return
    
    # 创建智能贩卖机实例
    try:
        vending_machine = SmartVendingMachine(model_path)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 加载交易历史
    vending_machine.load_transaction_history()
    
    while True:
        print("\n📋 智能贩卖机菜单:")
        print("1. 记录开门前状态")
        print("2. 记录关门后状态")
        print("3. 计算购买情况")
        print("4. 查看交易历史")
        print("5. 退出")
        
        choice = input("\n请选择操作 (1-5): ").strip()
        
        if choice == "1":
            # 记录开门前状态
            image_path = input("请输入开门前图片路径: ").strip()
            if image_path and os.path.exists(image_path):
                vending_machine.record_before_state(image_path)
            else:
                print("❌ 图片文件不存在")
        
        elif choice == "2":
            # 记录关门后状态
            image_path = input("请输入关门后图片路径: ").strip()
            if image_path and os.path.exists(image_path):
                vending_machine.record_after_state(image_path)
            else:
                print("❌ 图片文件不存在")
        
        elif choice == "3":
            # 计算购买情况
            purchase = vending_machine.calculate_purchase()
            if purchase:
                vending_machine.generate_bill(purchase)
                vending_machine.save_transaction_history()
        
        elif choice == "4":
            # 查看交易历史
            limit = input("显示最近几条记录 (默认10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            vending_machine.show_transaction_history(limit)
        
        elif choice == "5":
            print("👋 感谢使用智能贩卖机系统！")
            break
        
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main() 