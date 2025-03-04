@echo off
chcp 65001 > nul
title 构建截图工具安装程序
echo 正在构建截图工具安装程序...

:: 设置Python路径
set PYTHON_PATH=python.exe

:: 检查Python是否安装
where %PYTHON_PATH% >nul 2>nul
if errorlevel 1 (
    echo Python未找到，请确保Python已正确安装并添加到系统PATH中
    pause
    exit /b 1
)

:: 运行打包脚本
cd /d %~dp0
%PYTHON_PATH% build_installer.py

:: 如果脚本异常退出，暂停显示错误信息
if errorlevel 1 (
    echo 构建过程出错，请查看上方错误信息
    pause
)

echo 构建完成！
pause 