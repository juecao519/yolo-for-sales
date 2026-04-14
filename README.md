1.conda activate yoloenv
2.若没有，先 conda create -n yoloenv python=3.10，再 activate 并 pip install ultralytics torch torchvision opencv-python pillow ttkbootstrap paho-mqtt
检查依赖
pip list 或直接 python - <<'PY' 导入关键包确认无报错（ultralytics、torch、tkinter/PIL 等）
启动项目
训练模型（如需重新训练）
python train_drink_detection.py
按提示选择模型、轮数等；权重默认存到 drink_detection/.../best.pt
图形界面运行饮料机
python final.py
界面加载后可选择模型、开/关门图片，执行分析、支付、IoT 上报等功能
测试模型（命令行）
python test_drink_detection.py
