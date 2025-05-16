import sys
import cv2
import dlib
import numpy as np
import pyttsx3
import pygame
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QInputDialog
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap

class GazeApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Autism Gaze Response Test")
        self.setGeometry(100, 100, 900, 500)

        # UI
        self.label = QLabel(self)
        self.button = QPushButton("Stop", self)
        self.button.setStyleSheet("background-color: red; color: white;")
        self.button.clicked.connect(self.stop_program)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # Ask child name
        self.child_name, ok = QInputDialog.getText(self, "Child's Name", "Enter the child's name:")
        if not ok or not self.child_name:
            sys.exit()

        # Init
        self.cap = cv2.VideoCapture(0)
        self.video = cv2.VideoCapture("baby_shark.mp4")
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("C:/Users/vpree/.cache/kagglehub/datasets/sergiovirahonda/"
            "shape-predictor-68-face-landmarksdat/versions/1/"
            "shape_predictor_68_face_landmarks.dat")

        self.running = True
        self.distracted_count = 0
        self.start_time = time.time()

        # Audio
        pygame.mixer.init()
        try:
            pygame.mixer.music.load("baby_sharkk.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            #print("Audio error:", e)
            pass

        # Speak name
        self.speak_name()

        # Start timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def speak_name(self):
        engine = pyttsx3.init()
        def speak():
            for _ in range(3):
                if not self.running:
                    return
                engine.say(self.child_name)
                engine.runAndWait()
                time.sleep(2)
        import threading
        threading.Thread(target=speak, daemon=True).start()

    def get_gaze_ratio(self, eye_points, landmarks, gray):
        points = [landmarks.part(p) for p in eye_points]
        region = np.array([(p.x, p.y) for p in points], np.int32)
        mask = np.zeros_like(gray)
        cv2.fillPoly(mask, [region], 255)
        eye = cv2.bitwise_and(gray, gray, mask=mask)

        min_x = np.min(region[:, 0])
        max_x = np.max(region[:, 0])
        min_y = np.min(region[:, 1])
        max_y = np.max(region[:, 1])

        gray_eye = eye[min_y:max_y, min_x:max_x]
        _, threshold = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)
        left = threshold[:, :threshold.shape[1] // 2]
        right = threshold[:, threshold.shape[1] // 2:]
        left_white = cv2.countNonZero(left)
        right_white = cv2.countNonZero(right)

        try:
            return left_white / right_white
        except ZeroDivisionError:
            return 0

    def update_frame(self):
        if not self.running:
            return

        elapsed = time.time() - self.start_time
        if elapsed > 60:
            print("pass")
            self.stop_program()
            return

        ret_vid, vid_frame = self.video.read()
        ret_cam, cam_frame = self.cap.read()

        if not ret_vid:
            #print("Video finished or failed. Restarting video.")
            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        if not ret_cam:
            #print("Camera read failed.")
            return

        vid_frame = cv2.resize(vid_frame, (600, 400))
        cam_frame_small = cv2.resize(cam_frame, (200, 150))
        gray = cv2.cvtColor(cam_frame, cv2.COLOR_BGR2GRAY)

        faces = self.detector(gray)
        gaze_text = ""

        for face in faces:
            landmarks = self.predictor(gray, face)
            left = self.get_gaze_ratio([36, 37, 38, 39, 40, 41], landmarks, gray)
            right = self.get_gaze_ratio([42, 43, 44, 45, 46, 47], landmarks, gray)
            gaze_ratio = (left + right) / 2

            if 0.3 < gaze_ratio < 0.8:
                gaze_text = "LEFT"
                self.distracted_count += 1
            elif 0.8 <= gaze_ratio <= 1.3:
                gaze_text = "CENTER"
            else:
                gaze_text = "RIGHT"
                self.distracted_count += 1

            if gaze_ratio == 0:
                gaze_text = "EYES COVERED"
                self.distracted_count += 1

        if gaze_text:
            cv2.putText(cam_frame_small, gaze_text, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

        if self.distracted_count > 300:
            cv2.putText(cam_frame_small, "pass", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            print("fail")
            sys.exit(1)
            self.stop_program()

        # Combine
        combined = np.zeros((500, 900, 3), dtype=np.uint8)
        combined[50:450, 150:750] = vid_frame
        combined[340:490, 680:880] = cam_frame_small

        rgb_image = cv2.cvtColor(combined, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qt_image))

    def stop_program(self):
        self.running = False
        self.timer.stop()
        self.cap.release()
        self.video.release()
        pygame.mixer.music.stop()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GazeApp()
    window.show()
    sys.exit(app.exec_())
