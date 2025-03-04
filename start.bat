@echo off
chcp 65001 > nul
title 截图工具
echo 正在启动截图工具...

:: 设置Python路径
set PYTHON_PATH=python.exe

:: 检查Python是否安装
where %PYTHON_PATH% >nul 2>nul
if errorlevel 1 (
    echo Python未找到，请确保Python已正确安装并添加到系统PATH中
    pause
    exit /b 1
)

:: 设置环境变量
set QT_AUTO_SCREEN_SCALE_FACTOR=1
set QT_ENABLE_HIGHDPI_SCALING=1
set PYTHONPATH=%~dp0

:: 检查并安装所有依赖
echo 正在检查并安装依赖...

:: 先升级 pip
%PYTHON_PATH% -m pip install --upgrade pip

:: 安装 wheel 和编译工具
%PYTHON_PATH% -m pip install --upgrade wheel setuptools

:: 分步安装依赖，使用预编译的wheel包
echo 安装 PyQt6 相关包...
%PYTHON_PATH% -m pip install --no-cache-dir --only-binary :all: PyQt6==6.6.1
%PYTHON_PATH% -m pip install --no-cache-dir --only-binary :all: PyQt6-Qt6==6.6.1
%PYTHON_PATH% -m pip install --no-cache-dir --only-binary :all: PyQt6-sip==13.10.0

echo 安装 Pillow...
%PYTHON_PATH% -m pip install --no-cache-dir --only-binary :all: Pillow==11.1.0

echo 安装 pyperclip...
%PYTHON_PATH% -m pip install --no-cache-dir pyperclip==1.8.2

:: 清理 Python 缓存文件
echo 清理缓存文件...
del /s /q *.pyc >nul 2>&1
rd /s /q __pycache__ 2>nul

:: 启动程序
echo 启动程序...
cd /d %~dp0
%PYTHON_PATH% -B main.py

:: 如果程序异常退出，暂停显示错误信息
if errorlevel 1 (
    echo 程序异常退出，请查看上方错误信息
    pause
)