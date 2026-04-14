#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLOv8 饮料检测测试

"""

from ultralytics import YOLO
import cv2
import os
import numpy as np
from pathlib import Path
import paho.mqtt.client as mqtt
import json
import threading
import time

def test_model(model_path, image_path=None):
    """
    测试训练好的模型
    
    Args:
        model_path:  best.pt
        image_path: E:\yolo\dataset\images\train\IMG_20230418_202021.jpg
    """
    print("🔍 开始饮料检测测试...")
    
    # 检查模型文件
    if not os.path.exists(model_path):
        print(f"❌ 错误: 找不到模型文件 {model_path}")
        return
    
    # 加载模型
    try:
        model = YOLO(model_path)
        print(f"✅ 模型加载成功: {model_path}")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return
    
    # 类别名称
    class_names = ['cola', 'pepsi', 'sprite', 'fanta', 'spring', 'ice', 'scream', 'milk', 'red', 'king']
    
    # 如果没有指定图片，使用验证集中的图片
    if image_path is None:
        val_images_dir = "dataset/images/val"
        if os.path.exists(val_images_dir):
            image_files = [f for f in os.listdir(val_images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if image_files:
                image_path = os.path.join(val_images_dir, image_files[0])
                print(f"📸 使用验证集图片: {image_files[0]}")
            else:
                print("❌ 验证集中没有找到图片文件")
                return
        else:
            print("❌ 找不到验证集图片目录")
            return
    
    # 检查图片文件
    if not os.path.exists(image_path):
        print(f"❌ 错误: 找不到图片文件 {image_path}")
        return
    
    print(f"📸 测试图片: {image_path}")
    
    # 执行推理
    try:
        results = model(image_path, conf=0.25, iou=0.45)
        print("✅ 推理完成!")
        
        # 处理结果
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                print(f"\n🎯 检测到 {len(boxes)} 个目标:")
                
                for i, box in enumerate(boxes):
                    # 获取坐标
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # 获取类别和置信度
                    cls = int(box.cls[0].cpu().numpy())
                    conf = float(box.conf[0].cpu().numpy())
                    
                    # 获取类别名称
                    class_name = class_names[cls] if cls < len(class_names) else f"class_{cls}"
                    
                    print(f"   {i+1}. {class_name} (置信度: {conf:.3f}) - 位置: ({x1:.1f}, {y1:.1f}, {x2:.1f}, {y2:.1f})")
            else:
                print("❌ 未检测到任何目标")
        
        # 保存结果图片
        output_dir = "test_results"
        os.makedirs(output_dir, exist_ok=True)
        
        # 绘制结果
        img = cv2.imread(image_path)
        if img is not None:
            for result in results:
                annotated_img = result.plot()
                output_path = os.path.join(output_dir, f"result_{Path(image_path).name}")
                cv2.imwrite(output_path, annotated_img)
                print(f"💾 结果图片已保存: {output_path}")
        
    except Exception as e:
        print(f"❌ 推理过程中出现错误: {e}")
        return

def batch_test(model_path, test_dir=None):
    """
    批量测试
    
    Args:
        model_path: 模型文件路径
        test_dir: 测试图片目录
    """
    print("🔍 开始批量测试...")
    
    # 检查模型文件
    if not os.path.exists(model_path):
        print(f"❌ 错误: 找不到模型文件 {model_path}")
        return
    
    # 加载模型
    try:
        model = YOLO(model_path)
        print(f"✅ 模型加载成功: {model_path}")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return
    
    # 如果没有指定测试目录，使用验证集
    if test_dir is None:
        test_dir = "dataset/images/val"
    
    if not os.path.exists(test_dir):
        print(f"❌ 错误: 找不到测试目录 {test_dir}")
        return
    
    # 获取所有图片文件
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    image_files = [f for f in os.listdir(test_dir) if f.lower().endswith(image_extensions)]
    
    if not image_files:
        print(f"❌ 在 {test_dir} 中没有找到图片文件")
        return
    
    print(f"📸 找到 {len(image_files)} 张测试图片")
    
    # 批量推理
    try:
        results = model(test_dir, conf=0.25, iou=0.45, save=True, project="batch_test", name="drink_detection")
        print("✅ 批量测试完成!")
        
        # 显示统计信息
        total_detections = 0
        for result in results:
            if result.boxes is not None:
                total_detections += len(result.boxes)
        
        print(f"📊 统计信息:")
        print(f"   - 测试图片数量: {len(image_files)}")
        print(f"   - 总检测目标数: {total_detections}")
        print(f"   - 平均每张图片检测数: {total_detections/len(image_files):.2f}")
        
        print(f"💾 结果保存在: batch_test/drink_detection/")
        
    except Exception as e:
        print(f"❌ 批量测试过程中出现错误: {e}")

def main():
    """
    主函数
    """
    print("🍹 YOLOv8 饮料检测测试工具")
    print("=" * 40)
    # 新增：让用户输入模型路径
    model_path = input("请输入模型文件路径（留空使用默认）: ").strip()
    if not model_path:
        best_model_path = "drink_detection/yolov8_drink_model/weights/best.pt"
        last_model_path = "drink_detection/yolov8_drink_model/weights/last.pt"
        if os.path.exists(best_model_path):
            model_path = best_model_path
            print(f"✅ 找到最佳模型: {model_path}")
        elif os.path.exists(last_model_path):
            model_path = last_model_path
            print(f"✅ 找到最新模型: {model_path}")
        else:
            print("❌ 未找到训练好的模型")
            print("请先运行训练脚本: python train_drink_detection.py")
            return
    else:
        print(f"✅ 使用自定义模型: {model_path}")

    print("\n📋 选择测试模式:")
    print("1. 单张图片测试")
    print("2. 批量测试")
    choice = input("请选择 (1-2, 默认1): ").strip()
    if choice == "2":
        test_dir = input("测试图片目录 (默认使用验证集): ").strip()
        if not test_dir:
            test_dir = None
        batch_test(model_path, test_dir)
    else:
        image_path = input("测试图片路径 (留空使用验证集第一张图片): ").strip()
        if not image_path:
            image_path = None
        test_model(model_path, image_path)

class VendingMachineIoTClient:
    def __init__(self, broker, port, client_id, on_command=None, username=None, password=None):
        self.client = mqtt.Client(client_id)
        if username and password:
            self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker, port, 60)
        self.on_command = on_command  # 回调函数
        self.running = False

    def on_connect(self, client, userdata, flags, rc):
        print("✅ [IoT] 已连接到MQTT Broker，返回码:", rc)
        client.subscribe("vending/command")  # 订阅云端指令主题

    def on_message(self, client, userdata, msg):
        print("📥 [IoT] 收到云端指令:", msg.topic, msg.payload.decode())
        try:
            command = json.loads(msg.payload.decode())
            if self.on_command:
                self.on_command(command)
        except Exception as e:
            print("❌ [IoT] 指令解析失败:", e)

    def publish_status(self, topic, data):
        payload = json.dumps(data, ensure_ascii=False)
        self.client.publish(topic, payload)
        print(f"📤 [IoT] 上报数据到 {topic}: {payload}")

    def start(self):
        self.running = True
        threading.Thread(target=self.client.loop_forever, daemon=True).start()

    def stop(self):
        self.running = False
        self.client.disconnect()

# 用法示例
if __name__ == "__main__":
    main() 