from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PySide6.QtCore import Qt


class InfoCard(QFrame):

    def __init__(self, title, value):

        super().__init__()

        self.setMinimumHeight(170)

        self.setStyleSheet("""
        QFrame{
            background:#323844;
            border-radius:18px;
        }
        """)

        layout = QVBoxLayout(self)

        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignCenter)

        self.title.setStyleSheet("""
        color:#BFC5D2;
        font-size:18px;
        """)

        self.value = QLabel(value)
        self.value.setAlignment(Qt.AlignCenter)

        self.value.setStyleSheet("""
        color:white;
        font-size:34px;
        font-weight:bold;
        """)

        layout.addStretch()
        layout.addWidget(self.title)
        layout.addWidget(self.value)
        layout.addStretch()

    def setValue(self, text):
        self.value.setText(text)