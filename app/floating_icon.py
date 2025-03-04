from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtCore import Qt, QPoint, QTimer, QSettings
from PyQt6.QtGui import QPainter, QColor, QIcon, QPixmap
from .settings_dialog import SettingsDialog
from .screenshot import ScreenshotTool
from .cursor_rules import CursorRules
import os

class FloatingIcon(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('ScreenshotTool', 'Settings')
        self.initUI()
        
    def initUI(self):
        # 设置窗口无边框且始终置顶
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 设置默认大小
        self.setFixedSize(64, 64)
        
        # 初始化默认图标（粉色方块）
        self.custom_icon = None
        
        # 从设置中加载自定义图标
        self.loadCustomIcon()
        
        # 使用光标规则类设置光标
        self.setCursor(CursorRules.get_cursor_for_widget('floating_icon'))
        
    def loadCustomIcon(self):
        icon_path = self.settings.value('custom_icon_path', '')
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull() and pixmap.width() <= 64 and pixmap.height() <= 64:
                self.custom_icon = pixmap
        
    def paintEvent(self, event):
        painter = QPainter(self)
        if self.custom_icon:
            painter.drawPixmap(0, 0, self.custom_icon)
        else:
            # 绘制默认的粉色方块
            painter.fillRect(0, 0, 64, 64, QColor(255, 192, 203))
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.hide()  # 先隐藏悬浮图标
            QTimer.singleShot(200, self.startScreenshot)  # 增加延迟时间
        elif event.button() == Qt.MouseButton.RightButton:
            self.showSettingsDialog()
            
    def showSettingsDialog(self):
        settings = SettingsDialog(self)
        settings.exec()
        
    def startScreenshot(self):
        try:
            self.screenshot_tool = ScreenshotTool()
            self.screenshot_tool.finished.connect(self.onScreenshotFinished)
            QTimer.singleShot(100, self.screenshot_tool.start)  # 延迟启动截图
        except Exception as e:
            print(f"启动截图工具时出错: {str(e)}")
            self.show()  # 如果出错，重新显示图标
        
    def onScreenshotFinished(self):
        try:
            self.show()  # 截图完成后显示图标
        except Exception as e:
            print(f"截图完成处理时出错: {str(e)}") 