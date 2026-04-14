#!/bin/bash

echo "启动车辆速度检测应用..."
echo ""

# 检查是否在虚拟环境中
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 运行应用
python app.py


