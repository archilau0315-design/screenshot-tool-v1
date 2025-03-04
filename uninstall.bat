@echo off
title 截图工具 - 卸载
echo 正在卸载截图工具...

:: 删除桌面快捷方式
echo 正在删除桌面快捷方式...
set SHORTCUT_PATH=%USERPROFILE%\Desktop\截图工具.lnk
if exist "%SHORTCUT_PATH%" (
    del /f /q "%SHORTCUT_PATH%"
    echo 桌面快捷方式已删除
) else (
    echo 未找到桌面快捷方式
)

:: 删除开机自启动
echo 正在删除开机自启动...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "ScreenshotTool" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo 开机自启动已删除
) else (
    echo 未找到开机自启动项
)

:: 询问是否删除程序文件
echo.
set /p DELETE_FILES="是否删除程序文件？(Y/N): "
if /i "%DELETE_FILES%"=="Y" (
    echo 正在删除程序文件...
    cd ..
    rmdir /s /q "%~dp0"
    echo 程序文件已删除
) else (
    echo 已保留程序文件
    echo.
    echo 按任意键退出...
    pause > nul
)