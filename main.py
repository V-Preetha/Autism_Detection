import customtkinter as ctk
import subprocess
import threading
import time

# Global autism score counter
autism_score = 0

# Duration for countdown before each test starts
COUNTDOWN_SECONDS = 5

def run_test_with_countdown(script_name, status_label, button):
    def task():
        global autism_score

        button.configure(state="disabled")

        # Countdown before test start
        for i in range(COUNTDOWN_SECONDS, 0, -1):
            status_label.configure(text=f"Starting in {i} seconds...")
            time.sleep(1)

        status_label.configure(text="Running test...")

        # Run the test script and capture output
        result = subprocess.run(["python", script_name], capture_output=True, text=True)

        # Analyze output to check pass/fail (adjust logic based on your scripts)
        if result.returncode == 1:
            status_label.configure(text="Test Failed ❌")
            autism_score += 1
        else:
            status_label.configure(text="Test Passed ✅")
            

        button.configure(state="normal")

    # Run in separate thread to keep GUI responsive
    threading.Thread(target=task).start()


def show_summary():
    if autism_score >= 3:
        summary_label.configure(text=f"Likely autistic (Score: {autism_score})")
    else:
        summary_label.configure(text=f"Unlikely autistic (Score: {autism_score})")


# --- GUI Setup ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("600x600")
app.title("Autism Detection App")

title_label = ctk.CTkLabel(app, text="Autism Detection Tests", font=("Arial", 24))
title_label.pack(pady=20)

# Create widgets for each test
tests = [
    ("speech_delay.py", "Speech Delay Test"),
    ("smile_detection.py", "Smile Detection Test"),
    ("blinking_tracker.py", "Blinking Tracker Test"),
    ("repeated_behaviour.py", "Repeated Behavior Test"),
    ("eye_tracker.py", "Eye Tracker Test")
]

for script, test_name in tests:
    frame = ctk.CTkFrame(app)
    frame.pack(pady=10, fill="x", padx=20)

    label = ctk.CTkLabel(frame, text=test_name, font=("Arial", 16))
    label.pack(side="left", padx=10)

    status = ctk.CTkLabel(frame, text="Waiting...", width=120)
    status.pack(side="left", padx=10)

    btn = ctk.CTkButton(frame, text="Run Test",
                        command=lambda s=script, l=status, b=None: run_test_with_countdown(s, l, b))
    # We need a workaround to pass button reference to lambda
    # So create the button first, then update command
    btn.pack(side="left", padx=10)
    btn.configure(command=lambda s=script, l=status, b=btn: run_test_with_countdown(s, l, b))


# Summary label and button
summary_label = ctk.CTkLabel(app, text="Click 'Show Summary' when done.", font=("Arial", 18))
summary_label.pack(pady=40)

summary_btn = ctk.CTkButton(app, text="Show Summary", command=show_summary)
summary_btn.pack()

app.mainloop()
