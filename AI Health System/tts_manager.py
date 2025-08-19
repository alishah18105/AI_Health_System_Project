import pyttsx3
import threading

# ✅ Create global engine once
engine = pyttsx3.init()

def speak(text):
    """Speak without blocking Tkinter mainloop"""
    def run():
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print("TTS Error:", e)
    threading.Thread(target=run, daemon=True).start()
