import pyqtgraph as pg
from PySide6.QtGui import QPen, QColor
from PySide6.QtCore import Qt


class LiveGraph(pg.PlotWidget):
    def __init__(self):
        super().__init__()

        self.setBackground("#2A2F38")
        self.setMinimumHeight(260)

        self.showGrid(x=True, y=True, alpha=0.18)
        self.setMenuEnabled(False)
        self.setMouseEnabled(x=False, y=False)
        self.hideButtons()

        self.setClipToView(True)
        self.setAntialiasing(True)

        self.setTitle("", color="w")

        # Achsen-Style
        axis_pen = pg.mkPen("#6B7280")
        text_pen = pg.mkPen("#C7CEDA")
        for axis in ("left", "bottom"):
            ax = self.getAxis(axis)
            ax.setPen(axis_pen)
            ax.setTextPen(text_pen)
            ax.setStyle(showValues=True)

        self.getAxis("left").setTickFont(self.font())
        self.getAxis("bottom").setTickFont(self.font())

        # Daten
        self.x = []
        self.y = []
        self.max_points = 60

        # Hauptkurve
        line_pen = QPen(QColor("#3B82F6"))
        line_pen.setWidth(3)
        line_pen.setCapStyle(Qt.RoundCap)
        line_pen.setJoinStyle(Qt.RoundJoin)

        self.curve = self.plot(
            [],
            [],
            pen=line_pen,
            antialias=True,
        )

        # Fläche unter der Kurve
        self.fill = pg.FillBetweenItem(
            self.curve,
            pg.PlotDataItem([], []),
            brush=pg.mkBrush(59, 130, 246, 40),
        )
        self.addItem(self.fill)

        # Optional: leichte Referenzlinie
        self.avg_line = pg.InfiniteLine(
            angle=0,
            pos=0,
            pen=pg.mkPen("#4B5563", style=Qt.DashLine),
        )
        self.addItem(self.avg_line)

    def reset(self):
        self.x = []
        self.y = []
        self.curve.setData([], [])
        self.fill.curve2 = pg.PlotDataItem([], [])
        self.avg_line.setPos(0)
        self.enableAutoRange()

    def addPoint(self, value):
        self.x.append(len(self.x))
        self.y.append(float(value))

        if len(self.x) > self.max_points:
            self.x = self.x[-self.max_points :]
            self.y = self.y[-self.max_points :]

        self.curve.setData(self.x, self.y)
        self.fill.curve2 = pg.PlotDataItem(self.x, [0] * len(self.x))
        self.avg_line.setPos(sum(self.y) / len(self.y) if self.y else 0)

        self.setXRange(
            max(0, len(self.x) - self.max_points),
            max(self.max_points, len(self.x)),
            padding=0.02,
        )

        if self.y:
            ymax = max(self.y)
            self.setYRange(0, max(10, ymax * 1.15), padding=0.08)