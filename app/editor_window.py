from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QColorDialog, QSpinBox, QLabel, QSlider, QFileDialog,
                           QLineEdit, QComboBox, QToolButton, QFontDialog, QFrame, QMenu)
from PyQt6.QtCore import Qt, QPoint, QRect, QLineF, QPointF, QMimeData, QUrl, QTimer, QSize, QByteArray, QBuffer
from PyQt6.QtGui import QPainter, QPen, QColor, QImage, QPixmap, QFont, QTransform, QCursor, QDrag, QFontMetrics, QIcon
from PyQt6.QtWidgets import QApplication
import os
import pyperclip
from PIL import Image, ImageEnhance
import io
import math
from .cursor_rules import CursorRules
from PyQt6.QtCore import QSettings, QDateTime

class DynamicTextBox(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                          Qt.WindowType.WindowStaysOnTopHint |
                          Qt.WindowType.Tool)
        
        # 初始化背景色和边框色（默认透明）
        self.bg_color = QColor(255, 255, 255, 0)
        self.border_color = QColor(255, 255, 255, 0)
        
        # 初始化边框属性
        self.border_width = 1
        self.border_style = Qt.PenStyle.SolidLine  # 默认实线
        
        # 设置样式
        self.updateStyle()
        
        # 创建文本编辑框
        self.text_edit = QLineEdit(self)
        self.text_edit.setStyleSheet("""
            QLineEdit {
                background: transparent;
                padding: 4px;
                text-align: center;  /* 文本居中 */
                qproperty-alignment: AlignCenter;  /* 文本居中对齐 */
            }
        """)
        
        # 初始化变量
        self.resizing = False
        self.resize_margin = 10  # 调整大小的边距
        self.min_size = QSize(100, 30)  # 最小尺寸
        self.base_point = None  # 基准点（左下角）
        self.resize_corner = None  # 当前正在拖拽的角
        self.resize_start_pos = None
        self.resize_start_size = None
        self.resize_start_geo = None
        self.dragging = False
        
        # 设置初始大小
        self.setMinimumSize(self.min_size)
        self.resize(200, 30)
        
        # 布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.text_edit)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 设置鼠标跟踪
        self.setMouseTracking(True)
        self.text_edit.setMouseTracking(True)
        
        # 连接文本变化信号
        self.text_edit.textChanged.connect(self.adjustFontSize)
        
    def adjustFontSize(self):
        """根据文本框大小调整字体大小"""
        try:
            text = self.text_edit.text()
            if not text:
                return
                
            # 获取当前字体
            font = self.text_edit.font()
            
            # 计算合适的字体大小（考虑内边距）
            padding = 8  # 内边距
            height = int(self.height() * 0.8) - (padding * 2)  # 文本框高度的80%，减去内边距
            width = self.width() - (padding * 2)  # 减去内边距
            
            # 设置初始字体大小
            font.setPixelSize(height)
            
            # 创建字体度量对象
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(text)
            text_height = metrics.height()
            
            # 如果文本宽度超过可用宽度，或文本高度超过可用高度，调整字体大小
            if text_width > width or text_height > height:
                width_scale = width / text_width if text_width > width else 1
                height_scale = height / text_height if text_height > height else 1
                scale_factor = min(width_scale, height_scale)
                new_size = max(8, int(height * scale_factor))  # 设置最小字体大小为8像素
                font.setPixelSize(new_size)
            
            # 应用字体
            self.text_edit.setFont(font)
            
        except Exception as e:
            print(f"调整字体大小时出错: {str(e)}")
            
    def updatePosition(self, base_point):
        """更新文本框位置，保持左下角对齐"""
        try:
            if base_point:
                self.base_point = QPoint(base_point.x(), base_point.y())
                self.move(self.base_point.x(), self.base_point.y() - self.height())
        except Exception as e:
            print(f"更新位置时出错: {str(e)}")

    def getResizeCorner(self, pos):
        """确定鼠标位于哪个调整大小的角落"""
        try:
            margin = self.resize_margin
            width = self.width()
            height = self.height()
            
            # 检查四个角
            if pos.x() <= margin:
                if pos.y() <= margin:
                    return 'top-left'
                elif pos.y() >= height - margin:
                    return 'bottom-left'
            elif pos.x() >= width - margin:
                if pos.y() <= margin:
                    return 'top-right'
                elif pos.y() >= height - margin:
                    return 'bottom-right'
            return None
        except Exception as e:
            print(f"获取调整角落时出错: {str(e)}")
            return None

    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                corner = self.getResizeCorner(event.pos())
                if corner:
                    self.resizing = True
                    self.resize_corner = corner
                    self.resize_start_pos = QPoint(int(event.globalPosition().x()), 
                                                 int(event.globalPosition().y()))
                    self.resize_start_size = self.size()
                    self.resize_start_geo = self.geometry()
                    event.accept()
                    return
                elif self.text_edit.geometry().contains(event.pos()):
                    super().mousePressEvent(event)
                else:
                    self.dragging = True
                    self.drag_start_pos = QPoint(int(event.globalPosition().x()), 
                                               int(event.globalPosition().y()))
                    self.drag_start_geo = self.geometry()
        except Exception as e:
            print(f"鼠标按下时出错: {str(e)}")

    def mouseMoveEvent(self, event):
        try:
            if self.resizing and self.resize_corner and self.resize_start_pos:
                current_pos = QPoint(int(event.globalPosition().x()), 
                                   int(event.globalPosition().y()))
                delta = current_pos - self.resize_start_pos
                new_geo = QRect(self.resize_start_geo)
                
                if self.resize_corner == 'top-left':
                    new_width = max(self.resize_start_size.width() - delta.x(), self.min_size.width())
                    new_height = max(self.resize_start_size.height() - delta.y(), self.min_size.height())
                    new_geo.setLeft(self.resize_start_geo.right() - new_width)
                    new_geo.setTop(self.base_point.y() - new_height)
                elif self.resize_corner == 'top-right':
                    new_width = max(self.resize_start_size.width() + delta.x(), self.min_size.width())
                    new_height = max(self.resize_start_size.height() - delta.y(), self.min_size.height())
                    new_geo.setRight(self.resize_start_geo.left() + new_width)
                    new_geo.setTop(self.base_point.y() - new_height)
                elif self.resize_corner == 'bottom-left':
                    new_width = max(self.resize_start_size.width() - delta.x(), self.min_size.width())
                    new_height = max(self.resize_start_size.height() + delta.y(), self.min_size.height())
                    new_geo.setLeft(self.resize_start_geo.right() - new_width)
                    new_geo.setHeight(new_height)
                else:  # bottom-right
                    new_width = max(self.resize_start_size.width() + delta.x(), self.min_size.width())
                    new_height = max(self.resize_start_size.height() + delta.y(), self.min_size.height())
                    new_geo.setRight(self.resize_start_geo.left() + new_width)
                    new_geo.setHeight(new_height)
                
                # 确保底部对齐基准点
                new_geo.moveBottom(self.base_point.y())
                self.setGeometry(new_geo)
                
                # 调整字体大小
                self.adjustFontSize()
                
            elif self.dragging and self.drag_start_pos:
                # 处理整个文本框的拖动
                current_pos = QPoint(int(event.globalPosition().x()), 
                                   int(event.globalPosition().y()))
                delta = current_pos - self.drag_start_pos
                new_geo = self.drag_start_geo.translated(delta)
                self.setGeometry(new_geo)
                # 更新基准点
                self.base_point = QPoint(new_geo.left(), new_geo.bottom())
            else:
                # 更新鼠标样式
                corner = self.getResizeCorner(event.pos())
                if corner in ['top-left', 'bottom-right']:
                    self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                elif corner in ['top-right', 'bottom-left']:
                    self.setCursor(Qt.CursorShape.SizeBDiagCursor)
                else:
                    self.setCursor(Qt.CursorShape.IBeamCursor)
                super().mouseMoveEvent(event)
        except Exception as e:
            print(f"鼠标移动时出错: {str(e)}")

    def mouseReleaseEvent(self, event):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                if self.resizing:
                    self.resizing = False
                    self.resize_corner = None
                    self.resize_start_pos = None
                    self.resize_start_size = None
                    self.resize_start_geo = None
                elif self.dragging:
                    self.dragging = False
                    self.drag_start_pos = None
                    self.drag_start_geo = None
                event.accept()
            else:
                super().mouseReleaseEvent(event)
        except Exception as e:
            print(f"鼠标释放时出错: {str(e)}")

    def getText(self):
        return self.text_edit.text()
        
    def setFont(self, font):
        """设置字体并调整文本框大小"""
        self.text_edit.setFont(font)
        # 根据字体大小调整文本框高度
        metrics = QFontMetrics(font)
        height = metrics.height() + 10  # 添加一些内边距
        self.setMinimumSize(self.min_size.width(), height)
        self.resize(self.width(), height)
        
    def setTextColor(self, color):
        palette = self.text_edit.palette()
        palette.setColor(self.text_edit.foregroundRole(), color)
        self.text_edit.setPalette(palette)

    def updateStyle(self):
        """更新样式表"""
        # 将Qt.PenStyle转换为CSS border-style
        style_map = {
            Qt.PenStyle.SolidLine: 'solid',
            Qt.PenStyle.DashLine: 'dashed',
            Qt.PenStyle.DotLine: 'dotted',
            Qt.PenStyle.DashDotLine: 'dashed',
            Qt.PenStyle.DashDotDotLine: 'dashed'
        }
        border_style = style_map.get(self.border_style, 'solid')
        
        self.setStyleSheet(f"""
            DynamicTextBox {{
                background-color: rgba({self.bg_color.red()}, {self.bg_color.green()}, 
                                     {self.bg_color.blue()}, {self.bg_color.alpha()});
                border: {self.border_width}px {border_style} rgba({self.border_color.red()}, 
                       {self.border_color.green()}, {self.border_color.blue()}, 
                       {self.border_color.alpha()});
            }}
        """)

    def setBackgroundColor(self, color):
        """设置背景色"""
        self.bg_color = color
        self.updateStyle()

    def setBorderColor(self, color):
        """设置边框颜色"""
        self.border_color = color
        self.updateStyle()

    def setBorderWidth(self, width):
        """设置边框粗细"""
        self.border_width = width
        self.updateStyle()

    def setBorderStyle(self, style):
        """设置边框样式"""
        self.border_style = style
        self.updateStyle()

