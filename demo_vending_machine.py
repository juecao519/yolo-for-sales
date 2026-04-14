#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能饮料贩卖机演示
窗口化前的 页面
"""

from smart_vending_machine import SmartVendingMachine
import os

def demo_vending_machine():
    """
    演示智能贩卖机功能
    """
    print("🤖 智能饮料贩卖机演示")
    print("=" * 50)
    
    # 使用你的模型
    model_path = "drink_detection/quick_train_cpu/weights/best.pt"
    
    if not os.path.exists(model_path):
        print(f"❌ 模型文件不存在: {model_path}")
        print("请先训练模型或修改模型路径")
        return
    
    # 创建智能贩卖机实例
    try:
        vending_machine = SmartVendingMachine(model_path)
        print("✅ 智能贩卖机初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 演示流程
    print("\n📋 演示流程:")
    print("1. 记录开门前状态（贩卖机装满饮料）")
    print("2. 记录关门后状态（顾客购买后）")
    print("3. 自动计算购买情况和价格")
    
    # 步骤1：记录开门前状态
    print("\n" + "="*50)
    print("步骤1: 记录开门前状态")
    print("="*50)
    
    before_image = input("请输入开门前图片路径（贩卖机装满饮料的图片）: ").strip()
    if before_image and os.path.exists(before_image):
        vending_machine.record_before_state(before_image)
    else:
        print("❌ 图片文件不存在，使用示例图片")
        # 这里可以设置一个默认的示例图片
        return
    
    # 步骤2：记录关门后状态
    print("\n" + "="*50)
    print("步骤2: 记录关门后状态")
    print("="*50)
    
    after_image = input("请输入关门后图片路径（顾客购买后的图片）: ").strip()
    if after_image and os.path.exists(after_image):
        vending_machine.record_after_state(after_image)
    else:
        print("❌ 图片文件不存在")
        return
    
    # 步骤3：计算购买情况
    print("\n" + "="*50)
    print("步骤3: 计算购买情况")
    print("="*50)
    
    purchase = vending_machine.calculate_purchase()
    if purchase:
        vending_machine.generate_bill(purchase)
        vending_machine.save_transaction_history()
        
        print("\n🎉 演示完成！")
        print("💡 功能特点:")
        print("   - 自动检测饮料种类和数量")
        print("   - 智能计算购买差异")
        print("   - 自动生成账单")
        print("   - 保存交易历史")
        print("   - 支持多种饮料价格配置")
    else:
        print("❌ 没有检测到购买行为")

def batch_demo():
    """
    批量演示 - 使用多组图片
    """
    print("🤖 智能饮料贩卖机批量演示")
    print("=" * 50)
    
    model_path = "drink_detection/quick_train_cpu/weights/best.pt"
    
    if not os.path.exists(model_path):
        print(f"❌ 模型文件不存在: {model_path}")
        return
    
    try:
        vending_machine = SmartVendingMachine(model_path)
        print("✅ 智能贩卖机初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 获取图片对
    image_pairs = []
    while True:
        print(f"\n📸 输入第 {len(image_pairs)+1} 组图片:")
        before_img = input("开门前图片路径 (留空结束): ").strip()
        if not before_img:
            break
        
        after_img = input("关门后图片路径: ").strip()
        if before_img and after_img and os.path.exists(before_img) and os.path.exists(after_img):
            image_pairs.append((before_img, after_img))
        else:
            print("❌ 图片文件不存在，跳过")
    
    if not image_pairs:
        print("❌ 没有有效的图片对")
        return
    
    # 批量处理
    print(f"\n🔄 开始处理 {len(image_pairs)} 组图片...")
    
    for i, (before_img, after_img) in enumerate(image_pairs, 1):
        print(f"\n" + "="*50)
        print(f"处理第 {i} 组图片")
        print("="*50)
        
        # 记录开门前状态
        vending_machine.record_before_state(before_img, save_result=False)
        
        # 记录关门后状态
        vending_machine.record_after_state(after_img, save_result=False)
        
        # 计算购买情况
        purchase = vending_machine.calculate_purchase()
        if purchase:
            vending_machine.generate_bill(purchase)
        
        print("-" * 30)
    
    # 保存所有交易历史
    vending_machine.save_transaction_history()
    print(f"\n💾 所有交易记录已保存")
    
    # 显示交易历史
    vending_machine.show_transaction_history(len(image_pairs))

def main():
    """
    主函数
    """
    print("🤖 智能饮料贩卖机系统")
    print("=" * 50)
    print("选择演示模式:")
    print("1. 单次演示")
    print("2. 批量演示")
    print("3. 退出")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        demo_vending_machine()
    elif choice == "2":
        batch_demo()
    elif choice == "3":
        print("👋 再见！")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main() 