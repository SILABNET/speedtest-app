import speedtest
import time

from PySide6.QtCore import QThread, Signal


class SpeedTestWorker(QThread):

    progress = Signal(str, float)   # "download/upload/ping", value
    finished = Signal(float, float, float)
    error = Signal(str)

    def run(self):

        try:

            st = speedtest.Speedtest()
            st.get_best_server()

            # ---------------------------
            # DOWNLOAD TEST (LIVE)
            # ---------------------------
            download_speed = st.download()

            self.progress.emit("download", download_speed / 1_000_000)

            # ---------------------------
            # UPLOAD TEST (LIVE)
            # ---------------------------
            upload_speed = st.upload()

            self.progress.emit("upload", upload_speed / 1_000_000)

            # ---------------------------
            # PING
            # ---------------------------
            ping = st.results.ping

            self.progress.emit("ping", ping)

            self.finished.emit(
                download_speed / 1_000_000,
                upload_speed / 1_000_000,
                ping
            )

        except Exception as e:
            self.error.emit(str(e))