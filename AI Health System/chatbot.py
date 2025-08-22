import tkinter as tk
from tkinter import scrolledtext
import requests
import threading
import speech_recognition as sr

API_URL = "http://127.0.0.1:5000"

class HealthChatbotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Health Chatbot")

        self.root.state('zoomed')
        self.root.config(bg="#ecf0f1")

        # recognizer state
        self.recognizer = sr.Recognizer()
        self.listening = False
        self.stop_listening = None

        # UI layout
        top_bar = tk.Frame(self.root, bg="#ecf0f1")
        top_bar.pack(fill="x", pady=5)
        back_btn = tk.Button(top_bar, text="← Back", font=("Arial", 12, "bold"),
                             bg="#e74c3c", fg="white", command=self.go_back)
        back_btn.pack(side="left", padx=10, pady=5)

        main_frame = tk.Frame(self.root, bg="#ecf0f1")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.chat_area = scrolledtext.ScrolledText(
            main_frame, wrap=tk.WORD, state='disabled',
            width=100, height=25, font=("Arial", 12)
        )
        self.chat_area.pack(padx=10, pady=10)

        self.chat_area.tag_configure("user", foreground="#2c3e50", font=("Arial", 12, "bold"))   # Dark Blue
        self.chat_area.tag_configure("bot", foreground="#27ae60", font=("Arial", 12))  

        input_frame = tk.Frame(main_frame, bg="#ecf0f1")
        input_frame.pack(pady=(0, 10))

        self.user_input = tk.Entry(input_frame, width=70, font=("Arial", 12))
        self.user_input.pack(side=tk.LEFT, padx=(10, 0))
        self.user_input.bind("<Return>", lambda event: self.process_user_message())

        self.mic_btn = tk.Button(input_frame, text="🎤 Speak", font=("Arial", 12, "bold"),
                                 bg="#2ecc71", fg="white", command=self.toggle_listening)
        self.mic_btn.pack(side=tk.LEFT, padx=5)

        self.send_btn = tk.Button(input_frame, text="Send", font=("Arial", 12, "bold"),
                                  bg="#3498db", fg="white", command=self.process_user_message)
        self.send_btn.pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(main_frame, text="Idle", fg="blue", bg="#ecf0f1", font=("Arial", 10))
        self.status_label.pack()

        # state tracking
        self.last_disease = None
        self.multiple_diseases = []

        self.show_message("Bot", "Hi! Please type or speak your symptoms or disease to start.")

    def go_back(self):
        self.root.destroy()
        from home import open_health_dashboard
        open_health_dashboard()

    def show_message(self, sender, message):
        self.chat_area.configure(state='normal')
        if sender == "You":
            self.chat_area.insert(tk.END, f"{sender}: {message}\n\n", "user")
        else:
            self.chat_area.insert(tk.END, f"{sender}: {message}\n\n", "bot")
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)

    # 🎤 Speech Recognition
    def toggle_listening(self):
        if not self.listening:
            threading.Thread(target=self.start_listening).start()
        else:
            if self.stop_listening:
                self.stop_listening(wait_for_stop=False)
            self.listening = False
            self.mic_btn.config(text="🎤 Speak", bg="#2ecc71")
            self.status_label.config(text="Idle")

    def start_listening(self):
        def callback(recognizer, audio):
            try:
                text = recognizer.recognize_google(audio)
                self.user_input.delete(0, tk.END)
                self.user_input.insert(0, text)
                self.status_label.config(text="✅ Recognized")
            except sr.UnknownValueError:
                self.status_label.config(text="❌ Could not understand")
            except sr.RequestError:
                self.status_label.config(text="⚠️ API unavailable")

        self.status_label.config(text="🎤 Listening...")
        self.mic_btn.config(text="🛑 Stop", bg="#e67e22")
        self.listening = True
        self.stop_listening = self.recognizer.listen_in_background(sr.Microphone(), callback)

    # Chatbot logic
    def process_user_message(self):
        user_text = self.user_input.get().strip()
        if not user_text:
            return

        self.show_message("You", user_text)
        self.user_input.delete(0, tk.END)

        # Decide whether this is info query or symptom/disease entry
        if any(word in user_text.lower() for word in ["description", "medication", "prevention", "diet"]):
            threading.Thread(target=self.query_info, args=(user_text,)).start()
        else:
            threading.Thread(target=self.query_predict, args=(user_text,)).start()

    def query_predict(self, text):
        try:
            resp = requests.post(f"{API_URL}/predict", json={"symptoms": text})
            data = resp.json()
            if "error" in data:
                self.show_message("Bot", f"Error: {data['error']}")
                return

            if data.get("direct_match"):
                self.last_disease = data["disease"]
                self.show_message("Bot", f"You directly mentioned {self.last_disease}.")
                self.show_message("Bot", f"Description: {data['description']}")
                self.show_message("Bot", data["ask_more"])
                return

            self.multiple_diseases = [d["disease"] for d in data.get("predictions", [])]
            self.last_disease = None
            self.show_message("Bot", data.get("ask_more", "Which disease do you want details about?"))

        except Exception as e:
            self.show_message("Bot", f"Error connecting to API: {e}")

    def query_info(self, text):
        try:
            # extract disease & info type
            info_type = None
            for option in ["description", "medication", "prevention", "diet plan"]:
                if option in text.lower():
                    info_type = option
                    break

            disease = None
            for d in self.multiple_diseases:
                if d.lower() in text.lower():
                    disease = d
                    break
            if not disease:
                disease = self.last_disease  # fallback

            resp = requests.post(f"{API_URL}/info", json={
                "disease": disease,
                "info_type": info_type
            })
            data = resp.json()
            if "error" in data:
                self.show_message("Bot", f"Error: {data['error']}")
                return

            self.last_disease = data["disease"]
            self.show_message("Bot", f"{info_type.capitalize()} for {self.last_disease}: {data['info']}")
            self.show_message("Bot", data.get("ask_more", ""))

        except Exception as e:
            self.show_message("Bot", f"Error connecting to API: {e}")


def open_chatbot(name="", age="", allergy=""):
    root = tk.Tk()
    app = HealthChatbotUI(root)
    root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = HealthChatbotUI(root)
    root.mainloop()
