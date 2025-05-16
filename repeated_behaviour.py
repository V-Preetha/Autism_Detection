import sys
import cv2
import numpy as np
from collections import deque
from scipy.signal import find_peaks
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import mediapipe as mp
import time

class PoseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autism Behavior Detection")
        self.setGeometry(100, 100, 800, 600)

        # UI
        self.label = QLabel("Webcam Feed", self)
        self.label.setAlignment(Qt.AlignCenter)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setStyleSheet("background-color: red; color: white")
        self.stop_button.clicked.connect(self.stop_program)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)

        # Mediapipe pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.drawing_utils = mp.solutions.drawing_utils

        self.cap = cv2.VideoCapture(0)
        self.wrist_y_history = deque(maxlen=60)

        # Timer for updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        # Timer for max duration
        self.start_time = time.time()
        self.max_duration = 30  # seconds

    def update_frame(self):
        if time.time() - self.start_time > self.max_duration:
            print("⏱️ Time limit reached. Stopping.")
            self.stop_program()
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            right_wrist_y = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST].y
            self.wrist_y_history.append(right_wrist_y)

            self.drawing_utils.draw_landmarks(
                image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            if len(self.wrist_y_history) == self.wrist_y_history.maxlen:
                y_array = np.array(self.wrist_y_history)
                y_array = y_array - np.mean(y_array)
                peaks, _ = find_peaks(y_array, distance=5, prominence=0.01)

                if len(peaks) > 6:
                    cv2.putText(image, "pass", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    print("Fail")
                    sys.exit(1)
                    self.stop_program()
                    return

        # Convert to QImage and show
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        qt_img = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qt_img))

    def stop_program(self):
        self.timer.stop()
        self.cap.release()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PoseApp()
    window.show()
    sys.exit(app.exec_())
