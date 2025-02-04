import os
import cv2
import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QSpinBox, QSlider, QComboBox,
    QMessageBox, QToolBar, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# -----------------------
# Translation dictionary
# -----------------------
translations = {
    "en": {
        "window_title": "Video Frame Extraction Tool",
        "input_folder": "Input Folder:",
        "output_folder": "Output Folder:",
        "select_folder": "Select Folder",
        "extraction_fps": "Extraction FPS:",
        "image_format": "Image Format:",
        "start_extraction": "Start Extraction",
        "pause": "Pause",
        "resume": "Resume",
        "stop": "Stop",
        "no_video": "No video files found in the selected directory.",
        "invalid_input": "Please select a valid input folder.",
        "extraction_complete": "Frames extracted successfully!",
        "extraction_stopped": "Extraction stopped by user.",
        "error": "Error",
        "warning": "Warning",
        "language": "Language:",
        "processing": "Processing..."
    },
    "zh-TW": {
        "window_title": "影片影格抽取工具",
        "input_folder": "輸入資料夾：",
        "output_folder": "輸出資料夾：",
        "select_folder": "選擇資料夾",
        "extraction_fps": "抽取FPS：",
        "image_format": "圖片格式：",
        "start_extraction": "開始抽取影格",
        "pause": "暫停",
        "resume": "繼續",
        "stop": "停止",
        "no_video": "所選資料夾中沒有找到影片檔案。",
        "invalid_input": "請選擇有效的輸入資料夾。",
        "extraction_complete": "影格抽取完成！",
        "extraction_stopped": "使用者中止抽取。",
        "error": "錯誤",
        "warning": "警告",
        "language": "語言：",
        "processing": "處理中..."
    }
}

# --------------------------------------
# Worker thread for frame extraction
# --------------------------------------
class ExtractionWorker(QThread):
    progress_update = pyqtSignal(int)   # Signal to update current processed frame count
    max_update = pyqtSignal(int)        # Signal to update the total number of frames
    finished_signal = pyqtSignal()      # Signal emitted when extraction finishes normally
    stopped_signal = pyqtSignal()       # Signal emitted when extraction is stopped by user
    error_signal = pyqtSignal(str)      # Signal emitted when an error occurs

    def __init__(self, input_dir, output_dir, fps, img_format, trans):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir if output_dir else input_dir
        self.fps = fps
        self.img_format = img_format
        self.trans = trans
        self._paused = False  # Flag to indicate pause
        self._stopped = False # Flag to indicate stop

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def stop(self):
        self._stopped = True

    def run(self):
        try:
            if not os.path.isdir(self.output_dir):
                os.makedirs(self.output_dir)

            video_files = [f for f in os.listdir(self.input_dir)
                           if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
            if not video_files:
                self.error_signal.emit(self.trans["no_video"])
                return

            # Calculate the total number of frames in all videos (used as the progress bar maximum)
            total_frames = 0
            for video_file in video_files:
                video_path = os.path.join(self.input_dir, video_file)
                cap = cv2.VideoCapture(video_path)
                total_frames += int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.release()
            self.max_update.emit(total_frames)

            current_progress = 0
            # Process each video one by one
            for video_file in video_files:
                if self._stopped:
                    break  # Break out if stop flag is set

                video_path = os.path.join(self.input_dir, video_file)
                video_name, _ = os.path.splitext(video_file)
                video_output_dir = os.path.join(self.output_dir, video_name)
                os.makedirs(video_output_dir, exist_ok=True)

                cap = cv2.VideoCapture(video_path)
                original_fps = cap.get(cv2.CAP_PROP_FPS)
                # If the original FPS is lower, set frame_interval to 1
                frame_interval = max(1, int(original_fps) // self.fps)
                frame_count = 0
                extracted_count = 0

                while True:
                    # Check for pause flag
                    while self._paused:
                        if self._stopped:
                            break
                        self.msleep(100)  # Sleep for 100 ms while paused
                    if self._stopped:
                        break

                    ret, frame = cap.read()
                    if not ret:
                        break

                    if frame_count % frame_interval == 0:
                        frame_filename = os.path.join(video_output_dir,
                                                      f"frame_{extracted_count:04d}.{self.img_format}")
                        cv2.imwrite(frame_filename, frame)
                        extracted_count += 1

                    frame_count += 1
                    current_progress += 1
                    self.progress_update.emit(current_progress)
                cap.release()

            # Emit signal based on whether extraction was stopped by user
            if self._stopped:
                self.stopped_signal.emit()
            else:
                self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))


