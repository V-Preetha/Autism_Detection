import sys
import cv2
import dlib
import numpy as np
import time
from math import hypot
from collections import deque
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from threading import Thread
from flashlight import flash_white, stop_flash  # Your own functions

class EyeBlinkDetector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blink Detection with Flashlight")
        self.setGeometry(100, 100, 800, 600)

        self.image_label = QLabel("Starting camera...")
        self.image_label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        self.cap = cv2.VideoCapture(0)
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("C:\\Users\\vpree\\.cache\\kagglehub\\datasets\\sergiovirahonda\\shape-predictor-68-face-landmarksdat\\versions\\1\\shape_predictor_68_face_landmarks.dat")
        self.font = cv2.FONT_HERSHEY_TRIPLEX

        self.blink_timestamps = deque()
        self.BLINK_THRESHOLD = 5
        self.blinking_ratio_threshold = 4.8

        self.flash_thread = Thread(target=flash_white, daemon=True)
        self.flash_thread.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def midpoint(self, p1, p2):
        return int((p1.x + p2.x) / 2), int((p1.y + p2.y) / 2)

    def get_blinking_ratio(self, eye_points, facial_landmarks):
        left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
        right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
        center_top = self.midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
        center_bottom = self.midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

        hor_line_length = hypot(left_point[0] - right_point[0], left_point[1] - right_point[1])
        ver_line_length = hypot(center_top[0] - center_bottom[0], center_top[1] - center_bottom[1])
        try:
            ratio = hor_line_length / ver_line_length
        except ZeroDivisionError:
            ratio = 0
        return ratio

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)

        for face in faces:
            landmarks = self.predictor(gray, face)

            left_eye_ratio = self.get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
            right_eye_ratio = self.get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
            blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

            if blinking_ratio > self.blinking_ratio_threshold:
                cv2.putText(frame, "BLINKING...", (50, 150), self.font, 1, (255, 0, 0), 2)

                now = time.time()
                self.blink_timestamps.append(now)

                while self.blink_timestamps and now - self.blink_timestamps[0] > 1:
                    self.blink_timestamps.popleft()

                if len(self.blink_timestamps) > self.BLINK_THRESHOLD:
                    cv2.putText(frame, "ABNORMAL BLINK RATE", (50, 300), self.font, 1.5, (0, 0, 255), 2)
                    print("Fail")
                    sys.exit(1)

                    stop_flash()
                    self.timer.stop()
                    self.cap.release()
                    self.close()  # This will trigger closeEvent and quit the app
                    return
        # Convert frame for Qt
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.image_label.setPixmap(pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio))

    def closeEvent(self, event):
        self.cap.release()
        stop_flash()
        cv2.destroyAllWindows()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EyeBlinkDetector()
    window.show()
    sys.exit(app.exec_())


