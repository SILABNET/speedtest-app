from PySide6.QtWidgets import QWidget
from PySide6.QtGui import *
from PySide6.QtCore import Qt
import math


class SpeedGauge(QWidget):

    def __init__(self):

        super().__init__()

        self.value = 0
        self.maximum = 1000

        self.setMinimumSize(340,340)

    def setValue(self,value):

        self.value = value
        self.update()

    def paintEvent(self,event):

        p = QPainter(self)

        p.setRenderHint(QPainter.Antialiasing)

        w=self.width()
        h=self.height()

        rect=self.rect().adjusted(20,20,-20,-20)

        pen=QPen(QColor("#303643"),18)

        p.setPen(pen)

        p.drawArc(rect,225*16,-270*16)

        angle=(self.value/self.maximum)*270

        if self.value <100:
            color="#EF4444"

        elif self.value<300:
            color="#F59E0B"

        else:
            color="#22C55E"

        pen=QPen(QColor(color),18)

        p.setPen(pen)

        p.drawArc(rect,225*16,-angle*16)

        p.setPen(Qt.white)

        font=QFont()

        font.setPointSize(30)

        font.setBold(True)

        p.setFont(font)

        p.drawText(rect,Qt.AlignCenter,f"{self.value:.1f}")

        font.setPointSize(14)

        font.setBold(False)

        p.setFont(font)

        p.drawText(rect.adjusted(0,70,0,0),Qt.AlignCenter,"Mbps")