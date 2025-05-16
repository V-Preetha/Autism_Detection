import customtkinter as ctk
import pyttsx3
import speech_recognition as sr
import threading
import time
import random
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SpeechDelayTestApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Speech Delay Test")
        self.geometry("600x400")

        self.words_to_test = ["Rat", "Bat", "Man"]
        random.shuffle(self.words_to_test)
        self.delay_limit = 5
        self.max_score_allowed = 3
        self.score = 0
        self.current_word_index = 0

        self.engine = pyttsx3.init()

        # GUI Elements
        self.word_label = ctk.CTkLabel(self, text="", font=("Arial", 36))
        self.word_label.pack(pady=30)

        self.status_label = ctk.CTkLabel(self, text="Press 'Start Test' to begin", font=("Arial", 18))
        self.status_label.pack(pady=20)

        self.score_label = ctk.CTkLabel(self, text="Score: 0", font=("Arial", 18))
        self.score_label.pack(pady=10)

        self.start_btn = ctk.CTkButton(self, text="Start Test", command=self.start_test)
        self.start_btn.pack(pady=20)

    def speak(self, word):
        self.engine.say(word)
        self.engine.runAndWait()

    def listen_for_word(self, expected_word):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            self.update_status("Listening...")

            start_time = time.time()
            while True:
                try:
                    audio = recognizer.listen(source, timeout=self.delay_limit, phrase_time_limit=3)
                    response_time = time.time() - start_time
                    said = recognizer.recognize_google(audio).lower()
                    print(f"You said: {said}")

                    if expected_word.lower() in said:
                        self.update_status(f"Recognized '{expected_word}' in {int(response_time)} seconds.")
                        return False  # No delay
                    else:
                        self.update_status("Incorrect word. Waiting again...")
                        if response_time > self.delay_limit:
                            return True  # Delay occurred

                except sr.WaitTimeoutError:
                    self.update_status("No response detected.")
                    return True
                except sr.UnknownValueError:
                    self.update_status("Could not understand speech.")
                    if time.time() - start_time > self.delay_limit:
                        return True
                except sr.RequestError:
                    self.update_status("Speech Recognition API error.")
                    return True

    def update_status(self, text):
        self.status_label.configure(text=text)

    def update_score(self):
        self.score_label.configure(text=f"Score: {self.score}")

    def start_test(self):
        self.start_btn.configure(state="disabled")
        threading.Thread(target=self.run_tests).start()

    def run_tests(self):
        for word in self.words_to_test:
            self.word_label.configure(text=f"Say: {word}")

            # Speak the word
            self.speak(word)

            # Listen for response
            delayed = self.listen_for_word(word)
            if delayed:
                self.score += 1
                self.update_status(f"Delay detected for word: {word}")
            else:
                self.update_status(f"Good response for word: {word}")

            self.update_score()
            time.sleep(2)  # short pause before next word

        # Test finished
        self.word_label.configure(text="Test Completed.")
        if self.score > 1:
            self.update_status("Fail")
            sys.exit(1)
        else:
            self.update_status("Pass")
            sys.exit(0)
        self.start_btn.configure(state="normal")

if __name__ == "__main__":
    app = SpeechDelayTestApp()
    app.mainloop()

