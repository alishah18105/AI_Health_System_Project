import tkinter as tk
from tkinter import scrolledtext
import requests
import threading

API_URL = "http://127.0.0.1:5000"

class HealthChatbotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Health Chatbot")

        # ✅ Maximize window
        self.root.state('zoomed')
        self.root.config(bg="#ecf0f1")

        # 🔙 Back button frame
        top_bar = tk.Frame(self.root, bg="#ecf0f1")
        top_bar.pack(fill="x", pady=5)

        back_btn = tk.Button(top_bar, text="← Back", font=("Arial", 12, "bold"),
                             bg="#e74c3c", fg="white", command=self.go_back)
        back_btn.pack(side="left", padx=10, pady=5)

        # Frame to center chat UI
        main_frame = tk.Frame(self.root, bg="#ecf0f1")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Chat display area
        self.chat_area = scrolledtext.ScrolledText(
            main_frame, wrap=tk.WORD, state='disabled',
            width=100, height=25, font=("Arial", 12)
        )
        self.chat_area.pack(padx=10, pady=10)

        # Input frame for entry + button
        input_frame = tk.Frame(main_frame, bg="#ecf0f1")
        input_frame.pack(pady=(0, 10))

        self.user_input = tk.Entry(input_frame, width=80, font=("Arial", 12))
        self.user_input.pack(side=tk.LEFT, padx=(10, 0))
        self.user_input.bind("<Return>", lambda event: self.process_user_message())

        self.send_btn = tk.Button(input_frame, text="Send", font=("Arial", 12, "bold"),
                                  bg="#3498db", fg="white", command=self.process_user_message)
        self.send_btn.pack(side=tk.LEFT, padx=10)

        # State tracking
        self.last_disease = None
        self.expecting_info_type = False

        self.show_message("Bot", "Hi! Please type your symptoms to start.")

    def go_back(self):
        """Close this window and open home.py"""
        self.root.destroy()
        from home import open_health_dashboard
        open_health_dashboard()

    def show_message(self, sender, message):
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)

    def process_user_message(self):
        user_text = self.user_input.get().strip()
        if not user_text:
            return

        self.show_message("You", user_text)
        self.user_input.delete(0, tk.END)

        if self.expecting_info_type:
            choice = user_text.lower()
            if choice == 'no':
                self.show_message("Bot", "Thank you for using the Health Chatbot. Stay healthy!")
                self.expecting_info_type = False
                return
            elif choice in ['medication', 'prevention', 'diet plan']:
                threading.Thread(target=self.query_info, args=(self.last_disease, choice)).start()
            else:
                self.show_message("Bot", "Please enter medication, prevention, diet plan, or no.")
        else:
            threading.Thread(target=self.query_predict, args=(user_text,)).start()

    def query_predict(self, symptoms):
        try:
            resp = requests.post(f"{API_URL}/predict", json={"symptoms": symptoms})
            data = resp.json()
            if "error" in data:
                self.show_message("Bot", f"Error: {data['error']}")
                return

            disease = data.get("disease")
            description = data.get("description", "")
            self.last_disease = disease

            self.show_message("Bot", f"You may be suffering from: {disease}")
            self.show_message("Bot", description)
            self.show_message("Bot", "Do you want information about medication, prevention, or diet plan? Please reply with one of these options.")

            self.expecting_info_type = True

        except Exception as e:
            self.show_message("Bot", f"Error connecting to API: {e}")

    def query_info(self, disease, info_type):
        try:
            resp = requests.post(f"{API_URL}/info", json={"disease": disease, "info_type": info_type})
            data = resp.json()
            if "error" in data:
                self.show_message("Bot", f"Error: {data['error']}")
                return

            info_data = data.get("info", "")
            if isinstance(info_data, list):
                info_text = ", ".join(info_data)
            else:
                info_text = str(info_data)

            self.show_message("Bot", f"{info_type.capitalize()} for {disease}: {info_text}")
            self.expecting_info_type = True

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
