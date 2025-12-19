from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton,
    QProgressBar, QMessageBox, QFileDialog, QComboBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from workers.download_worker import DownloadWorker
from utils.validator import is_valid_youtube_url
from utils.metadata import fetch_metadata


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YouTube Pro Max")
        self.resize(500, 650)

        # ===== Widgets =====
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube / Shorts URL")

        self.preview_label = QLabel("Preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setFixedHeight(180)

        self.title_label = QLabel("")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)

        self.path_button = QPushButton("Choose Download Folder")
        self.path_button.clicked.connect(self.choose_path)
        self.download_path = ""

        self.format_box = QComboBox()
        self.format_box.addItems(["mp4", "mp3"])

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.speed_label = QLabel("Speed: --")
        self.eta_label = QLabel("ETA: --")

        self.download_button = QPushButton("Download")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)

        # ===== Layout =====
        layout = QVBoxLayout(self)
        layout.addWidget(self.url_input)
        layout.addWidget(self.preview_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.path_button)
        layout.addWidget(self.format_box)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.speed_label)
        layout.addWidget(self.eta_label)
        layout.addWidget(self.download_button)
        layout.addWidget(self.cancel_button)

        # ===== Signals =====
        self.url_input.textChanged.connect(self.load_preview)
        self.download_button.clicked.connect(self.start_download)
        self.cancel_button.clicked.connect(self.cancel_download)

        self.worker = None

    # =========================
    # Choose folder
    # =========================
    def choose_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.download_path = folder

    # =========================
    # Load preview
    # =========================
    def load_preview(self):
        url = self.url_input.text().strip()

        if not is_valid_youtube_url(url):
            self.preview_label.clear()
            self.title_label.clear()
            return

        try:
            title, image_data = fetch_metadata(url)
            self.title_label.setText(title or "Unknown title")

            if image_data:
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                self.preview_label.setPixmap(
                    pixmap.scaled(
                        320, 180,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )
        except Exception:
            self.title_label.setText("Failed to load preview")
            self.preview_label.clear()

    # =========================
    # Start download
    # =========================
    def start_download(self):
        url = self.url_input.text().strip()

        if not is_valid_youtube_url(url):
            QMessageBox.warning(self, "Error", "Invalid YouTube URL")
            return

        if not self.download_path:
            QMessageBox.warning(self, "Error", "Choose download folder")
            return

        # UI state
        self.progress_bar.setValue(0)
        self.speed_label.setText("Speed: --")
        self.eta_label.setText("ETA: --")
        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        # Worker
        self.worker = DownloadWorker(
            url,
            self.download_path,
            self.format_box.currentText()
        )

        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.speed.connect(
            lambda s: self.speed_label.setText(f"Speed: {s}")
        )
        self.worker.eta.connect(
            lambda e: self.eta_label.setText(f"ETA: {e}")
        )
        self.worker.finished.connect(self.download_finished)
        self.worker.error.connect(self.download_error)

        self.worker.start()

    # =========================
    # Cancel download
    # =========================
    def cancel_download(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
        self.reset_ui()

    # =========================
    # Finished
    # =========================
    def download_finished(self):
        QMessageBox.information(self, "Done", "Download completed")
        self.reset_ui()

    # =========================
    # Error
    # =========================
    def download_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.reset_ui()

    # =========================
    # Reset UI
    # =========================
    def reset_ui(self):
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.speed_label.setText("Speed: --")
        self.eta_label.setText("ETA: --")