# -----------------------
# Main Window
# -----------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "en"  # Default language: English
        self.trans = translations[self.lang]
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.trans["window_title"])
        self.setGeometry(100, 100, 600, 450)

        # Add a toolbar for language selection
        toolbar = QToolBar()
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        lang_label = QLabel(self.trans["language"] + " ")
        toolbar.addWidget(lang_label)
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("中文(臺灣)", "zh-TW")
        self.lang_combo.currentIndexChanged.connect(self.changeLanguage)
        toolbar.addWidget(self.lang_combo)

        # Main widget and layout
        widget = QWidget()
        self.layout = QVBoxLayout()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        # Input folder selection
        input_layout = QHBoxLayout()
        self.input_label = QLabel(self.trans["input_folder"])
        self.input_edit = QLineEdit()
        self.input_btn = QPushButton(self.trans["select_folder"])  # Reference stored here
        self.input_btn.clicked.connect(self.select_input_dir)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(self.input_btn)
        self.layout.addLayout(input_layout)

        # Output folder selection
        output_layout = QHBoxLayout()
        self.output_label = QLabel(self.trans["output_folder"])
        self.output_edit = QLineEdit()
        self.output_btn = QPushButton(self.trans["select_folder"])  # Reference stored here
        self.output_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(self.output_btn)
        self.layout.addLayout(output_layout)

        # FPS setting: SpinBox and Slider synchronized
        fps_layout = QHBoxLayout()
        self.fps_label = QLabel(self.trans["extraction_fps"])
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 120)
        self.fps_spin.setValue(1)
        self.fps_slider = QSlider(Qt.Horizontal)
        self.fps_slider.setRange(1, 120)
        self.fps_slider.setValue(1)
        # Synchronize the SpinBox and Slider
        self.fps_spin.valueChanged.connect(self.fps_slider.setValue)
        self.fps_slider.valueChanged.connect(self.fps_spin.setValue)
        fps_layout.addWidget(self.fps_label)
        fps_layout.addWidget(self.fps_spin)
        fps_layout.addWidget(self.fps_slider)
        self.layout.addLayout(fps_layout)

        # Image format selection (ComboBox)
        format_layout = QHBoxLayout()
        self.format_label = QLabel(self.trans["image_format"])
        self.format_combo = QComboBox()
        self.format_combo.addItems(["jpg", "jpeg", "png", "tif"])
        format_layout.addWidget(self.format_label)
        format_layout.addWidget(self.format_combo)
        self.layout.addLayout(format_layout)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar)

        # Execution button and pause/stop buttons layout
        button_layout = QHBoxLayout()
        self.run_btn = QPushButton(self.trans["start_extraction"])
        self.run_btn.clicked.connect(self.start_extraction)
        button_layout.addWidget(self.run_btn)

        self.pause_btn = QPushButton(self.trans["pause"])
        self.pause_btn.clicked.connect(self.pause_or_resume)
        self.pause_btn.setEnabled(False)
        button_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton(self.trans["stop"])
        self.stop_btn.clicked.connect(self.stop_extraction)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)

        self.layout.addLayout(button_layout)

        # Apply a modern stylesheet for a better look
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit, QSpinBox, QSlider, QComboBox, QPushButton {
                font-size: 14px;
                padding: 4px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 4px;
                text-align: center;
                background-color: #eee;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
        """)

    def changeLanguage(self):
        self.lang = self.lang_combo.currentData()
        self.trans = translations[self.lang]
        self.updateTranslations()

    def updateTranslations(self):
        self.setWindowTitle(self.trans["window_title"])
        self.input_label.setText(self.trans["input_folder"])
        self.output_label.setText(self.trans["output_folder"])
        self.fps_label.setText(self.trans["extraction_fps"])
        self.format_label.setText(self.trans["image_format"])
        self.run_btn.setText(self.trans["start_extraction"])
        self.pause_btn.setText(self.trans["pause"])
        self.stop_btn.setText(self.trans["stop"])
        # Update the language label in the toolbar
        toolbar = self.findChild(QToolBar)
        if toolbar is not None and toolbar.actions():
            lang_widget = toolbar.widgetForAction(toolbar.actions()[0])
            if lang_widget:
                lang_widget.setText(self.trans["language"] + " ")
        # Update the text on the "Select Folder" buttons
        self.input_btn.setText(self.trans["select_folder"])
        self.output_btn.setText(self.trans["select_folder"])

    def select_input_dir(self):
        directory = QFileDialog.getExistingDirectory(self, self.trans["input_folder"])
        if directory:
            self.input_edit.setText(directory)

    def select_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, self.trans["output_folder"])
        if directory:
            self.output_edit.setText(directory)

    def start_extraction(self):
        input_dir = self.input_edit.text().strip()
        output_dir = self.output_edit.text().strip()
        fps = self.fps_spin.value()
        img_format = self.format_combo.currentText()

        if not os.path.isdir(input_dir):
            QMessageBox.warning(self, self.trans["warning"], self.trans["invalid_input"])
            return

        if not output_dir:
            output_dir = input_dir

        # Disable the run button and enable pause and stop buttons; show progress bar
        self.run_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.pause_btn.setText(self.trans["pause"])
        self.progress_bar.setValue(0)
        self.progress_bar.show()

        # Create and start the worker thread
        self.worker = ExtractionWorker(input_dir, output_dir, fps, img_format, self.trans)
        self.worker.max_update.connect(self.progress_bar.setMaximum)
        self.worker.progress_update.connect(self.progress_bar.setValue)
        self.worker.finished_signal.connect(self.on_extraction_finished)
        self.worker.stopped_signal.connect(self.on_extraction_stopped)
        self.worker.error_signal.connect(self.on_extraction_error)
        self.worker.start()

    def pause_or_resume(self):
        # Toggle between pause and resume
        if self.worker is None:
            return
        if not self.worker._paused:
            self.worker.pause()
            self.pause_btn.setText(self.trans["resume"])
        else:
            self.worker.resume()
            self.pause_btn.setText(self.trans["pause"])

    def stop_extraction(self):
        # Stop the extraction process
        if self.worker is not None:
            self.worker.stop()
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)

    def on_extraction_finished(self):
        # Use system beep for notification and show finished pop-up
        QApplication.beep()
        QMessageBox.information(self, self.trans["window_title"], self.trans["extraction_complete"])
        self.run_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.progress_bar.hide()

    def on_extraction_stopped(self):
        # Use system beep for notification and show stopped pop-up
        QApplication.beep()
        QMessageBox.information(self, self.trans["window_title"], self.trans["extraction_stopped"])
        self.run_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.progress_bar.hide()

    def on_extraction_error(self, msg):
        QMessageBox.critical(self, self.trans["error"], msg)
        self.run_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.progress_bar.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
