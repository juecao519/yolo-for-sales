#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLOv8 饮料检测训练脚本
用不着
"""

from ultralytics import YOLO
import os
import yaml
import torch
import shutil

def main():
    """
    主训练函数
    """
    print("🚀 开始YOLOv8饮料检测模型训练...")
    
    # 检查数据集配置文件
    data_yaml_path = "dataset/data.yaml"
    if not os.path.exists(data_yaml_path):
        print(f"❌ 错误: 找不到数据集配置文件 {data_yaml_path}")
        return
    
    # 验证配置文件
    try:
        with open(data_yaml_path, 'r', encoding='utf-8') as f:
            data_config = yaml.safe_load(f)
        print(f"✅ 数据集配置加载成功:")
        print(f"   - 类别数量: {data_config['nc']}")
        print(f"   - 类别名称: {data_config['names']}")
        print(f"   - 训练图片路径: {data_config['train']}")
        print(f"   - 验证图片路径: {data_config['val']}")
    except Exception as e:
        print(f"❌ 配置文件验证失败: {e}")
        return
    
    # 选择YOLOv8模型
    print("\n📋 选择训练模型:")
    print("1. YOLOv8n (最小，最快)")
    print("2. YOLOv8s (小)")
    print("3. YOLOv8m (中等)")
    print("4. YOLOv8l (大)")
    print("5. YOLOv8x (最大，最准确)")
    
    model_choice = input("请选择模型 (1-5, 默认1): ").strip()
    
    model_map = {
        '1': 'yolov8n.pt',
        '2': 'yolov8s.pt', 
        '3': 'yolov8m.pt',
        '4': 'yolov8l.pt',
        '5': 'yolov8x.pt'
    }
    
    model_name = model_map.get(model_choice, 'yolov8n.pt')
    print(f"✅ 选择模型: {model_name}")
    
    # 加载模型
    try:
        model = YOLO(model_name)
        print(f"✅ 模型加载成功: {model_name}")
        # 集成自定义损失函数
        from custom_loss import CustomDetectionLoss
        model.loss = CustomDetectionLoss(model.model)
        print("✅ 已集成自定义损失函数（CIoU+Focal Loss+类别加权）")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return
    
    # 训练参数配置
    print("\n⚙️ 配置训练参数...")
    
    # 检查是否有GPU
    has_gpu = torch.cuda.is_available()
    
    if has_gpu:
        print("✅ 检测到GPU，可以使用GPU训练")
        device_choice = input("使用GPU训练? (y/n, 默认y): ").strip().lower()
        use_gpu = device_choice not in ['n', 'no']
    else:
        print("ℹ️ 未检测到GPU，将使用CPU训练")
        use_gpu = False
    
    # 根据设备选择默认参数
    if use_gpu:
        default_batch = 16
        default_imgsz = 640
        default_epochs = 100
        device = 'auto'
    else:
        default_batch = 4
        default_imgsz = 416
        default_epochs = 50
        device = 'cpu'
        print("💡 CPU训练建议:")
        print("   - 使用较小的批次大小 (2-8)")
        print("   - 使用较小的图片尺寸 (320-416)")
        print("   - 减少训练轮数 (30-100)")
    
    # 获取训练轮数
    epochs = input(f"训练轮数 (默认{default_epochs}): ").strip()
    epochs = int(epochs) if epochs.isdigit() else default_epochs
    
    # 获取批次大小
    batch_size = input(f"批次大小 (默认{default_batch}): ").strip()
    batch_size = int(batch_size) if batch_size.isdigit() else default_batch
    
    # 获取图片尺寸
    imgsz = input(f"图片尺寸 (默认{default_imgsz}): ").strip()
    imgsz = int(imgsz) if imgsz.isdigit() else default_imgsz
    
    print(f"✅ 训练参数:")
    print(f"   - 训练轮数: {epochs}")
    print(f"   - 批次大小: {batch_size}")
    print(f"   - 图片尺寸: {imgsz}")
    print(f"   - 设备: {'GPU' if use_gpu else 'CPU'}")
    
    # 开始训练
    print(f"\n🔥 开始训练...")
    print("=" * 50)
    
    try:
        # 执行训练
        results = model.train(
            data=data_yaml_path,
            epochs=epochs,
            batch=batch_size,
            imgsz=imgsz,
            patience=20,  # 早停耐心值
            save=True,    # 保存模型
            save_period=10,  # 每10轮保存一次
            device=device,   # 根据选择设置设备
            workers=2 if not use_gpu else 4,  # CPU训练减少线程数
            project='drink_detection',  # 项目名称
            name='yolov8_drink_model',  # 实验名称
            exist_ok=True,   # 覆盖已存在的实验
            pretrained=True, # 使用预训练权重
            optimizer='auto', # 自动选择优化器
            verbose=True,    # 详细输出
            seed=42,         # 随机种子
            deterministic=True,  # 确定性训练
            single_cls=False,    # 多类别
            rect=False,          # 矩形训练
            cos_lr=False,        # 余弦学习率调度
            close_mosaic=10,     # 最后10轮关闭mosaic
            resume=False,        # 不恢复训练
            amp=use_gpu,        # 只有GPU才使用混合精度
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
            half=use_gpu,       # 只有GPU才使用半精度
            dnn=False,          # 不使用DNN
        )
        
        print("=" * 50)
        print("🎉 训练完成!")
        
        # 显示训练结果
        print(f"\n📊 训练结果:")
        try:
            # 尝试获取训练结果
            if hasattr(results, 'results_dict'):
                print(f"   - 最佳mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")
                print(f"   - 最佳mAP50-95: {results.results_dict.get('metrics/mAP50-95(B)', 'N/A')}")
                print(f"   - 训练轮数: {results.results_dict.get('train/epoch', 'N/A')}")
            else:
                print("   - 训练完成，详细结果请查看生成的图表")
        except Exception as e:
            print("   - 训练完成，详细结果请查看生成的图表")
        
        # 模型保存路径
        try:
            if hasattr(results, 'save_dir'):
                best_model_path = results.save_dir / 'weights' / 'best.pt'
                last_model_path = results.save_dir / 'weights' / 'last.pt'
                
                print(f"\n💾 模型已保存:")
                print(f"   - 最佳模型: {best_model_path}")
                print(f"   - 最新模型: {last_model_path}")
            else:
                print(f"\n💾 模型已保存到: drink_detection/yolov8_drink_model/weights/")
        except Exception as e:
            print(f"\n💾 模型已保存到: drink_detection/yolov8_drink_model/weights/")
        
        # 验证模型
        print(f"\n🔍 开始验证...")
        try:
            val_results = model.val()
            print(f"✅ 验证完成!")
        except Exception as e:
            print(f"⚠️ 验证过程中出现错误: {e}")
            print(f"   但训练已完成，模型已保存")

        # === 新增：保存compare.pt ===
        try:
            if hasattr(results, 'save_dir'):
                best_model_path = results.save_dir / 'weights' / 'best.pt'
                compare_model_path = results.save_dir / 'weights' / 'compare.pt'
                shutil.copy(str(best_model_path), str(compare_model_path))
                print(f"✅ 已额外保存模型为: {compare_model_path}")
        except Exception as e:
            print(f"⚠️ compare.pt保存失败: {e}")
        
    except Exception as e:
        print(f"❌ 训练过程中出现错误: {e}")
        return
    
    print("\n🎯 下一步建议:")
    print("1. 查看训练结果图表: drink_detection/yolov8_drink_model/")
    print("2. 使用最佳模型进行推理测试")
    print("3. 如果效果不理想，可以调整超参数重新训练")
    print("4. 考虑数据增强或收集更多数据")

if __name__ == "__main__":
    main() 