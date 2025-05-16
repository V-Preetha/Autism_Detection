import sys
import time
import threading

import cv2
from deepface import DeepFace
import pygame

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton


# Thread to play Baby Shark audio
class AudioThread(QThread):
    def run(self):
        pygame.mixer.init()
        pygame.mixer.music.load("baby_sharkk.mp3")
        pygame.mixer.music.play(-1)  # loop forever


# Thread to play Baby Shark video using OpenCV
class VideoThread(QThread):
    frame_ready = pyqtSignal(QImage)
    stopped = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.stop_flag = False

    def run(self):
        cap = cv2.VideoCapture("baby_shark.mp4")
        fps = cap.get(cv2.CAP_PROP_FPS)
        delay = int(1000 / fps)  # ms per frame

        while cap.isOpened() and not self.stop_flag:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert BGR frame to RGB QImage
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.frame_ready.emit(qt_image)

            self.msleep(delay)

        cap.release()
        self.stopped.emit()

    def stop(self):
        self.stop_flag = True


# Thread for emotion detection from webcam
class EmotionThread(QThread):
    emotion_signal = pyqtSignal(str)
    stop_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.stop_flag = False

    def run(self):
        cap = cv2.VideoCapture(0)
        no_emotion_start = None

        while not self.stop_flag:
            ret, frame = cap.read()
            if not ret:
                continue

            try:
                result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                dominant_emotion = result[0]['dominant_emotion']
            except Exception as e:
                dominant_emotion = "No face"

            self.emotion_signal.emit(dominant_emotion)

            if dominant_emotion.lower() in ["neutral", "sad",""]:
                if no_emotion_start is None:
                    no_emotion_start = time.time()
                elif time.time() - no_emotion_start > 10:
                    self.stop_signal.emit()
                    break
            else:
                no_emotion_start = None

            self.msleep(100)  # 0.1 sec delay between frames

        cap.release()

    def stop(self):
        self.stop_flag = True


# Main PyQt Application Window
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Baby Shark & Emotion Detection")

        self.video_label = QLabel("Loading video...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emotion_label = QLabel("Emotion: ")
        self.emotion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_all)

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.emotion_label)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)

        self.audio_thread = AudioThread()
        self.video_thread = VideoThread()
        self.emotion_thread = EmotionThread()

        # Connect video frame signal
        self.video_thread.frame_ready.connect(self.update_video_frame)
        #self.video_thread.stopped.connect(self.handle_video_stopped)

        # Connect emotion signals
        self.emotion_thread.emotion_signal.connect(self.update_emotion_label)
        self.emotion_thread.stop_signal.connect(self.handle_emotion_stop)

        # Timer to stop everything after 20 seconds
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.handle_timeout)

        self.start_all()

    def start_all(self):
        self.audio_thread.start()
        self.video_thread.start()
        self.emotion_thread.start()
        self.timer.start(60000)  # 60 seconds

    def update_video_frame(self, qimage):
        self.video_label.setPixmap(QPixmap.fromImage(qimage).scaled(
            self.video_label.width(), self.video_label.height(), Qt.AspectRatioMode.KeepAspectRatio))

    def update_emotion_label(self, emotion):
        self.emotion_label.setText(f"Emotion: {emotion}")

    def handle_timeout(self):
        print("Time limit reached! Stopping...")
        self.stop_all()

    def handle_emotion_stop(self):
        print("Fail")
        sys.exit(1)
        self.stop_all()

    

    def stop_all(self):
        self.audio_thread.terminate()  # pygame mixer stop? You can also add a stop method there
        pygame.mixer.music.stop()

        self.video_thread.stop()
        self.video_thread.wait()

        self.emotion_thread.stop()
        self.emotion_thread.wait()

        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
