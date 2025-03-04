from PyQt6.QtWidgets import QWidget, QApplication, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QScreen, QIcon, QPixmap
from .editor_window import EditorWindow
from .cursor_rules import CursorRules

class FloatingToolPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # 设置无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 创建水平布局
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)
        
        # 添加尺寸标签
        self.size_label = QLabel()
        self.size_label.setStyleSheet("""
            QLabel {
                color: white;
                background: rgba(60, 60, 60, 0.8);
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.size_label)
        
        # 添加按钮
        self.copy_btn = self.createButton("复制")
        self.save_btn = self.createButton("保存")
        self.edit_btn = self.createButton("编辑")
        self.cancel_btn = self.createButton("取消")
        
        layout.addWidget(self.copy_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.cancel_btn)
        
        self.setLayout(layout)
        
        # 设置整体样式
        self.setStyleSheet("""
            QWidget {
                background: rgba(32, 33, 36, 0.9);
                border-radius: 8px;
            }
            QPushButton {
                color: white;
                background: transparent;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.2);
            }
        """)
        
    def createButton(self, text):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn
        
    def updateSizeLabel(self, width, height):
        self.size_label.setText(f"{width} × {height}")

class ScreenshotTool(QWidget):
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__(None)
        self.initUI()
        
    def initUI(self):
        # 设置全屏无边框窗口，并保持透明
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        # 截图相关变量
        self.begin = QPoint()
        self.end = QPoint()
        self.is_drawing = False
        
        # 获取所有屏幕信息
        self.screens = QApplication.screens()
        
        # 计算所有屏幕的总区域
        self.virtual_geometry = self.calculate_virtual_geometry()
        
        # 获取所有屏幕的截图
        self.original_pixmap = self.grab_all_screens()
        
        # 设置鼠标追踪
        self.setMouseTracking(True)
        
        # 设置光标
        self.setCursor(CursorRules.get_cursor_for_tool('screenshot'))
        
    def calculate_virtual_geometry(self):
        """计算所有屏幕的总区域"""
        virtual_geometry = QRect()
        for screen in self.screens:
            virtual_geometry = virtual_geometry.united(screen.geometry())
        return virtual_geometry
        
    def grab_all_screens(self):
        """捕获所有屏幕的截图"""
        # 创建一个足够大的空白图像
        combined_pixmap = QPixmap(self.virtual_geometry.width(), self.virtual_geometry.height())
        combined_pixmap.fill(Qt.GlobalColor.transparent)
        
        # 创建画布
        painter = QPainter(combined_pixmap)
        
        # 在相应位置绘制每个屏幕的截图
        for screen in self.screens:
            # 获取屏幕截图
            screen_pixmap = screen.grabWindow(0)
            # 计算屏幕在虚拟桌面中的相对位置
            screen_rect = screen.geometry()
            # 绘制到合并的图像上
            painter.drawPixmap(
                screen_rect.x() - self.virtual_geometry.x(),
                screen_rect.y() - self.virtual_geometry.y(),
                screen_pixmap
            )
            
        painter.end()
        return combined_pixmap
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 绘制半透明背景
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))
        
        if self.is_drawing:
            # 计算选择区域
            rect = QRect(self.begin, self.end).normalized()
            
            # 绘制选择框边界
            pen = QPen(QColor(0, 174, 255), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawRect(rect)
            
            # 绘制选择框四角
            corner_size = 10
            corner_color = QColor(0, 174, 255)
            painter.setPen(QPen(corner_color, 2))
            
            # 获取整数坐标
            x1, y1 = int(rect.topLeft().x()), int(rect.topLeft().y())
            x2, y2 = int(rect.topRight().x()), int(rect.topRight().y())
            x3, y3 = int(rect.bottomLeft().x()), int(rect.bottomLeft().y())
            x4, y4 = int(rect.bottomRight().x()), int(rect.bottomRight().y())
            
            # 左上角
            painter.drawLine(x1, y1, x1 + corner_size, y1)
            painter.drawLine(x1, y1, x1, y1 + corner_size)
            
            # 右上角
            painter.drawLine(x2, y2, x2 - corner_size, y2)
            painter.drawLine(x2, y2, x2, y2 + corner_size)
            
            # 左下角
            painter.drawLine(x3, y3, x3 + corner_size, y3)
            painter.drawLine(x3, y3, x3, y3 - corner_size)
            
            # 右下角
            painter.drawLine(x4, y4, x4 - corner_size, y4)
            painter.drawLine(x4, y4, x4, y4 - corner_size)
            
            # 显示尺寸信息
            size_text = f'{rect.width()} x {rect.height()}'
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            
            text_rect = painter.fontMetrics().boundingRect(size_text)
            text_x = int(rect.center().x() - text_rect.width() / 2)
            text_y = int(rect.top() - 5)
            
            # 绘制文本背景
            text_bg_rect = QRect(text_x - 5, text_y - text_rect.height(),
                               text_rect.width() + 10, text_rect.height() + 5)
            painter.fillRect(text_bg_rect, QColor(0, 0, 0, 160))
            
            # 绘制尺寸文本
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(text_x, text_y, size_text)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.begin = event.pos()
            self.end = self.begin
            self.is_drawing = True
            self.update()
            
    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.end = event.pos()
            self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.is_drawing = False
            if self.begin and self.end:
                rect = QRect(self.begin, self.end).normalized()
                if rect.width() > 0 and rect.height() > 0:
                    self.capture_screenshot()
                    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            self.finished.emit()
            
    def capture_screenshot(self):
        if self.begin and self.end:
            rect = QRect(self.begin, self.end).normalized()
            if rect.width() > 0 and rect.height() > 0:
                # 捕获选定区域的截图
                screenshot = self.original_pixmap.copy(rect)
                
                # 打开编辑窗口
                from .editor_window import EditorWindow
                self.editor = EditorWindow(screenshot)
                self.editor.show()
                
        self.close()
        self.finished.emit()
        
    def copyScreenshot(self):
        if self.begin and self.end:
            rect = QRect(self.begin, self.end).normalized()
            screenshot = self.original_pixmap.copy(rect)
            QApplication.clipboard().setPixmap(screenshot)
            self.close()
            self.finished.emit()
            
    def saveScreenshot(self):
        if self.begin and self.end:
            rect = QRect(self.begin, self.end).normalized()
            screenshot = self.original_pixmap.copy(rect)
            self.editor = EditorWindow(screenshot)
            self.editor.show()
            self.close()
            self.finished.emit()
            
    def editScreenshot(self):
        if self.begin and self.end:
            rect = QRect(self.begin, self.end).normalized()
            screenshot = self.original_pixmap.copy(rect)
            self.editor = EditorWindow(screenshot)
            self.editor.show()
            self.close()
            self.finished.emit()
            
    def start(self):
        # 设置窗口大小为所有屏幕的总区域
        self.setGeometry(self.virtual_geometry)
        self.showFullScreen()  # 使用showFullScreen而不是show
        QApplication.processEvents()  # 确保窗口完全显示
        self.activateWindow()  # 确保窗口获得焦点
        self.raise_()  # 确保窗口在最顶层