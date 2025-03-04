import os
from pathlib import Path
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPen
from PyQt6.QtCore import Qt

def create_default_icon():
    """创建默认图标"""
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent.absolute()
    
    # 创建资源目录（如果不存在）
    resources_dir = current_dir / "app" / "resources"
    if not resources_dir.exists():
        resources_dir.mkdir(parents=True)
    
    # 创建图标文件
    icon_file = resources_dir / "icon.ico"
    
    # 创建一个64x64的图像
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(255, 192, 203))  # 粉色背景
    
    # 创建画笔
    painter = QPainter(pixmap)
    
    # 设置画笔
    pen = QPen(QColor(255, 255, 255), 2)  # 白色，2像素宽
    painter.setPen(pen)
    
    # 绘制一个简单的相机图标
    # 相机主体
    painter.drawRect(10, 15, 44, 34)
    
    # 相机镜头
    painter.drawEllipse(22, 25, 20, 20)
    painter.drawEllipse(27, 30, 10, 10)
    
    # 相机闪光灯
    painter.drawRect(45, 10, 8, 5)
    
    # 结束绘制
    painter.end()
    
    # 保存图标
    pixmap.save(str(icon_file))
    
    print(f"默认图标已创建: {icon_file}")

if __name__ == "__main__":
    create_default_icon() 