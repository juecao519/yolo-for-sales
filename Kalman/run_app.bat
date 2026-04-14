@echo off
chcp 65001 >nul
echo 启动车辆速度检测应用...
echo.

REM 检查是否在虚拟环境中
if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 运行应用
python app.py

pause


