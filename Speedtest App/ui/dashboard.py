from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QProgressBar,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from ui.gauge import SpeedGauge
from ui.graph import LiveGraph
from backend.speedtest_worker import SpeedTestWorker


class MetricCard(QFrame):
    def __init__(self, title: str, value: str, subtitle: str = ""):
        super().__init__()

        self.setObjectName("metricCard")
        self.setMinimumHeight(120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        self.titleLabel = QLabel(title)
        self.titleLabel.setObjectName("metricTitle")

        self.valueLabel = QLabel(value)
        self.valueLabel.setObjectName("metricValue")

        self.subtitleLabel = QLabel(subtitle)
        self.subtitleLabel.setObjectName("metricSubtitle")

        layout.addWidget(self.titleLabel)
        layout.addWidget(self.valueLabel)
        layout.addWidget(self.subtitleLabel)
        layout.addStretch()

    def set_value(self, value: str):
        self.valueLabel.setText(value)

    def set_subtitle(self, text: str):
        self.subtitleLabel.setText(text)

    def set_title(self, text: str):
        self.titleLabel.setText(text)


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("dashboardRoot")
        self.setStyleSheet("""
            QWidget#dashboardRoot {
                background: #20242C;
            }

            QLabel {
                color: white;
            }

            QFrame#panel {
                background: #2A2F38;
                border-radius: 20px;
            }

            QFrame#metricCard {
                background: #2A2F38;
                border-radius: 18px;
            }

            QLabel#pageTitle {
                font-size: 34px;
                font-weight: 800;
                color: white;
            }

            QLabel#pageSubtitle {
                font-size: 14px;
                color: #AAB2C0;
            }

            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: 700;
                color: white;
            }

            QLabel#metricTitle {
                font-size: 14px;
                color: #C7CEDA;
                font-weight: 600;
            }

            QLabel#metricValue {
                font-size: 30px;
                font-weight: 800;
                color: white;
            }

            QLabel#metricSubtitle {
                font-size: 12px;
                color: #98A2B3;
            }

            QLabel#statusChip {
                padding: 10px 14px;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 700;
                background: #1F2937;
                color: #D1D5DB;
            }

            QPushButton#startButton {
                background: #2563EB;
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 18px;
                font-weight: 800;
                padding: 16px;
            }

            QPushButton#startButton:hover {
                background: #3B82F6;
            }

            QPushButton#startButton:disabled {
                background: #44506A;
                color: #B9C2D3;
            }

            QProgressBar {
                border: none;
                background: #1F2430;
                border-radius: 10px;
                height: 14px;
                text-align: center;
                color: transparent;
            }

            QProgressBar::chunk {
                border-radius: 10px;
                background: #3B82F6;
            }
        """)

        self._build_ui()

        self.worker = None
        self._animation_timer = QTimer(self)
        self._animation_timer.setInterval(16)
        self._animation_timer.timeout.connect(self._animate_step)

        self._anim_kind = None
        self._anim_start = 0.0
        self._anim_target = 0.0
        self._anim_step = 0
        self._anim_steps = 24
        self._last_download = 0.0
        self._last_upload = 0.0
        self._current_stage = "idle"

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        headerRow = QHBoxLayout()
        headerRow.setSpacing(12)

        titleBox = QVBoxLayout()
        titleBox.setSpacing(4)

        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Live Internet Speed Analyse mit Bewertung in Echtzeit")
        subtitle.setObjectName("pageSubtitle")

        titleBox.addWidget(title)
        titleBox.addWidget(subtitle)

        headerRow.addLayout(titleBox)
        headerRow.addStretch()

        self.statusChip = QLabel("Bereit")
        self.statusChip.setObjectName("statusChip")
        self.statusChip.setAlignment(Qt.AlignCenter)
        headerRow.addWidget(self.statusChip)

        root.addLayout(headerRow)

        topRow = QHBoxLayout()
        topRow.setSpacing(16)

        self.gaugePanel = QFrame()
        self.gaugePanel.setObjectName("panel")
        gaugeLayout = QVBoxLayout(self.gaugePanel)
        gaugeLayout.setContentsMargins(18, 18, 18, 18)
        gaugeLayout.setSpacing(8)

        gaugeTitle = QLabel("Download-Geschwindigkeit")
        gaugeTitle.setObjectName("sectionTitle")
        gaugeTitle.setAlignment(Qt.AlignCenter)

        self.gauge = SpeedGauge()
        self.gauge.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.gaugeHint = QLabel("Noch kein Test gestartet")
        self.gaugeHint.setAlignment(Qt.AlignCenter)
        self.gaugeHint.setStyleSheet("color:#B6BDC8; font-size:13px;")

        gaugeLayout.addWidget(gaugeTitle)
        gaugeLayout.addWidget(self.gauge, 1)
        gaugeLayout.addWidget(self.gaugeHint)

        self.graphPanel = QFrame()
        self.graphPanel.setObjectName("panel")
        graphLayout = QVBoxLayout(self.graphPanel)
        graphLayout.setContentsMargins(18, 18, 18, 18)
        graphLayout.setSpacing(8)

        graphTitle = QLabel("Live-Diagramm")
        graphTitle.setObjectName("sectionTitle")

        self.graph = LiveGraph()
        self.graph.setMinimumHeight(260)

        self.graphHint = QLabel("Download und Upload werden hier live sichtbar")
        self.graphHint.setStyleSheet("color:#B6BDC8; font-size:13px;")

        graphLayout.addWidget(graphTitle)
        graphLayout.addWidget(self.graph, 1)
        graphLayout.addWidget(self.graphHint)

        topRow.addWidget(self.gaugePanel, 1)
        topRow.addWidget(self.graphPanel, 2)

        root.addLayout(topRow)

        statsRow = QHBoxLayout()
        statsRow.setSpacing(16)

        self.downloadCard = MetricCard("Download", "-- Mbps", "Warte auf Testergebnis")
        self.uploadCard = MetricCard("Upload", "-- Mbps", "Warte auf Testergebnis")
        self.pingCard = MetricCard("Ping", "-- ms", "Warte auf Testergebnis")

        statsRow.addWidget(self.downloadCard)
        statsRow.addWidget(self.uploadCard)
        statsRow.addWidget(self.pingCard)

        root.addLayout(statsRow)

        summaryRow = QHBoxLayout()
        summaryRow.setSpacing(16)

        self.qualityCard = MetricCard("Internetqualität", "Bereit", "Bewertung nach dem Test")
        self.qualityCard.setMinimumHeight(130)

        self.gamingCard = MetricCard("Gaming", "—", "CS2, Fortnite, Minecraft")
        self.streamingCard = MetricCard("Streaming", "—", "YouTube, Netflix, Twitch")

        summaryRow.addWidget(self.qualityCard, 2)
        summaryRow.addWidget(self.gamingCard, 1)
        summaryRow.addWidget(self.streamingCard, 1)

        root.addLayout(summaryRow)

        controlRow = QHBoxLayout()
        controlRow.setSpacing(12)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)

        self.button = QPushButton("Start Speedtest")
        self.button.setObjectName("startButton")
        self.button.setMinimumHeight(58)
        self.button.clicked.connect(self.start_test)

        controlRow.addWidget(self.progress, 3)
        controlRow.addWidget(self.button, 1)

        root.addLayout(controlRow)
        root.addStretch()

    def start_test(self):
        self._reset_ui_for_test()

        self.worker = SpeedTestWorker()
        self.worker.progress.connect(self.update_live)
        self.worker.finished.connect(self.done)
        self.worker.error.connect(self.error)
        self.worker.start()

        self.button.setEnabled(False)
        self.statusChip.setText("Test läuft...")
        self.progress.setValue(5)

    def _reset_ui_for_test(self):
        self._animation_timer.stop()

        self._anim_kind = None
        self._anim_start = 0.0
        self._anim_target = 0.0
        self._anim_step = 0

        self._last_download = 0.0
        self._last_upload = 0.0
        self._current_stage = "download"

        self.graph.x = []
        self.graph.y = []
        self.graph.curve.setData([], [])

        self.gauge.setValue(0)
        self.gaugeHint.setText("Test wird vorbereitet...")

        self.downloadCard.set_value("-- Mbps")
        self.downloadCard.set_subtitle("Noch kein Ergebnis")
        self.uploadCard.set_value("-- Mbps")
        self.uploadCard.set_subtitle("Noch kein Ergebnis")
        self.pingCard.set_value("-- ms")
        self.pingCard.set_subtitle("Noch kein Ergebnis")

        self.qualityCard.set_value("Wird berechnet...")
        self.qualityCard.set_subtitle("Analyse läuft")
        self.gamingCard.set_value("—")
        self.streamingCard.set_value("—")

        self.statusChip.setText("Bereit")
        self.progress.setValue(0)

    def update_live(self, typ, value):
        if typ == "download":
            self._last_download = float(value)
            self.downloadCard.set_value(f"{value:.2f} Mbps")
            self.downloadCard.set_subtitle(self._rate_download(value))

            self.statusChip.setText(self._rate_download(value))
            self.gaugeHint.setText("Download läuft...")
            self._start_animation("download", float(value))

            self.progress.setValue(45)

        elif typ == "upload":
            self._last_upload = float(value)
            self.uploadCard.set_value(f"{value:.2f} Mbps")
            self.uploadCard.set_subtitle(self._rate_upload(value))

            self.statusChip.setText(self._rate_upload(value))
            self.gaugeHint.setText("Upload läuft...")
            self._start_animation("upload", float(value))

            self.progress.setValue(80)

        elif typ == "ping":
            self.pingCard.set_value(f"{value:.1f} ms")
            self.pingCard.set_subtitle(self._rate_ping(value))

            self.statusChip.setText(self._rate_ping(value))
            self.progress.setValue(90)

    def _start_animation(self, kind: str, target: float):
        self._anim_kind = kind
        self._anim_start = self.gauge.value
        self._anim_target = max(0.0, float(target))
        self._anim_step = 0
        self._animation_timer.start()

    def _animate_step(self):
        if self._anim_kind is None:
            self._animation_timer.stop()
            return

        self._anim_step += 1
        progress = min(self._anim_step / self._anim_steps, 1.0)

        # leichte Ease-Out-Kurve
        eased = 1 - (1 - progress) * (1 - progress)
        current = self._anim_start + (self._anim_target - self._anim_start) * eased

        self.gauge.setValue(current)

        if self._anim_kind in ("download", "upload"):
            self.graph.addPoint(current)

        self._update_quality_preview()

        if progress >= 1.0:
            self._animation_timer.stop()

    def _update_quality_preview(self):
        score = self._overall_score(self._last_download, self._last_upload, None)
        label, tone = self._quality_label(score)

        self.qualityCard.set_value(label)
        self.qualityCard.set_subtitle(f"Qualität: {score:.0f}/100 • {tone}")

        gaming = self._gaming_score(self._last_download, self._last_upload)
        streaming = self._streaming_score(self._last_download, self._last_upload)

        self.gamingCard.set_value(gaming)
        self.streamingCard.set_value(streaming)

    def done(self, down, up, ping):
        self._animation_timer.stop()

        self._last_download = float(down)
        self._last_upload = float(up)

        self.gauge.setValue(down)
        self.gaugeHint.setText("Test abgeschlossen")

        self.downloadCard.set_value(f"{down:.2f} Mbps")
        self.downloadCard.set_subtitle(self._rate_download(down))

        self.uploadCard.set_value(f"{up:.2f} Mbps")
        self.uploadCard.set_subtitle(self._rate_upload(up))

        self.pingCard.set_value(f"{ping:.1f} ms")
        self.pingCard.set_subtitle(self._rate_ping(ping))

        score = self._overall_score(down, up, ping)
        quality_label, tone = self._quality_label(score)

        self.qualityCard.set_value(quality_label)
        self.qualityCard.set_subtitle(f"Qualität: {score:.0f}/100 • {tone}")

        self.gamingCard.set_value(self._gaming_score(down, up))
        self.streamingCard.set_value(self._streaming_score(down, up))

        self.statusChip.setText(f"Fertig • {quality_label}")
        self.progress.setValue(100)

        self.button.setEnabled(True)
        self.button.setText("Erneut testen")

    def error(self, msg):
        self._animation_timer.stop()

        self.statusChip.setText("Fehler")
        self.gaugeHint.setText("Speedtest fehlgeschlagen")
        self.graphHint.setText("Es konnte kein Ergebnis erzeugt werden")

        self.qualityCard.set_value("Fehler")
        self.qualityCard.set_subtitle(msg)

        self.button.setEnabled(True)
        self.button.setText("Start Speedtest")

    def _rate_download(self, mbps: float) -> str:
        if mbps >= 500:
            return "🟢 Ausgezeichnet"
        if mbps >= 200:
            return "🟢 Sehr gut"
        if mbps >= 100:
            return "🟡 Gut"
        if mbps >= 50:
            return "🟠 Mittel"
        return "🔴 Langsam"

    def _rate_upload(self, mbps: float) -> str:
        if mbps >= 100:
            return "🟢 Ausgezeichnet"
        if mbps >= 50:
            return "🟢 Sehr gut"
        if mbps >= 20:
            return "🟡 Gut"
        if mbps >= 10:
            return "🟠 Mittel"
        return "🔴 Langsam"

    def _rate_ping(self, ping_ms: float) -> str:
        if ping_ms < 10:
            return "🟢 Perfekt"
        if ping_ms < 20:
            return "🟢 Sehr gut"
        if ping_ms < 40:
            return "🟡 Gut"
        if ping_ms < 80:
            return "🟠 Mittel"
        return "🔴 Schlecht"

    def _overall_score(self, download: float | None, upload: float | None, ping: float | None) -> float:
        download = download or 0.0
        upload = upload or 0.0
        ping = ping or 0.0

        # einfache, verständliche Gesamtskala 0–100
        d_score = min(download / 8.0, 1.0) * 100.0
        u_score = min(upload / 3.0, 1.0) * 100.0
        p_score = 100.0 if ping == 0 else max(0.0, 100.0 - (ping * 1.2))

        return (d_score * 0.55) + (u_score * 0.25) + (p_score * 0.20)

    def _quality_label(self, score: float) -> tuple[str, str]:
        if score >= 85:
            return "🟢 Ausgezeichnet", "Top-Verbindung"
        if score >= 70:
            return "🟢 Sehr gut", "Sehr stabil"
        if score >= 55:
            return "🟡 Gut", "Alltagstauglich"
        if score >= 35:
            return "🟠 Mittel", "Spürbare Limits"
        return "🔴 Schwach", "Auffällig langsam"

    def _gaming_score(self, download: float, upload: float) -> str:
        if download >= 300 and upload >= 30:
            return "★★★★★"
        if download >= 150 and upload >= 20:
            return "★★★★☆"
        if download >= 75 and upload >= 10:
            return "★★★☆☆"
        if download >= 25 and upload >= 5:
            return "★★☆☆☆"
        return "★☆☆☆☆"

    def _streaming_score(self, download: float, upload: float) -> str:
        if download >= 200:
            return "★★★★★"
        if download >= 100:
            return "★★★★☆"
        if download >= 50:
            return "★★★☆☆"
        if download >= 20:
            return "★★☆☆☆"
        return "★☆☆☆☆"