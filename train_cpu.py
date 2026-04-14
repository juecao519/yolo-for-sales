#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLOv8 饮料检测 CPU训练脚本
CPU环境优化的训练脚本
"""

from ultralytics import YOLO
import os
import yaml
import torch

def main():
    """
    CPU训练主函数
    """
    print("🚀 YOLOv8 饮料检测 CPU训练")
    print("=" * 50)
    
    # 检查GPU
    if torch.cuda.is_available():
        print("⚠️ 检测到GPU，但将使用CPU训练")
        print("   如需使用GPU，请运行: python train_drink_detection.py")
    else:
        print("✅ 使用CPU训练模式")
    
    print(f"💻 CPU核心数: {os.cpu_count()}")
    
    # 检查数据集配置文件
    data_yaml_path = "dataset/data.yaml"
    if not os.path.exists(data_yaml_path):
        print(f"❌ 错误: 找不到数据集配置文件 {data_yaml_path}")
        return
    
    # 验证配置文件
    try:
        with open(data_yaml_path, 'r', encoding='utf-8') as f:
            data_config = yaml.safe_load(f)
        print(f"✅ 数据集配置验证成功:")
        print(f"   - 类别数量: {data_config['nc']}")
        print(f"   - 类别名称: {data_config['names']}")
    except Exception as e:
        print(f"❌ 配置文件验证失败: {e}")
        return
    
    # 选择模型
    print("\n📋 选择训练模型 (CPU优化):")
    print("1. YOLOv8n (最小，最快，推荐)")
    print("2. YOLOv8s (小)")
    print("3. YOLOv8m (中等，较慢)")
    
    model_choice = input("请选择模型 (1-3, 默认1): ").strip()
    
    model_map = {
        '1': 'yolov8n.pt',
        '2': 'yolov8s.pt', 
        '3': 'yolov8m.pt'
    }
    
    model_name = model_map.get(model_choice, 'yolov8n.pt')
    print(f"✅ 选择模型: {model_name}")
    
    # 加载模型
    try:
        model = YOLO(model_name)
        print(f"✅ 模型加载成功")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return
    
    # CPU训练参数配置
    print(f"\n⚙️ CPU训练参数配置:")
    print(f"💡 CPU训练建议:")
    print(f"   - 批次大小: 2-8 (根据内存调整)")
    print(f"   - 图片尺寸: 320-416 (越小越快)")
    print(f"   - 训练轮数: 30-100 (根据时间调整)")
    
    # 获取训练轮数
    epochs = input("训练轮数 (默认50): ").strip()
    epochs = int(epochs) if epochs.isdigit() else 50
    
    # 获取批次大小
    batch_size = input("批次大小 (默认4): ").strip()
    batch_size = int(batch_size) if batch_size.isdigit() else 4
    
    # 获取图片尺寸
    imgsz = input("图片尺寸 (默认416): ").strip()
    imgsz = int(imgsz) if imgsz.isdigit() else 416
    
    print(f"✅ 训练参数:")
    print(f"   - 训练轮数: {epochs}")
    print(f"   - 批次大小: {batch_size}")
    print(f"   - 图片尺寸: {imgsz}")
    print(f"   - 设备: CPU")
    
    # 估算训练时间
    estimated_time = epochs * batch_size * 0.5  # 粗略估算，每轮每批次约0.5秒
    print(f"⏱️ 预估训练时间: {estimated_time/60:.1f} 分钟")
    
    # 开始训练
    print(f"\n🔥 开始CPU训练...")
    print("=" * 50)
    print("💡 提示: CPU训练较慢，请耐心等待")
    print("   可以随时按 Ctrl+C 停止训练")
    print("=" * 50)
    
    try:
        # 执行训练
        results = model.train(
            data=data_yaml_path,
            epochs=epochs,
            batch=batch_size,
            imgsz=imgsz,
            patience=15,         # 早停耐心值
            save=True,           # 保存模型
            save_period=5,       # 每5轮保存一次
            device='cpu',        # 强制使用CPU
            workers=2,           # CPU训练减少线程数
            project='drink_detection',  # 项目名称
            name='cpu_training', # 实验名称
            exist_ok=True,       # 覆盖已存在的实验
            pretrained=True,     # 使用预训练权重
            optimizer='auto',    # 自动选择优化器
            verbose=True,        # 详细输出
            seed=42,             # 随机种子
            deterministic=True,  # 确定性训练
            single_cls=False,    # 多类别
            rect=False,          # 矩形训练
            cos_lr=False,        # 余弦学习率调度
            close_mosaic=5,      # 最后5轮关闭mosaic
            resume=False,        # 不恢复训练
            amp=False,          # CPU训练关闭混合精度
            fraction=1.0,       # 使用全部数据
            cache=False,        # 不缓存图片
            overlap_mask=True,  # 重叠mask
            mask_ratio=4,       # mask比例
            dropout=0.0,        # dropout率
            val=True,           # 验证
            plots=True,         # 生成训练图表
            save_json=False,    # 不保存JSON结果
            save_hybrid=False,  # 不保存混合结果
            conf=0.001,         # 置信度阈值
            iou=0.6,            # NMS IoU阈值
            max_det=300,        # 最大检测数
            half=False,         # CPU训练关闭半精度
            dnn=False,          # 不使用DNN
        )
        
        print("=" * 50)
        print("🎉 CPU训练完成!")
        
        # 显示训练结果
        print(f"\n📊 训练结果:")
        print(f"   - 最佳mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")
        print(f"   - 最佳mAP50-95: {results.results_dict.get('metrics/mAP50-95(B)', 'N/A')}")
        print(f"   - 训练轮数: {results.results_dict.get('train/epoch', 'N/A')}")
        
        # 模型保存路径
        best_model_path = results.save_dir / 'weights' / 'best.pt'
        last_model_path = results.save_dir / 'weights' / 'last.pt'
        
        print(f"\n💾 模型已保存:")
        print(f"   - 最佳模型: {best_model_path}")
        print(f"   - 最新模型: {last_model_path}")
        
        # 快速验证
        print(f"\n🔍 开始验证...")
        val_results = model.val()
        print(f"✅ 验证完成!")
        
        print(f"\n🎯 下一步:")
        print(f"1. 查看训练结果: drink_detection/cpu_training/")
        print(f"2. 运行测试: python test_drink_detection.py")
        print(f"3. 如果效果满意，可以增加训练轮数重新训练")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ 训练被用户中断")
        print(f"💾 已保存的模型可以在 drink_detection/cpu_training/weights/ 中找到")
    except Exception as e:
        print(f"❌ 训练过程中出现错误: {e}")
        return

if __name__ == "__main__":
    main() 