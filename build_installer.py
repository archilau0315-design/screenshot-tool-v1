import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_requirements():
    """检查是否安装了必要的依赖"""
    try:
        import PyInstaller
        print("PyInstaller 已安装")
    except ImportError:
        print("正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    try:
        import innosetup
        print("innosetup 已安装")
    except ImportError:
        print("正在安装 innosetup...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "innosetup"])

def create_icon():
    """创建图标文件"""
    print("正在检查图标文件...")
    
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent.absolute()
    
    # 检查图标文件是否存在
    icon_file = current_dir / "app" / "resources" / "icon.ico"
    if not icon_file.exists():
        print("图标文件不存在，正在创建...")
        
        # 运行图标创建脚本
        icon_script = current_dir / "create_icon.py"
        if icon_script.exists():
            subprocess.check_call([sys.executable, str(icon_script)])
        else:
            print("图标创建脚本不存在，将使用默认图标")
            
            # 创建资源目录（如果不存在）
            resources_dir = current_dir / "app" / "resources"
            if not resources_dir.exists():
                resources_dir.mkdir(parents=True)
            
            # 创建一个默认图标
            from PyQt6.QtGui import QPixmap, QColor
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor(255, 192, 203))  # 粉色
            pixmap.save(str(icon_file))

def build_executable():
    """使用 PyInstaller 构建可执行文件"""
    print("正在构建可执行文件...")
    
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent.absolute()
    
    # 创建 dist 目录（如果不存在）
    dist_dir = current_dir / "dist"
    if not dist_dir.exists():
        dist_dir.mkdir()
    
    # 创建 build 目录（如果不存在）
    build_dir = current_dir / "build"
    if not build_dir.exists():
        build_dir.mkdir()
    
    # 确保图标文件存在
    icon_file = current_dir / "app" / "resources" / "icon.ico"
    
    # 构建命令
    pyinstaller_cmd = [
        "pyinstaller",
        "--name=截图工具",
        "--windowed",
        "--onedir",
        "--clean",
        f"--icon={icon_file}",
        "--add-data=app/resources;app/resources",
        "--distpath=" + str(dist_dir),
        "--workpath=" + str(build_dir),
        "main.py"
    ]
    
    # 执行构建命令
    subprocess.check_call(pyinstaller_cmd, cwd=current_dir)
    
    # 复制必要的文件到 dist 目录
    data_dir = dist_dir / "截图工具" / "data"
    if not data_dir.exists():
        data_dir.mkdir()
    
    print("可执行文件构建完成！")
    return dist_dir / "截图工具"

def create_installer(app_dir):
    """使用 Inno Setup 创建安装程序"""
    print("正在创建安装程序...")
    
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent.absolute()
    
    # 创建 Inno Setup 脚本
    iss_file = current_dir / "installer.iss"
    
    # 图标文件路径
    icon_file = current_dir / "app" / "resources" / "icon.ico"
    
    # 写入 Inno Setup 脚本内容
    with open(iss_file, "w", encoding="utf-8") as f:
        f.write(f"""
[Setup]
AppName=截图工具
AppVersion=1.0
DefaultDirName={{pf}}\\截图工具
DefaultGroupName=截图工具
OutputDir={current_dir}\\output
OutputBaseFilename=截图工具安装程序
Compression=lzma
SolidCompression=yes
SetupIconFile={icon_file}

[Files]
Source: "{app_dir}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\截图工具"; Filename: "{{app}}\\截图工具.exe"
Name: "{{commondesktop}}\\截图工具"; Filename: "{{app}}\\截图工具.exe"

[Run]
Filename: "{{app}}\\截图工具.exe"; Description: "立即运行截图工具"; Flags: nowait postinstall skipifsilent
        """)
    
    # 导入 innosetup 模块
    import innosetup
    
    # 创建输出目录
    output_dir = current_dir / "output"
    if not output_dir.exists():
        output_dir.mkdir()
    
    # 编译 Inno Setup 脚本
    innosetup.compile(str(iss_file))
    
    print(f"安装程序已创建！位置: {output_dir}\\截图工具安装程序.exe")

def main():
    """主函数"""
    print("开始打包截图工具...")
    
    # 检查依赖
    check_requirements()
    
    # 创建图标
    create_icon()
    
    # 构建可执行文件
    app_dir = build_executable()
    
    # 创建安装程序
    create_installer(app_dir)
    
    print("打包完成！")

if __name__ == "__main__":
    main() 