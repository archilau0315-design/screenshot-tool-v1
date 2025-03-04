@echo off
chcp 65001 > nul
title 创建图标
echo 正在创建图标...

:: 设置Python路径
set PYTHON_PATH=python.exe

:: 检查Python是否安装
where %PYTHON_PATH% >nul 2>nul
if errorlevel 1 (
    echo Python未找到，请确保Python已正确安装并添加到系统PATH中
    pause
    exit /b 1
)

:: 运行图标生成脚本
cd /d %~dp0
%PYTHON_PATH% create_icon.py

:: 如果脚本异常退出，暂停显示错误信息
if errorlevel 1 (
    echo 图标创建过程出错，请查看上方错误信息
    pause
)

echo 图标创建完成！
pause 