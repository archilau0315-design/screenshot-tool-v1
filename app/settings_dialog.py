from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QFileDialog, QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QPixmap, QFont
import os
import shutil

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.settings = QSettings('ScreenshotTool', 'Settings')
        self.custom_icon_path = self.settings.value('custom_icon_path', '')
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('设置')
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()

        # 添加一个标题

        layout = QVBoxLayout()
        
        # 添加标题文本
        title_label = QLabel('Kustai@Archilau')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setItalic(True)  # 斜体
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: gray; text-decoration: underline; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 当前图标预览
        self.preview_label = QLabel('当前图标:')
        if self.parent and self.parent.custom_icon:
            self.preview_label.setPixmap(self.parent.custom_icon.scaled(64, 64))
        else:
            self.preview_label.setText('当前使用默认图标')
        layout.addWidget(self.preview_label)
        
        # 自定义图标按钮
        self.icon_btn = QPushButton('更换图标', self)
        self.icon_btn.clicked.connect(self.changeIcon)
        layout.addWidget(self.icon_btn)
        
        # 添加存储路径设置
        path_layout = QHBoxLayout()
        self.path_label = QLabel('存储路径:')
        self.path_edit = QLineEdit(self.settings.value('save_path', ''))
        self.path_btn = QPushButton('选择路径')
        self.path_btn.clicked.connect(self.choosePath)
        
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.path_btn)
        layout.addLayout(path_layout)
        
        # 保存设置按钮
        self.save_btn = QPushButton('保存设置', self)
        self.save_btn.clicked.connect(self.saveSettings)
        layout.addWidget(self.save_btn)
        
        # 退出程序按钮
        self.exit_btn = QPushButton('退出程序', self)
        self.exit_btn.clicked.connect(self.exitApp)
        layout.addWidget(self.exit_btn)
        
        self.setLayout(layout)
        
    def changeIcon(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择图标",
            "",
            "图片文件 (*.png)"
        )
        
        if file_name:
            pixmap = QPixmap(file_name)
            if pixmap.width() > 64 or pixmap.height() > 64:
                QMessageBox.warning(self, "警告", "图片尺寸必须小于64x64像素")
                return
            
            # 创建应用程序数据目录（如果不存在）
            app_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
            if not os.path.exists(app_data_dir):
                os.makedirs(app_data_dir)
            
            # 复制图标到应用程序数据目录
            icon_filename = os.path.basename(file_name)
            icon_path = os.path.join(app_data_dir, 'custom_icon.png')
            
            try:
                shutil.copy2(file_name, icon_path)
                self.custom_icon_path = icon_path
                
                # 更新父窗口的图标
                self.parent.custom_icon = pixmap
                self.preview_label.setPixmap(pixmap)
                self.parent.update()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"保存图标时出错: {str(e)}")
            
    def choosePath(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "选择保存路径",
            self.path_edit.text() or os.path.expanduser("~")
        )
        if path:
            self.path_edit.setText(path)
            
    def saveSettings(self):
        # 保存设置
        self.settings.setValue('save_path', self.path_edit.text())
        
        # 保存自定义图标路径
        if self.custom_icon_path:
            self.settings.setValue('custom_icon_path', self.custom_icon_path)
        
        QMessageBox.information(self, "提示", "设置已保存")
        
    def exitApp(self):
        reply = QMessageBox.question(
            self, 
            '确认', 
            '确定要退出程序吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.parent.close() 