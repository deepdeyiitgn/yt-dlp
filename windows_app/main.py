import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox,
    QFileDialog, QProgressBar, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import yt_dlp

class DownloadThread(QThread):
    progress = pyqtSignal(float)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url, ydl_opts):
        super().__init__()
        self.url = url
        self.ydl_opts = ydl_opts

    def run(self):
        self._last_filename = None
        def hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
                downloaded = d.get('downloaded_bytes', 0)
                percent = int(downloaded / total * 100)
                self.progress.emit(percent)
            elif d['status'] == 'finished':
                self._last_filename = d.get('filename')
        self.ydl_opts['progress_hooks'] = [hook]
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([self.url])
            if self._last_filename:
                self.finished.emit(self._last_filename)
            else:
                self.finished.emit('Download finished')
        except Exception as e:
            self.error.emit(str(e))


class YTDLPApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('QuickFile - Download any Content in One Place')
        self.setGeometry(200, 200, 480, 480)
        self.last_folder = None
        self.remember_folder = False
        self.formats = []
        self.qualities = []
        self.init_ui()
        self.load_stylesheet()

    def init_ui(self):
        layout = QVBoxLayout()
        self.title_label = QLabel('QuickFile - Download any Content in One Place')
        self.title_label.setObjectName('titleLabel')
        layout.addWidget(self.title_label)

        layout.addWidget(QLabel('Paste video/audio link:'))
        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

        layout.addWidget(QLabel('Download type:'))
        self.type_combo = QComboBox()
        self.type_combo.addItems(['Video', 'Audio'])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        layout.addWidget(self.type_combo)

        layout.addWidget(QLabel('Format:'))
        self.format_combo = QComboBox()
        layout.addWidget(self.format_combo)

        layout.addWidget(QLabel('Quality:'))
        self.quality_combo = QComboBox()
        layout.addWidget(self.quality_combo)

        self.download_btn = QPushButton('Download')
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.remember_checkbox = QCheckBox('Always use this folder for downloads')
        self.remember_checkbox.stateChanged.connect(self.toggle_remember_folder)
        layout.addWidget(self.remember_checkbox)

        self.footer_label = QLabel('© 2025 Quicklink | All Right Reserved')
        self.footer_label.setObjectName('footerLabel')
        layout.addWidget(self.footer_label)

        self.setLayout(layout)
        self.on_type_changed()

    def load_stylesheet(self):
        qss_path = os.path.join(os.path.dirname(__file__), 'style.qss')
        if os.path.exists(qss_path):
            with open(qss_path, 'r') as f:
                self.setStyleSheet(f.read())

    def toggle_remember_folder(self, state):
        self.remember_folder = state == Qt.Checked

    def on_type_changed(self):
        # Placeholder: will be replaced with dynamic format fetching
        if self.type_combo.currentText().lower() == 'video':
            formats = ['mp4', 'webm', 'mkv', 'flv', 'mov', 'avi']
        else:
            formats = ['mp3', 'm4a', 'flac', 'wav', 'aac', 'opus']
        self.format_combo.clear()
        self.format_combo.addItems(formats)
        self.quality_combo.clear()
        self.quality_combo.addItems([
            'best', 'worst', '180p', '240p', '360p', '480p', '720p', '1080p', '2k', '4k',
            '30fps', '60fps', '24fps', '25fps', 'custom'
        ])

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, 'Error', 'Please enter a URL.')
            return
        download_type = self.type_combo.currentText().lower()
        file_format = self.format_combo.currentText()
        quality = self.quality_combo.currentText()

        if self.remember_folder and self.last_folder:
            folder = self.last_folder
        else:
            folder = QFileDialog.getExistingDirectory(self, 'Select Download Folder')
            if not folder:
                return
            self.last_folder = folder

        outtmpl = os.path.join(folder, '%(title)s.%(ext)s')
        ydl_opts = {
            'outtmpl': outtmpl,
            'format': self.get_format_string(download_type, file_format, quality),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
        if download_type == 'audio':
            ydl_opts['extract_audio'] = True
            ydl_opts['audio_format'] = file_format
        self.progress_bar.setValue(0)
        self.download_btn.setEnabled(False)
        self.thread = DownloadThread(url, ydl_opts)
        self.thread.progress.connect(lambda v: self.progress_bar.setValue(int(v)))
        self.thread.finished.connect(self.download_finished)
        self.thread.error.connect(self.download_error)
        self.thread.start()

    def get_format_string(self, download_type, file_format, quality):
        if quality == 'custom':
            return file_format
        if download_type == 'audio':
            return f'bestaudio/{file_format}'
        if download_type == 'video':
            if quality == 'best':
                return f'bestvideo[ext={file_format}]+bestaudio/best[ext={file_format}]'
            elif quality == 'worst':
                return f'worstvideo[ext={file_format}]+worstaudio/worst[ext={file_format}]'
        return 'best'

    def download_finished(self, outtmpl):
        self.download_btn.setEnabled(True)
        QMessageBox.information(self, 'Done', 'Download finished!')
        if not self.remember_folder:
            reply = QMessageBox.question(self, 'Default Folder',
                'Do you want to always download to this folder?',
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.remember_checkbox.setChecked(True)

    def download_error(self, error):
        self.download_btn.setEnabled(True)
        QMessageBox.critical(self, 'Error', f'Download failed: {error}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = YTDLPApp()
    window.show()
    sys.exit(app.exec_())
