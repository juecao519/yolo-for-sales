#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLOv8 饮料检测训练脚本

"""

from ultralytics import YOLO
import os
import yaml

def quick_train():
    """
    快速训练函数 - 使用默认参数
    """
    print("🚀 YOLOv8 饮料检测快速训练")
    print("=" * 50)
    
    # 检查数据集配置
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
    
    # 使用YOLOv8n进行快速训练
    model_name = 'yolov8n.pt'
    print(f"\n📋 使用模型: {model_name}")
    
    # 加载模型
    try:
        model = YOLO(model_name)
        print(f"✅ 模型加载成功")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return
    
    # 快速训练参数
    print(f"\n⚙️ 快速训练参数 (CPU优化):")
    print(f"   - 训练轮数: 30")
    print(f"   - 批次大小: 4")
    print(f"   - 图片尺寸: 416")
    print(f"   - 早停耐心: 8")
    print(f"   - 设备: CPU")
    
    # 开始训练
    print(f"\n🔥 开始快速训练 (CPU模式)...")
    print("=" * 50)
    
    try:
        results = model.train(
            data=data_yaml_path,
            epochs=30,           # CPU训练减少轮数
            batch=4,             # CPU训练减小批次大小
            imgsz=416,           # CPU训练减小图片尺寸
            patience=8,          # 早停耐心值
            save=True,           # 保存模型
            save_period=5,       # 每5轮保存一次
            device='cpu',        # 强制使用CPU
            workers=2,           # CPU训练减少线程数
            project='drink_detection',  # 项目名称
            name='quick_train_cpu',  # 实验名称
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
        print("🎉 快速训练完成!")
        
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
                print(f"\n💾 模型已保存到: drink_detection/quick_train_cpu/weights/")
        except Exception as e:
            print(f"\n💾 模型已保存到: drink_detection/quick_train_cpu/weights/")
        
        # 快速验证
        print(f"\n🔍 开始验证...")
        try:
            val_results = model.val()
            print(f"✅ 验证完成!")
        except Exception as e:
            print(f"⚠️ 验证过程中出现错误: {e}")
            print(f"   但训练已完成，模型已保存")
        
        print(f"\n🎯 下一步:")
        print(f"1. 查看训练结果: drink_detection/quick_train_cpu/")
        print(f"2. 运行测试: python test_drink_detection.py")
        print(f"3. 如果效果满意，可以运行完整训练: python train_drink_detection.py")
        
    except Exception as e:
        print(f"❌ 训练过程中出现错误: {e}")
        return

def check_environment():
    """
    检查环境配置
    """
    print("🔍 检查环境配置...")
    
    # 检查必要的库
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"   - CUDA可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   - GPU数量: {torch.cuda.device_count()}")
            print(f"   - 当前GPU: {torch.cuda.get_device_name()}")
        else:
            print(f"   - 使用CPU训练模式")
            print(f"   - CPU核心数: {os.cpu_count()}")
    except ImportError:
        print("❌ PyTorch未安装")
        return False
    
    try:
        import ultralytics
        print(f"✅ Ultralytics: {ultralytics.__version__}")
    except ImportError:
        print("❌ Ultralytics未安装")
        return False
    
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV未安装")
        return False
    
    # 检查数据集
    if os.path.exists("dataset/data.yaml"):
        print("✅ 数据集配置文件存在")
    else:
        print("❌ 数据集配置文件不存在")
        return False
    
    if os.path.exists("dataset/images/train"):
        train_count = len([f for f in os.listdir("dataset/images/train") if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        print(f"✅ 训练图片: {train_count} 张")
    else:
        print("❌ 训练图片目录不存在")
        return False
    
    if os.path.exists("dataset/images/val"):
        val_count = len([f for f in os.listdir("dataset/images/val") if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        print(f"✅ 验证图片: {val_count} 张")
    else:
        print("❌ 验证图片目录不存在")
        return False
    
    return True

def main():
    """
    主函数
    """
    print("🍹 YOLOv8 饮料检测快速启动")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请检查依赖安装和数据集配置")
        return
    
    print("\n✅ 环境检查通过!")
    
    # 询问是否开始快速训练
    choice = input("\n是否开始快速训练? (y/n, 默认y): ").strip().lower()
    
    if choice in ['', 'y', 'yes']:
        quick_train()
    else:
        print("👋 已取消训练")

if __name__ == "__main__":
    main() 