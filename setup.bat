@echo off
chcp 65001 > nul
title 截图工具 - 设置
color 0F
echo 正在配置截图工具...
echo.

:: 获取当前目录的完整路径
set CURRENT_PATH=%~dp0
set START_BAT=%CURRENT_PATH%start.bat

:: 询问是否创建桌面快捷方式
set /p CREATE_SHORTCUT="是否创建桌面快捷方式？(Y/N): "
if /i "%CREATE_SHORTCUT%"=="Y" (
    echo 正在创建桌面快捷方式...
    set SHORTCUT_PATH=%USERPROFILE%\Desktop\截图工具.lnk
    powershell "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%START_BAT%'; $s.WorkingDirectory = '%CURRENT_PATH%'; $s.Save()"
    echo 桌面快捷方式已创建
) else (
    echo 已跳过创建桌面快捷方式
)

:: 询问是否添加开机自启动
echo.
set /p AUTO_START="是否添加到开机自启动？(Y/N): "
if /i "%AUTO_START%"=="Y" (
    echo 正在添加开机自启动...
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "ScreenshotTool" /t REG_SZ /d "\"%START_BAT%\"" /f
    echo 已添加开机自启动
) else (
    echo 已跳过开机自启动设置
)

echo.
echo ========== 设置完成 ==========
if /i "%CREATE_SHORTCUT%"=="Y" echo √ 桌面快捷方式已创建
if /i "%AUTO_START%"=="Y" echo √ 开机自启动已设置
echo ============================
echo.
echo 按任意键退出...
pause > nul 