import tkinter as tk
import pyttsx3
from form import open_form
from tts_manager import speak

def splash_screen():
    splash = tk.Tk()
    splash.title("Health Care AI Project")

    # ✅ Maximize the window
    splash.state('zoomed')  # For Windows (maximized mode)
    splash.config(bg="#2C3E50")

    # ✅ Create a frame to center content
    frame = tk.Frame(splash, bg="#2C3E50")
    frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame

    label = tk.Label(
        frame,
        text="Welcome to Health Care Assistant",
        font=("Arial", 28, "bold"),  # Increased font size for big screen
        fg="white",
        bg="#2C3E50"
    )
    label.pack()

    # Speak after 1 second
    splash.after(1000, lambda: speak("Welcome to Health Care Assistant"))

    # After 5 sec → close splash & open form
    splash.after(5000, lambda: [splash.withdraw(), open_form()])

    splash.mainloop()

if __name__ == "__main__":
    splash_screen()
