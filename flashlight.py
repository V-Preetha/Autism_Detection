# flashlight.py
import tkinter as tk
import threading

# Shared stop flag
flash_should_stop = False

def flash_white():
    global flash_should_stop
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.configure(bg='white')

    def check_stop():
        if flash_should_stop:
            root.quit()  # Stop the Tkinter window
        else:
            root.after(100, check_stop)  # Check every 100ms

    # Start the stop timer (30 seconds)
    root.after(30000, stop_flash)  # 30,000 ms = 30 seconds

    root.after(100, check_stop)  # Start the check_stop loop
    root.mainloop()  # Start Tkinter's main loop

def stop_flash():
    global flash_should_stop
    flash_should_stop = True  # Stop the flash
