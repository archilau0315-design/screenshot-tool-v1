from PyQt6.QtCore import Qt

class CursorRules:
    @staticmethod
    def get_cursor_for_tool(tool_name):
        """
        根据工具类型返回对应的光标样式
        """
        cursor_map = {
            'pen': Qt.CursorShape.CrossCursor,
            'rect': Qt.CursorShape.CrossCursor,
            'circle': Qt.CursorShape.CrossCursor,
            'text': Qt.CursorShape.IBeamCursor,
            'arrow': Qt.CursorShape.CrossCursor,
            'mosaic': Qt.CursorShape.CrossCursor,
            'floating_icon': Qt.CursorShape.PointingHandCursor,
            'screenshot': Qt.CursorShape.CrossCursor,
        }
        return cursor_map.get(tool_name, Qt.CursorShape.ArrowCursor)  # 默认使用箭头光标
    
    @staticmethod
    def get_cursor_for_widget(widget_name):
        """
        根据控件类型返回对应的光标样式
        """
        cursor_map = {
            'floating_icon': Qt.CursorShape.PointingHandCursor,
            'button': Qt.CursorShape.PointingHandCursor,
            'slider': Qt.CursorShape.PointingHandCursor,
            'spinbox': Qt.CursorShape.IBeamCursor,
            'text_input': Qt.CursorShape.IBeamCursor,
        }
        return cursor_map.get(widget_name, Qt.CursorShape.ArrowCursor)  # 默认使用箭头光标 