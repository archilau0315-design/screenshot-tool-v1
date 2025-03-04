import sys
import os
from PyQt6.QtWidgets import QApplication
from app.floating_icon import FloatingIcon

def ensure_app_directories():
    """确保应用程序所需的目录存在"""
    # 创建数据目录
    app_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)

def main():
    # 确保应用程序目录存在
    ensure_app_directories()
    
    app = QApplication(sys.argv)
    
    # 创建悬浮图标
    floating_icon = FloatingIcon()
    floating_icon.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 