class EditorWindow(QWidget):
    def __init__(self, screenshot, parent=None):
        super().__init__(parent)
        self.original_screenshot = screenshot
        self.current_screenshot = screenshot.copy()
        self.drawing = False
        self.last_point = None
        self.preview_point = None
        self.is_dragging = False  # 添加拖拽状态标志
        
        # 添加当前颜色属性
        self.current_color = QColor(255, 0, 0)  # 默认红色
        
        # 设置窗口属性以支持拖放
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowMinMaxButtonsHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # 添加绘图模式
        self.draw_mode = 'pen'
        self.text_input = ''
        self.current_font = QFont('Arial', 12)
        self.text_position = None
        
        # 添加历史记录用于撤销/重做
        self.history = [screenshot.copy()]
        self.history_index = 0
        
        # 添加延迟更新定时器
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.delayedImageUpdate)
        
        self.temp_file = None
        
        # 修改文本输入框为动态文本框
        self.text_box = DynamicTextBox()
        self.text_box.hide()
        self.text_box.text_edit.returnPressed.connect(self.handleTextInput)
        
        # 添加文本背景色按钮
        self.text_bg_color_btn = QPushButton('文本背景色')
        self.text_bg_color_btn.clicked.connect(self.chooseTextBackgroundColor)
        
        # 添加文本边框颜色按钮
        self.text_border_color_btn = QPushButton('文本边框颜色')
        self.text_border_color_btn.clicked.connect(self.chooseTextBorderColor)
        
        # 添加设置对象
        self.settings = QSettings('ScreenshotTool', 'Settings')
        
        # 初始化自定义图标
        self.loadCustomIcons()
        
        # 修改布局为水平布局
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        
        # 图片显示区域（左侧）
        self.image_label = QLabel()
        self.image_label.setPixmap(self.current_screenshot)
        self.main_layout.addWidget(self.image_label, stretch=1)
        
        # 工具栏（右侧）
        toolbar = QVBoxLayout()
        toolbar.setSpacing(2)  # 减小控件间距
        
        # 工具选择下拉框
        self.tool_combo = QComboBox()
        self.tool_combo.addItems(['画笔', '矩形', '圆形', '文字', '箭头', '马赛克'])
        self.tool_combo.currentTextChanged.connect(self.changeDrawMode)
        toolbar.addWidget(self.tool_combo)
        
        # 画笔颜色和粗细
        color_thickness_layout = QHBoxLayout()
        self.color_btn = QPushButton('画笔颜色')
        self.color_btn.clicked.connect(self.choosePenColor)
        self.color_btn.setMaximumWidth(80)
        color_thickness_layout.addWidget(self.color_btn)
        
        self.thickness_spin = QSpinBox()
        self.thickness_spin.setRange(1, 20)
        self.thickness_spin.setValue(2)
        self.thickness_spin.setMaximumWidth(50)
        color_thickness_layout.addWidget(self.thickness_spin)
        toolbar.addLayout(color_thickness_layout)
        
        # 字体设置和文本相关功能
        text_settings_layout = QVBoxLayout()
        text_settings_layout.setSpacing(2)  # 减小间距
        
        # 文本按钮组
        text_buttons_layout = QVBoxLayout()
        text_buttons_layout.setSpacing(2)
        
        # 文本按钮
        self.font_btn = QPushButton('文本')
        self.font_btn.clicked.connect(self.chooseFont)
        self.font_btn.setMinimumHeight(30)  # 增加按钮高度
        text_buttons_layout.addWidget(self.font_btn)
        
        # 背景和边框按钮
        self.text_bg_color_btn = QPushButton('文本背景')
        self.text_bg_color_btn.clicked.connect(self.chooseTextBackgroundColor)
        self.text_bg_color_btn.setMinimumHeight(30)  # 增加按钮高度
        text_buttons_layout.addWidget(self.text_bg_color_btn)
        
        self.text_border_color_btn = QPushButton('文本边框')
        self.text_border_color_btn.clicked.connect(self.chooseTextBorderColor)
        self.text_border_color_btn.setMinimumHeight(30)  # 增加按钮高度
        text_buttons_layout.addWidget(self.text_border_color_btn)
        
        text_settings_layout.addLayout(text_buttons_layout)
        toolbar.addLayout(text_settings_layout)
        
        # 图片调整
        adjustment_group = QVBoxLayout()
        adjustment_group.setSpacing(1)
        
        # 亮度
        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(QLabel('亮度:'))
        
        # 亮度数值输入框
        self.brightness_spin = QSpinBox()
        self.brightness_spin.setRange(-100, 100)  # -100到100，0为中间值
        self.brightness_spin.setValue(0)
        self.brightness_spin.setFixedWidth(60)
        self.brightness_spin.setSuffix("%")  # 添加百分比后缀
        brightness_layout.addWidget(self.brightness_spin)
        
        # 亮度滑动条
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-100, 100)  # -100到100，0为中间值
        self.brightness_slider.setValue(0)
        self.brightness_slider.setTickPosition(QSlider.TickPosition.TicksBelow)  # 添加刻度
        self.brightness_slider.setTickInterval(50)  # 每50一个刻度
        brightness_layout.addWidget(self.brightness_slider)
        
        # 连接亮度控件信号
        self.brightness_slider.valueChanged.connect(self.brightness_spin.setValue)
        self.brightness_spin.valueChanged.connect(self.brightness_slider.setValue)
        self.brightness_spin.valueChanged.connect(lambda: self.update_timer.start(100))
        adjustment_group.addLayout(brightness_layout)
        
        # 对比度
        contrast_layout = QHBoxLayout()
        contrast_layout.addWidget(QLabel('对比:'))
        
        # 对比度数值输入框
        self.contrast_spin = QSpinBox()
        self.contrast_spin.setRange(-100, 100)  # -100到100，0为中间值
        self.contrast_spin.setValue(0)
        self.contrast_spin.setFixedWidth(60)
        self.contrast_spin.setSuffix("%")  # 添加百分比后缀
        contrast_layout.addWidget(self.contrast_spin)
        
        # 对比度滑动条
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(-100, 100)  # -100到100，0为中间值
        self.contrast_slider.setValue(0)
        self.contrast_slider.setTickPosition(QSlider.TickPosition.TicksBelow)  # 添加刻度
        self.contrast_slider.setTickInterval(50)  # 每50一个刻度
        contrast_layout.addWidget(self.contrast_slider)
        
        # 连接对比度控件信号
        self.contrast_slider.valueChanged.connect(self.contrast_spin.setValue)
        self.contrast_spin.valueChanged.connect(self.contrast_slider.setValue)
        self.contrast_spin.valueChanged.connect(lambda: self.update_timer.start(100))
        adjustment_group.addLayout(contrast_layout)
        
        # 色相
        hue_layout = QHBoxLayout()
        hue_layout.addWidget(QLabel('色相:'))
        
        # 色相数值输入框
        self.hue_spin = QSpinBox()
        self.hue_spin.setRange(-180, 180)  # -180到180度，0为中间值
        self.hue_spin.setValue(0)
        self.hue_spin.setFixedWidth(60)
        self.hue_spin.setSuffix("°")  # 添加度数后缀
        hue_layout.addWidget(self.hue_spin)
        
        # 色相滑动条
        self.hue_slider = QSlider(Qt.Orientation.Horizontal)
        self.hue_slider.setRange(-180, 180)  # -180到180度，0为中间值
        self.hue_slider.setValue(0)
        self.hue_slider.setTickPosition(QSlider.TickPosition.TicksBelow)  # 添加刻度
        self.hue_slider.setTickInterval(60)  # 每60度一个刻度
        hue_layout.addWidget(self.hue_slider)
        
        # 连接色相控件信号
        self.hue_slider.valueChanged.connect(self.hue_spin.setValue)
        self.hue_spin.valueChanged.connect(self.hue_slider.setValue)
        self.hue_spin.valueChanged.connect(lambda: self.update_timer.start(100))
        adjustment_group.addLayout(hue_layout)
        
        toolbar.addLayout(adjustment_group)
        
        # 旋转按钮
        rotation_layout = QHBoxLayout()
        self.rotate_left_btn = QToolButton()
        self.rotate_left_btn.setText('↺')
        self.rotate_left_btn.clicked.connect(lambda: self.rotateImage(-90))
        self.rotate_left_btn.setMinimumSize(40, 40)
        self.rotate_left_btn.setFont(QFont('Arial', 16))
        self.rotate_left_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.rotate_left_btn.customContextMenuRequested.connect(lambda pos: self.showIconMenu(self.rotate_left_btn, 'rotate_left_icon'))
        rotation_layout.addWidget(self.rotate_left_btn)
        
        self.rotate_right_btn = QToolButton()
        self.rotate_right_btn.setText('↻')
        self.rotate_right_btn.clicked.connect(lambda: self.rotateImage(90))
        self.rotate_right_btn.setMinimumSize(40, 40)
        self.rotate_right_btn.setFont(QFont('Arial', 16))
        self.rotate_right_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.rotate_right_btn.customContextMenuRequested.connect(lambda pos: self.showIconMenu(self.rotate_right_btn, 'rotate_right_icon'))
        rotation_layout.addWidget(self.rotate_right_btn)
        toolbar.addLayout(rotation_layout)
        
        # 撤销/重做按钮
        undo_redo_layout = QHBoxLayout()
        self.undo_btn = QPushButton('↩')
        self.undo_btn.clicked.connect(self.undo)
        self.undo_btn.setMinimumSize(40, 40)
        self.undo_btn.setFont(QFont('Arial', 16))
        self.undo_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.undo_btn.customContextMenuRequested.connect(lambda pos: self.showIconMenu(self.undo_btn, 'undo_icon'))
        undo_redo_layout.addWidget(self.undo_btn)
        
        self.redo_btn = QPushButton('↪')
        self.redo_btn.clicked.connect(self.redo)
        self.redo_btn.setMinimumSize(40, 40)
        self.redo_btn.setFont(QFont('Arial', 16))
        self.redo_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.redo_btn.customContextMenuRequested.connect(lambda pos: self.showIconMenu(self.redo_btn, 'redo_icon'))
        undo_redo_layout.addWidget(self.redo_btn)
        toolbar.addLayout(undo_redo_layout)
        
        # 保存/分享按钮
        save_share_layout = QHBoxLayout()
        self.save_btn = QPushButton('保存')
        self.save_btn.clicked.connect(self.saveImage)
        self.save_btn.setMaximumWidth(60)
        save_share_layout.addWidget(self.save_btn)
        
        self.share_btn = QPushButton('分享')
        self.share_btn.clicked.connect(self.shareImage)
        self.share_btn.setMaximumWidth(60)
        save_share_layout.addWidget(self.share_btn)
        toolbar.addLayout(save_share_layout)
        
        # 添加弹簧
        toolbar.addStretch()
        
        # 将工具栏添加到主布局
        toolbar_widget = QWidget()
        toolbar_widget.setLayout(toolbar)
        toolbar_widget.setMaximumWidth(200)  # 限制工具栏宽度
        self.main_layout.addWidget(toolbar_widget)
        
    def changeDrawMode(self, mode):
        mode_map = {
            '画笔': 'pen', 
            '矩形': 'rect', 
            '圆形': 'circle', 
            '文字': 'text',
            '箭头': 'arrow',
            '马赛克': 'mosaic'
        }
        
        if self.drawing:
            self.drawing = False
            self.last_point = None
            self.update()
            
        self.draw_mode = mode_map[mode]
        
        # 使用光标规则类设置光标
        self.setCursor(CursorRules.get_cursor_for_tool(self.draw_mode))
        
        # 隐藏文本框
        if self.text_box and self.text_box.isVisible():
            self.text_box.hide()
            self.text_position = None
            
    def handleTextInput(self):
        """处理文本输入的回车事件"""
        try:
            text = self.text_box.getText()
            if text and self.text_position:
                painter = QPainter(self.current_screenshot)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
                
                # 使用文本框的字体和颜色
                font = self.text_box.text_edit.font()
                painter.setFont(font)
                painter.setPen(QPen(self.current_color))
                
                # 获取文本框当前的全局位置
                text_box_pos = self.text_box.mapToGlobal(QPoint(0, 0))
                # 转换为图片坐标系
                window_pos = self.mapFromGlobal(text_box_pos)
                image_pos = QPoint(window_pos.x() - self.image_label.pos().x(),
                                 window_pos.y() - self.image_label.pos().y())
                
                # 计算文本边界
                metrics = QFontMetrics(font)
                text_width = metrics.horizontalAdvance(text)
                text_height = metrics.height()
                
                # 调整文本位置，确保在图片范围内
                x = min(max(0, image_pos.x()), self.current_screenshot.width() - text_width)
                y = min(max(text_height, image_pos.y() + text_height),
                       self.current_screenshot.height())
                
                # 绘制文本背景（如果不是完全透明）
                if self.text_box.bg_color.alpha() > 0:
                    bg_rect = QRect(x - 2, y - text_height - 2,
                                  text_width + 4, text_height + 4)
                    painter.fillRect(bg_rect, self.text_box.bg_color)
                
                # 绘制文本边框（如果不是完全透明）
                if self.text_box.border_color.alpha() > 0:
                    pen = QPen(self.text_box.border_color, 
                             self.text_box.border_width,
                             self.text_box.border_style)
                    painter.setPen(pen)
                    painter.drawRect(bg_rect)
                
                # 绘制文本
                painter.setPen(QPen(self.current_color))
                painter.drawText(x, y, text)
                
                # 更新图片
                self.image_label.setPixmap(self.current_screenshot)
                self.addToHistory()
                
                # 重置状态
                self.text_box.hide()
                self.text_position = None
                self.drawing = False
                self.last_point = None
                self.is_dragging = False
                
                # 启用所有工具
                self.enableTools()
                
                # 重置工具状态
                self.tool_combo.setEnabled(True)
                self.drawing = False
                
        except Exception as e:
            print(f"Error in handleTextInput: {str(e)}")
            # 发生错误时也要确保重置状态
            self.text_box.hide()
            self.text_position = None
            self.drawing = False
            self.last_point = None
            self.is_dragging = False
            self.enableTools()
            self.tool_combo.setEnabled(True)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton or \
           (event.button() == Qt.MouseButton.LeftButton and 
            event.modifiers() == Qt.KeyboardModifier.ControlModifier):
            # 重置拖拽状态
            self.is_dragging = False
            # 开始拖拽
            self.startDrag(event)
            return
        elif event.button() == Qt.MouseButton.LeftButton and \
             event.modifiers() == Qt.KeyboardModifier.NoModifier:
            # 确保工具栏是启用的
            self.enableTools()
            
            # 获取鼠标位置相对于图片标签的偏移
            pos = event.pos()
            label_pos = self.image_label.pos()
            image_pos = QPoint(pos.x() - label_pos.x(), pos.y() - label_pos.y())
            
            # 检查是否在图片范围内
            if image_pos.x() >= 0 and image_pos.y() >= 0 and \
               image_pos.x() < self.current_screenshot.width() and \
               image_pos.y() < self.current_screenshot.height():
                self.drawing = True
                self.last_point = image_pos
                
                if self.draw_mode == 'text':
                    self.text_position = image_pos
                    # 显示动态文本框，使用实际鼠标位置
                    self.text_box.setFont(self.current_font)
                    self.text_box.setTextColor(self.current_color)
                    self.text_box.text_edit.clear()
                    # 使用实际鼠标位置
                    self.text_box.updatePosition(self.mapToGlobal(pos))
                    self.text_box.show()
                    self.text_box.text_edit.setFocus()
                    self.text_box.raise_()
        elif event.button() == Qt.MouseButton.RightButton:
            self.confirmEdit()

    def startDrag(self, event):
        """开始拖拽操作"""
        try:
            # 创建拖拽对象
            drag = QDrag(self)
            mime_data = QMimeData()
            
            # 设置剪贴板
            clipboard = QApplication.clipboard()
            clipboard.clear()
            clipboard.setPixmap(self.current_screenshot)
            
            # 将图片转换为字节数据
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QBuffer.OpenModeFlag.WriteOnly)
            self.current_screenshot.save(buffer, 'PNG', quality=100)  # 使用高质量设置
            buffer.close()
            
            # 设置MIME数据
            mime_data.setImageData(self.current_screenshot.toImage())
            mime_data.setData('image/png', byte_array)
            
            # 设置拖拽数据
            drag.setMimeData(mime_data)
            
            # 设置拖拽预览图
            preview = self.current_screenshot.scaled(
                64, 64,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # 设置拖拽预览图和热点
            drag.setPixmap(preview)
            drag.setHotSpot(QPoint(preview.width() // 2, preview.height() // 2))
            
            # 执行拖拽
            result = drag.exec(Qt.DropAction.CopyAction)
            
            # 确保拖拽完成后剪贴板内容仍然存在
            if not clipboard.pixmap().isNull():
                clipboard.setPixmap(self.current_screenshot)
            
        except Exception as e:
            print(f"拖拽操作出错: {str(e)}")
            self.is_dragging = False
        
    def confirmEdit(self):
        """右键确认编辑完成"""
        try:
            if self.text_box and self.text_box.isVisible():
                self.text_box.hide()
                self.text_position = None
                return
                
            # 设置拖拽状态
            self.is_dragging = True
            
            # 复制到剪贴板
            clipboard = QApplication.clipboard()
            clipboard.clear()  # 先清除剪贴板
            if not clipboard.setPixmap(self.current_screenshot):
                print("设置剪贴板失败")
            
            # 保存到设置的路径（如果有）
            settings = QSettings('ScreenshotTool', 'Settings')
            save_path = settings.value('save_path', '')
            if save_path:
                timestamp = QDateTime.currentDateTime().toString('yyyyMMdd_hhmmss')
                filename = os.path.join(save_path, f'screenshot_{timestamp}.png')
                self.current_screenshot.save(filename, quality=100)
            
            # 禁用所有工具按钮
            self.disableTools()
            
            # 开始拖拽操作
            self.startDrag(None)
            
        except Exception as e:
            print(f"确认编辑时出错: {str(e)}")
            self.is_dragging = False  # 发生错误时重置拖拽状态
        
    def disableTools(self):
        """禁用所有工具按钮"""
        self.tool_combo.setEnabled(False)
        self.color_btn.setEnabled(False)
        self.thickness_spin.setEnabled(False)
        self.font_btn.setEnabled(False)
        self.brightness_slider.setEnabled(False)
        self.brightness_spin.setEnabled(False)
        self.contrast_slider.setEnabled(False)
        self.contrast_spin.setEnabled(False)
        self.hue_slider.setEnabled(False)
        self.hue_spin.setEnabled(False)
        self.undo_btn.setEnabled(False)
        self.redo_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.share_btn.setEnabled(False)
        
    def enableTools(self):
        """启用所有工具按钮"""
        self.tool_combo.setEnabled(True)
        self.color_btn.setEnabled(True)
        self.thickness_spin.setEnabled(True)
        self.font_btn.setEnabled(True)
        self.brightness_slider.setEnabled(True)
        self.brightness_spin.setEnabled(True)
        self.contrast_slider.setEnabled(True)
        self.contrast_spin.setEnabled(True)
        self.hue_slider.setEnabled(True)
        self.hue_spin.setEnabled(True)
        self.undo_btn.setEnabled(True)
        self.redo_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.share_btn.setEnabled(True)
        self.text_bg_color_btn.setEnabled(True)
        self.text_border_color_btn.setEnabled(True)
        
    def mouseMoveEvent(self, event):
        if self.is_dragging:
            return
            
        # 获取相对于图片标签的位置
        pos = event.pos()
        label_pos = self.image_label.pos()
        image_pos = QPoint(pos.x() - label_pos.x(), pos.y() - label_pos.y())
        
        # 检查是否在图片范围内
        if image_pos.x() >= 0 and image_pos.y() >= 0 and \
           image_pos.x() < self.current_screenshot.width() and \
           image_pos.y() < self.current_screenshot.height():
            self.preview_point = image_pos
            
            if not self.drawing:
                if self.draw_mode == 'pen':
                    self.update()
                return
                
            # 创建临时副本用于预览
            temp_pixmap = QPixmap(self.current_screenshot)
            painter = QPainter(temp_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            try:
                if self.draw_mode == 'pen':
                    pen = QPen(self.current_color, 
                              self.thickness_spin.value(),
                              Qt.PenStyle.SolidLine,
                              Qt.PenCapStyle.RoundCap,
                              Qt.PenJoinStyle.RoundJoin)
                    painter.setPen(pen)
                    if self.last_point:  # 确保有上一个点
                        painter.drawLine(self.last_point, image_pos)
                    self.current_screenshot = temp_pixmap
                    self.last_point = image_pos
                elif self.draw_mode == 'mosaic':
                    if self.last_point:  # 确保有上一个点
                        self.applyMosaic(painter, self.last_point, image_pos)
                    self.current_screenshot = temp_pixmap
                    self.last_point = image_pos
                else:
                    pen = QPen(self.current_color, 
                              self.thickness_spin.value(),
                              Qt.PenStyle.SolidLine)
                    if self.draw_mode == 'arrow':
                        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                    painter.setPen(pen)
                    
                    if self.draw_mode in ['rect', 'circle']:
                        rect = QRect(self.last_point, image_pos).normalized()
                        if self.draw_mode == 'rect':
                            painter.drawRect(rect)
                        else:
                            painter.drawEllipse(rect)
                    elif self.draw_mode == 'arrow':
                        self.drawArrow(painter, self.last_point, image_pos)
            finally:
                painter.end()
                
            self.image_label.setPixmap(temp_pixmap)
        else:
            self.preview_point = None
            self.update()
        
    def mouseReleaseEvent(self, event):
        if self.is_dragging:  # 如果正在拖拽，不处理其他鼠标事件
            self.is_dragging = False
            self.enableTools()  # 拖拽结束后重新启用工具
            return
            
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.drawing = False
            # 获取相对于图片标签的位置
            pos = event.pos()
            label_pos = self.image_label.pos()
            image_pos = QPoint(pos.x() - label_pos.x(), pos.y() - label_pos.y())
            
            if self.draw_mode in ['rect', 'circle', 'arrow'] and self.last_point:
                painter = QPainter(self.current_screenshot)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                try:
                    pen = QPen(self.current_color, 
                              self.thickness_spin.value(),
                              Qt.PenStyle.SolidLine)
                    if self.draw_mode == 'arrow':
                        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                    painter.setPen(pen)
                    
                    if self.draw_mode in ['rect', 'circle']:
                        rect = QRect(self.last_point, image_pos).normalized()
                        if self.draw_mode == 'rect':
                            painter.drawRect(rect)
                        else:
                            painter.drawEllipse(rect)
                    else:  # arrow
                        self.drawArrow(painter, self.last_point, image_pos)
                finally:
                    painter.end()
                    
                self.image_label.setPixmap(self.current_screenshot)
                
            self.addToHistory()  # 移动到这里，确保所有工具都会添加历史记录
            
    def choosePenColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color
            
    def chooseFont(self):
        font, ok = QFontDialog.getFont(self.current_font, self)
        if ok:
            self.current_font = font
            
    def delayedImageUpdate(self):
        self.adjustImage()
        
    def adjustImage(self):
        """调整图片的亮度、对比度和色相"""
        try:
            # 将QPixmap转换为PIL Image
            qimage = self.current_screenshot.toImage()
            buffer = QBuffer()
            buffer.open(QBuffer.OpenModeFlag.ReadWrite)
            qimage.save(buffer, "PNG")
            img = Image.open(io.BytesIO(buffer.data().data()))
            
            # 应用亮度调整（-100到100，0为原始值）
            brightness_value = self.brightness_spin.value()
            if brightness_value != 0:
                # 将-100到100映射到0.0到2.0，0映射到1.0
                brightness_factor = 1.0 + (brightness_value / 100.0)
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness_factor)
            
            # 应用对比度调整（-100到100，0为原始值）
            contrast_value = self.contrast_spin.value()
            if contrast_value != 0:
                # 将-100到100映射到0.0到2.0，0映射到1.0
                contrast_factor = 1.0 + (contrast_value / 100.0)
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast_factor)
            
            # 应用色相调整（-180到180，0为原始值）
            hue_value = self.hue_spin.value()
            if hue_value != 0:
                # 转换为HSV颜色空间
                img = img.convert('HSV')
                h, s, v = img.split()
                
                # 调整色相（直接使用度数作为偏移量）
                h_data = list(h.getdata())
                # 将色相值归一化到0-255范围
                hue_shift = int((hue_value / 360.0) * 255)
                h_data = [(i + hue_shift) % 255 for i in h_data]
                h.putdata(h_data)
                
                # 合并通道并转回RGB
                img = Image.merge('HSV', (h, s, v)).convert('RGB')
            
            # 转换回QPixmap
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            pixmap = QPixmap()
            pixmap.loadFromData(img_bytes.getvalue())
            
            # 更新显示
            self.current_screenshot = pixmap
            self.image_label.setPixmap(self.current_screenshot)
            
        except Exception as e:
            print(f"调整图片时出错: {str(e)}")
        
    def saveImage(self):
        """保存图片到文件"""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "保存截图",
            os.path.expanduser("~/Pictures/screenshot.png"),
            "PNG图片 (*.png);;JPEG图片 (*.jpg *.jpeg)"
        )
        
        if file_name:
            # 使用高质量设置保存图片
            self.current_screenshot.save(file_name, quality=100)
        
    def shareImage(self):
        # 将图片保存到剪贴板
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(self.current_screenshot)
        
        # 也可以添加其他分享方式，比如：
        # 1. 直接上传到图床
        # 2. 发送到其他应用
        # 3. 分享到社交媒体 
        
    def addToHistory(self):
        # 添加当前状态到历史记录
        self.history = self.history[:self.history_index + 1]
        self.history.append(self.current_screenshot.copy())
        self.history_index += 1
        self.updateUndoRedoButtons()
        
    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.current_screenshot = self.history[self.history_index].copy()
            self.image_label.setPixmap(self.current_screenshot)
            self.updateUndoRedoButtons()
            
    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_screenshot = self.history[self.history_index].copy()
            self.image_label.setPixmap(self.current_screenshot)
            self.updateUndoRedoButtons()
            
    def updateUndoRedoButtons(self):
        self.undo_btn.setEnabled(self.history_index > 0)
        self.redo_btn.setEnabled(self.history_index < len(self.history) - 1)
        
    def drawArrow(self, painter, start, end):
        try:
            # 计算箭头参数
            arrow_size = self.thickness_spin.value() * 3
            
            # 确保使用浮点数进行计算
            start_point = QPointF(float(start.x()), float(start.y()))
            end_point = QPointF(float(end.x()), float(end.y()))
            
            # 计算方向向量
            dx = end_point.x() - start_point.x()
            dy = end_point.y() - start_point.y()
            length = math.sqrt(dx * dx + dy * dy)
            
            if length < 1:  # 避免除以零
                return
                
            # 单位向量
            udx = dx / length
            udy = dy / length
            
            # 画箭头主线
            painter.drawLine(start_point, end_point)
            
            # 计算箭头两边的点
            # 箭头角度为30度（pi/6）
            angle1 = math.atan2(udy, udx) + math.pi/6
            angle2 = math.atan2(udy, udx) - math.pi/6
            
            arrow_p1 = QPointF(
                end_point.x() - arrow_size * math.cos(angle1),
                end_point.y() - arrow_size * math.sin(angle1)
            )
            arrow_p2 = QPointF(
                end_point.x() - arrow_size * math.cos(angle2),
                end_point.y() - arrow_size * math.sin(angle2)
            )
            
            # 画箭头两边
            painter.drawLine(end_point, arrow_p1)
            painter.drawLine(end_point, arrow_p2)
            
        except Exception as e:
            print(f"绘制箭头时出错: {str(e)}")
        
    def rotateImage(self, angle):
        # 旋转图片
        transform = QTransform().rotate(angle)
        self.current_screenshot = self.current_screenshot.transformed(transform)
        self.image_label.setPixmap(self.current_screenshot)
        self.addToHistory()
        
    def applyMosaic(self, painter, start, end):
        # 马赛克块的大小
        block_size = self.thickness_spin.value() * 5
        
        # 计算需要处理的矩形区域
        x1 = min(start.x(), end.x())
        y1 = min(start.y(), end.y())
        x2 = max(start.x(), end.x())
        y2 = max(start.y(), end.y())
        
        # 确保处理区域不超出图片范围
        x1 = max(0, x1 - block_size)
        y1 = max(0, y1 - block_size)
        x2 = min(self.current_screenshot.width(), x2 + block_size)
        y2 = min(self.current_screenshot.height(), y2 + block_size)
        
        # 获取图片数据
        image = self.current_screenshot.toImage()
        
        # 对区域内的每个块进行马赛克处理
        for x in range(x1, x2, block_size):
            for y in range(y1, y2, block_size):
                # 计算块的平均颜色
                r, g, b, count = 0, 0, 0, 0
                for dx in range(block_size):
                    for dy in range(block_size):
                        if x + dx < x2 and y + dy < y2:
                            pixel = image.pixel(x + dx, y + dy)
                            color = QColor(pixel)
                            r += color.red()
                            g += color.green()
                            b += color.blue()
                            count += 1
                
                if count > 0:
                    avg_color = QColor(r // count, g // count, b // count)
                    painter.fillRect(x, y, block_size, block_size, avg_color)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self.preview_point and self.draw_mode == 'pen':
            # 获取图片标签的位置
            label_pos = self.image_label.pos()
            # 转换预览点到窗口坐标系
            window_pos = QPoint(self.preview_point.x() + label_pos.x(),
                              self.preview_point.y() + label_pos.y())
            
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 绘制画笔预览圆圈
            painter.setPen(QPen(self.current_color, 1, Qt.PenStyle.SolidLine))
            painter.setBrush(QColor(self.current_color.red(), 
                                  self.current_color.green(),
                                  self.current_color.blue(), 
                                  100))
            radius = int(self.thickness_spin.value() / 2)
            painter.drawEllipse(window_pos, radius, radius)
            
            # 绘制十字线（确保十字线在圆圈中心）
            line_length = radius  # 使用画笔半径作为十字线长度
            painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.PenStyle.SolidLine))
            painter.drawLine(window_pos.x(), window_pos.y() - line_length,
                           window_pos.x(), window_pos.y() + line_length)
            painter.drawLine(window_pos.x() - line_length, window_pos.y(),
                           window_pos.x() + line_length, window_pos.y())
            
    def closeEvent(self, event):
        # 窗口关闭时清理临时文件
        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except:
                pass
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self.text_box.isVisible():
                self.text_box.hide()
                self.text_position = None
            else:
                self.confirmEdit()
        else:
            super().keyPressEvent(event)

    def chooseTextBackgroundColor(self):
        """选择文本背景色"""
        # 创建颜色对话框
        color_dialog = QColorDialog(self)
        color_dialog.setWindowTitle("选择文本背景色")
        color_dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel)
        
        # 添加完全透明的按钮
        transparent_button = QPushButton("完全透明", color_dialog)
        transparent_button.clicked.connect(lambda: self.setTextBackgroundTransparent(color_dialog))
        
        # 将按钮添加到对话框布局中
        layout = color_dialog.layout()
        if layout:
            layout.addWidget(transparent_button)
        
        if color_dialog.exec() == QColorDialog.DialogCode.Accepted:
            color = color_dialog.currentColor()
            if color.isValid():
                self.text_box.setBackgroundColor(color)
                
    def setTextBackgroundTransparent(self, dialog):
        """设置文本背景为完全透明"""
        transparent_color = QColor(255, 255, 255, 0)
        self.text_box.setBackgroundColor(transparent_color)
        dialog.close()

    def chooseTextBorderColor(self):
        """选择文本边框颜色和样式"""
        # 创建颜色对话框
        color_dialog = QColorDialog(self)
        color_dialog.setWindowTitle("设置文本边框")
        color_dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel)
        
        # 创建额外的控件
        extra_widget = QWidget(color_dialog)
        extra_layout = QVBoxLayout(extra_widget)
        
        # 添加边框粗细设置
        thickness_layout = QHBoxLayout()
        thickness_layout.addWidget(QLabel("边框粗细:"))
        
        # 创建数值输入组合控件
        thickness_widget = QWidget()
        thickness_input_layout = QHBoxLayout(thickness_widget)
        thickness_input_layout.setContentsMargins(0, 0, 0, 0)
        
        thickness_spin = QSpinBox()
        thickness_spin.setRange(1, 10)
        thickness_spin.setValue(self.text_box.border_width if self.text_box else 1)
        
        thickness_slider = QSlider(Qt.Orientation.Horizontal)
        thickness_slider.setRange(1, 10)
        thickness_slider.setValue(self.text_box.border_width if self.text_box else 1)
        
        # 连接信号
        thickness_spin.valueChanged.connect(thickness_slider.setValue)
        thickness_slider.valueChanged.connect(thickness_spin.setValue)
        
        thickness_input_layout.addWidget(thickness_spin)
        thickness_input_layout.addWidget(thickness_slider)
        
        thickness_layout.addWidget(thickness_widget)
        extra_layout.addLayout(thickness_layout)
        
        # 添加边框样式选择
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("边框样式:"))
        style_combo = QComboBox()
        style_combo.addItems(['实线', '虚线', '点线', '点划线', '双点划线'])
        style_map = {
            '实线': Qt.PenStyle.SolidLine,
            '虚线': Qt.PenStyle.DashLine,
            '点线': Qt.PenStyle.DotLine,
            '点划线': Qt.PenStyle.DashDotLine,
            '双点划线': Qt.PenStyle.DashDotDotLine
        }
        style_layout.addWidget(style_combo)
        extra_layout.addLayout(style_layout)
        
        # 添加完全透明的按钮
        transparent_button = QPushButton("完全透明", extra_widget)
        transparent_button.clicked.connect(lambda: self.setTextBorderTransparent(color_dialog))
        extra_layout.addWidget(transparent_button)
        
        # 将额外的控件添加到对话框
        layout = color_dialog.layout()
        if layout:
            layout.addWidget(extra_widget)
        
        if color_dialog.exec() == QColorDialog.DialogCode.Accepted:
            color = color_dialog.currentColor()
            if color.isValid():
                self.text_box.setBorderColor(color)
                self.text_box.setBorderWidth(thickness_spin.value())
                self.text_box.setBorderStyle(style_map[style_combo.currentText()])
                
    def setTextBorderTransparent(self, dialog):
        """设置文本边框为完全透明"""
        transparent_color = QColor(255, 255, 255, 0)
        self.text_box.setBorderColor(transparent_color)
        dialog.close()

    def loadCustomIcons(self):
        """加载自定义图标"""
        # 从设置中加载自定义图标
        for btn_name in ['rotate_left_icon', 'rotate_right_icon', 'undo_icon', 'redo_icon']:
            icon_path = self.settings.value(btn_name, '')
            if icon_path and os.path.exists(icon_path):
                btn = getattr(self, btn_name.replace('_icon', '_btn'), None)
                if btn:
                    btn.setIcon(QIcon(icon_path))
                    btn.setText('')  # 清除文本，只显示图标

    def showIconMenu(self, button, setting_key):
        """显示图标设置菜单"""
        menu = QMenu(self)
        
        # 选择自定义图标
        choose_action = menu.addAction('选择自定义图标')
        choose_action.triggered.connect(lambda: self.chooseCustomIcon(button, setting_key))
        
        # 重置为默认图标
        reset_action = menu.addAction('重置为默认图标')
        reset_action.triggered.connect(lambda: self.resetIcon(button, setting_key))
        
        # 在按钮位置显示菜单
        menu.exec(button.mapToGlobal(QPoint(0, button.height())))

    def chooseCustomIcon(self, button, setting_key):
        """选择自定义图标"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择图标",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.ico *.svg)"
        )
        
        if file_name:
            # 保存设置
            self.settings.setValue(setting_key, file_name)
            # 设置图标
            button.setIcon(QIcon(file_name))
            button.setText('')  # 清除文本，只显示图标

    def resetIcon(self, button, setting_key):
        """重置为默认图标"""
        # 清除设置
        self.settings.remove(setting_key)
        # 移除图标
        button.setIcon(QIcon())
        # 恢复默认文本
        default_text = {
            'rotate_left_icon': '↺',
            'rotate_right_icon': '↻',
            'undo_icon': '↩',
            'redo_icon': '↪'
        }
        button.setText(default_text.get(setting_key, ''))