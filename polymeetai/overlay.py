from PySide6.QtCore import Qt, Signal, QObject, QPoint
from PySide6.QtGui import QFont, QMouseEvent
from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout
from .config import Config

class SubtitleBridge(QObject):
    new_text = Signal(str)

class SubtitleWindow(QWidget):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # Using QTextEdit for scrollable history
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("""
            QTextEdit {
                color: white;
                background-color: rgba(0,0,0,180);
                padding: 15px;
                border-radius: 10px;
                font-family: -apple-system, "SF Pro Display", sans-serif;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255,255,255,100);
                border-radius: 4px;
            }
        """)
        self.text_area.setFont(QFont("SF Pro Display", 18))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.text_area)

        self._drag_pos: QPoint | None = None
        self._resize_and_place()

    def _resize_and_place(self):
        screen = self.screen().geometry()
        # Made it taller to show more history
        w = self.cfg.overlay_width
        h = 300 
        self.setGeometry(
            (screen.width() - w) // 2,
            screen.height() - h - self.cfg.overlay_bottom_margin,
            w, h
        )

    def push_text(self, text: str):
        # Append new text instead of replacing it
        self.text_area.append(text)
        # Auto-scroll to the bottom
        self.text_area.verticalScrollBar().setValue(self.text_area.verticalScrollBar().maximum())

    # --- Dragging Logic ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None
        event.accept()
