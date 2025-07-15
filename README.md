# Autism_Detection
Autism Detection App is an interactive desktop application developed in Python using CustomTkinter and PyQt, designed to help identify early signs of autism through a series of behavior-based tests. The app combines multiple AI and computer vision techniques to evaluate specific developmental traits associated with autism spectrum disorder (ASD).

The application includes the following modules:
-Speech Delay Test: Uses speech recognition to analyze the user's ability to respond to spoken prompts, helping assess potential delays in verbal communication.
-Smile Detection Test: Displays a child-friendly video (like "Baby Shark") and uses DeepFace to detect emotional responses by analyzing the user's facial expressions.
-Blinking Tracker Test: Utilizes dlib and OpenCV to monitor eye blink patterns, identifying irregularities or reduced blinking, which can be linked to ASD.
-Repeated Behavior Test: Applies MediaPipe for body movement analysis to detect repetitive physical behaviors, a common indicator of autism.
-Eye Tracker Test: Tracks the user's eye gaze to check attention and focus, using facial landmarks to determine if gaze patterns deviate from typical responses.

Each module is presented with countdowns and clear instructions. After completing the tests, the app calculates a score based on the user's performance and provides a final result screen that indicates the likelihood of autism traits.
This app is intended as a screening aid, not a diagnostic tool, and can be useful for parents, educators, or researchers looking to monitor developmental behavior in children.

DEMO LINK: https://drive.google.com/file/d/13nSG0un0AOHa9tFGlxmfdPWaw0X9uwdW/view?usp=drive_link


