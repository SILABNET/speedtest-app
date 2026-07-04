from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QStackedWidget
)

from PySide6.QtCore import Qt

from ui.dashboard import Dashboard


class SidebarButton(QPushButton):

    def __init__(self, text):

        super().__init__(text)

        self.setCursor(Qt.PointingHandCursor)

        self.setMinimumHeight(52)

        self.setStyleSheet("""

        QPushButton{

            background:transparent;

            color:white;

            border:none;

            text-align:left;

            padding-left:18px;

            font-size:15px;

            border-radius:12px;

        }

        QPushButton:hover{

            background:#2F3542;

        }

        """)


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("SPEEDTEST APP")

        self.resize(1450,850)

        self.setMinimumSize(1200,700)

        root = QWidget()

        self.setCentralWidget(root)

        layout = QHBoxLayout(root)

        layout.setContentsMargins(0,0,0,0)

        layout.setSpacing(0)

        ###################################################
        # Sidebar
        ###################################################

        sidebar = QFrame()

        sidebar.setFixedWidth(240)

        sidebar.setStyleSheet("""

        QFrame{

            background:#181C24;

        }

        """)

        side = QVBoxLayout(sidebar)

        side.setContentsMargins(15,20,15,20)

        ###################################################

        logo = QLabel("⚡ SPEEDTEST")

        logo.setAlignment(Qt.AlignCenter)

        logo.setStyleSheet("""

        color:white;

        font-size:28px;

        font-weight:bold;

        padding:10px;

        """)

        side.addWidget(logo)

        side.addSpacing(20)

        ###################################################

        self.dashboardButton = SidebarButton("🏠 Dashboard")
        self.historyButton = SidebarButton("📈 Verlauf")
        self.networkButton = SidebarButton("🌐 Netzwerk")
        self.analysisButton = SidebarButton("📊 Analyse")
        self.settingsButton = SidebarButton("⚙ Einstellungen")

        side.addWidget(self.dashboardButton)
        side.addWidget(self.historyButton)
        side.addWidget(self.networkButton)
        side.addWidget(self.analysisButton)
        side.addWidget(self.settingsButton)

        side.addStretch()

        ###################################################

        version = QLabel("Version 1.0")

        version.setAlignment(Qt.AlignCenter)

        version.setStyleSheet("""

        color:gray;

        font-size:12px;

        """)

        side.addWidget(version)

        ###################################################
        # Hauptbereich
        ###################################################

        self.pages = QStackedWidget()

        self.pages.setStyleSheet("""

        background:#20242C;

        """)

        ###################################################
        # Dashboard
        ###################################################

        self.dashboard = Dashboard()

        self.pages.addWidget(self.dashboard)

        ###################################################
        # Platzhalterseiten
        ###################################################

        self.historyPage = self.placeholder(
            "📈 Verlauf",
            "Hier erscheinen später alle Speedtests."
        )

        self.networkPage = self.placeholder(
            "🌐 Netzwerk",
            "Netzwerkinformationen folgen."
        )

        self.analysisPage = self.placeholder(
            "📊 Analyse",
            "Internetanalyse folgt."
        )

        self.settingsPage = self.placeholder(
            "⚙ Einstellungen",
            "Einstellungen folgen."
        )

        self.pages.addWidget(self.historyPage)
        self.pages.addWidget(self.networkPage)
        self.pages.addWidget(self.analysisPage)
        self.pages.addWidget(self.settingsPage)

        ###################################################

        self.dashboardButton.clicked.connect(
            lambda: self.pages.setCurrentIndex(0)
        )

        self.historyButton.clicked.connect(
            lambda: self.pages.setCurrentIndex(1)
        )

        self.networkButton.clicked.connect(
            lambda: self.pages.setCurrentIndex(2)
        )

        self.analysisButton.clicked.connect(
            lambda: self.pages.setCurrentIndex(3)
        )

        self.settingsButton.clicked.connect(
            lambda: self.pages.setCurrentIndex(4)
        )

        ###################################################

        layout.addWidget(sidebar)

        layout.addWidget(self.pages)

    ########################################################

    def placeholder(self, title, text):

        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setAlignment(Qt.AlignCenter)

        titleLabel = QLabel(title)

        titleLabel.setStyleSheet("""

        color:white;

        font-size:34px;

        font-weight:bold;

        """)

        info = QLabel(text)

        info.setStyleSheet("""

        color:#B6BDC8;

        font-size:18px;

        """)

        layout.addWidget(titleLabel)

        layout.addWidget(info)

        return page