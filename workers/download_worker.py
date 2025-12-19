from PyQt6.QtCore import QThread, pyqtSignal
import yt_dlp
import os
import re
import time

ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    speed = pyqtSignal(str)
    eta = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, url: str, folder: str, mode: str):
        super().__init__()
        self.url = url
        self.folder = folder
        self.mode = mode
        self._stop = False

    def stop(self):
        self._stop = True

    def _clean(self, text):
        if not text:
            return ""
        return ANSI_ESCAPE.sub("", text).strip()

    def hook(self, d):
        if self._stop:
            raise Exception("Download cancelled")

        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)

            if total:
                percent = int(downloaded / total * 100)
                self.progress.emit(percent)

            speed = d.get("speed")
            if speed:
                self.speed.emit(f"{speed/1024/1024:.2f} MB/s")

            eta = d.get("eta")
            if eta:
                self.eta.emit(time.strftime("%H:%M:%S", time.gmtime(eta)))

        elif d["status"] == "finished":
            self.progress.emit(100)

    def run(self):
        try:
            outtmpl = os.path.join(self.folder, "%(title)s.%(ext)s")

            if self.mode == "mp3":
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": outtmpl,
                    "progress_hooks": [self.hook],
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "320",
                    }],
                    "quiet": True,
                }
            else:
                ydl_opts = {
                    "format": "bestvideo+bestaudio/best",
                    "merge_output_format": "mp4",
                    "outtmpl": outtmpl,
                    "progress_hooks": [self.hook],
                    "quiet": True,
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))
