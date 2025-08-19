import tkinter as tk
import pyttsx3

from chatbot import open_chatbot
from cbc_screen import open_cbc_screen
from tts_manager import speak

# 🔊 Create one engine globally

def open_health_dashboard(patient_id=None, name="", age="", allergy=""):
    root = tk.Tk()
    root.title("Health Dashboard")

    # ✅ Maximize the window
    root.state('zoomed')
    root.config(bg="#ecf0f1")

    # 🔹 Patient info at top-right
    info_text = f"🆔 ID: {patient_id}   👤 Name: {name}   🎂 Age: {age}"
    info_label = tk.Label(
        root,
        text=info_text,
        font=("Arial", 12, "bold"),
        fg="#2c3e50",
        bg="#ecf0f1",
        anchor="e",
        justify="right"
    )
    info_label.pack(anchor="ne", padx=20, pady=10)

    # 🔹 Dashboard Title (centered)
    tk.Label(
        root,
        text="🏥 Health Management Dashboard",
        font=("Helvetica", 26, "bold"),
        bg="#ecf0f1",
        fg="#2c3e50"
    ).pack(pady=20)

    # 🔹 Center frame for buttons
    center_frame = tk.Frame(root, bg="#ecf0f1")
    center_frame.place(relx=0.5, rely=0.5, anchor="center")

    # 📦 Function to create buttons with voice + close dashboard
    def create_box(text, command):
        def on_click():
            speak(text)  # start speech
            root.after(800, lambda: [root.destroy(), command()])

        return tk.Button(
            center_frame,
            text=text,
            font=("Arial", 16, "bold"),
            width=20,
            height=3,
            bg="#3498db",
            fg="white",
            bd=0,
            relief="raised",
            activebackground="#2980b9",
            activeforeground="white",
            command=on_click
        )


    # 🔹 Button layout (grid)
    create_box("Emergency", lambda: open_chatbot(name=name, age=age, allergy=allergy)).grid(row=0, column=0, padx=30, pady=20)
    create_box("OPD", open_chatbot).grid(row=0, column=1, padx=30, pady=20)
    create_box("Nutrition", open_chatbot).grid(row=1, column=0, padx=30, pady=20)
    create_box("X-Ray Report", open_chatbot).grid(row=1, column=1, padx=30, pady=20)
    create_box("CBC Report", open_cbc_screen).grid(row=2, column=0, columnspan=2, pady=20)

    root.mainloop()

if __name__ == "__main__":
    open_health_dashboard()
