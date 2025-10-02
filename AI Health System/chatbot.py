import sys
import threading
import requests
import speech_recognition as sr
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


API_URL = "http://127.0.0.1:5000"


class ChatBubble(QLabel):
    """Custom rectangular chat bubble"""
    def __init__(self, text, sender="bot"):
        super().__init__(text)
        self.setWordWrap(True)
        self.setFont(QFont("Arial", 12))
        self.setMargin(12)
        self.setMinimumHeight(45)   # like button height
        self.setMaximumWidth(500)   # bubble max width

        if sender == "user":
            self.setStyleSheet("""
                QLabel {
                    background-color: #3498db;  /* blue */
                    color: white;
                    border-radius: 12px;
                    padding: 10px;
                }
            """)
            self.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            self.setStyleSheet("""
                QLabel {
                    background-color: #2c3e50;  /* dark grey */
                    color: white;
                    border-radius: 12px;
                    padding: 10px;
                }
            """)
            self.setAlignment(Qt.AlignmentFlag.AlignLeft)


class HealthChatbotUI(QWidget):
    message_ready = pyqtSignal(str, str)
    def __init__(self, name="", age="", allergy=""):
        super().__init__()
        self.message_ready.connect(self.show_message)
        self.showFullScreen()

        self.name = name
        self.age = age
        self.allergy = allergy

        # 🔹 Window setup
        self.setWindowTitle("Health Chatbot")
           # smaller window
        self.setStyleSheet("background-color: #ecf0f1;")

        self.recognizer = sr.Recognizer()
        self.listening = False
        self.stop_listening = None

        layout = QVBoxLayout(self)

        # 🔹 Top bar (Back + Title)
        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        back_btn.setFixedHeight(35)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 5px 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        top_bar.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        heading = QLabel("🩺 Health Chat Bot")
        heading.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        heading.setStyleSheet("color: #2c3e50;")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_bar.addWidget(heading, stretch=1)

        top_bar.addStretch()
        layout.addLayout(top_bar)

        # 🔹 Chat area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.chat_widget)
        layout.addWidget(self.scroll_area, stretch=7)

        # 🔹 Input bar
        input_bar = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setFont(QFont("Arial", 11))
        self.user_input.setPlaceholderText("Type your message...")
        self.user_input.setFixedHeight(38)
        self.user_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 12px;
                padding: 6px 10px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
""")
        self.user_input.returnPressed.connect(self.process_user_message)
        input_bar.addWidget(self.user_input, stretch=4)

        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setFixedSize(50, 45)
        self.mic_btn.setStyleSheet("background-color:#2ecc71; color:white; border-radius:8px;")
        self.mic_btn.clicked.connect(self.toggle_listening)
        input_bar.addWidget(self.mic_btn)

        send_btn = QPushButton("Send")
        send_btn.setFixedSize(70, 45)
        send_btn.setStyleSheet("background-color:#3498db; color:white; border-radius:8px;")
        send_btn.clicked.connect(self.process_user_message)
        input_bar.addWidget(send_btn)

        layout.addLayout(input_bar)

        # 🔹 Status
        self.status_label = QLabel("Idle")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #34495e;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Initial greeting
        self.show_message("bot", f"Hello {self.name or 'User'} 👋! Please type or speak your symptoms.")

    def go_back(self):
        from home import HealthDashboard
        self.close()
        self.dashboard_window = HealthDashboard(
            patient_id=None, 
            name=self.name, 
            age=self.age, 
            allergy=self.allergy
        )
        self.dashboard_window.show()



    def show_message(self, sender, message):
        bubble = ChatBubble(message, sender=sender)
        wrapper = QHBoxLayout()
        if sender == "user":
            wrapper.addStretch()
            wrapper.addWidget(bubble)
        else:
            wrapper.addWidget(bubble)
            wrapper.addStretch()
        container = QWidget()
        container.setLayout(wrapper)
        self.chat_layout.addWidget(container)
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    # 🎤 Speech Recognition
    def toggle_listening(self):
        if not self.listening:
            threading.Thread(target=self.start_listening).start()
        else:
            if self.stop_listening:
                self.stop_listening(wait_for_stop=False)
            self.listening = False
            self.mic_btn.setText("🎤")
            self.mic_btn.setStyleSheet("background-color:#2ecc71; color:white;")
            self.status_label.setText("Idle")

    def start_listening(self):
        def callback(recognizer, audio):
            try:
                text = recognizer.recognize_google(audio)
                self.user_input.setText(text)
                self.status_label.setText("✅ Recognized")
            except sr.UnknownValueError:
                self.status_label.setText("❌ Could not understand")
            except sr.RequestError:
                self.status_label.setText("⚠️ API unavailable")

        self.status_label.setText("🎤 Listening...")
        self.mic_btn.setText("🛑")
        self.mic_btn.setStyleSheet("background-color:#e67e22; color:white;")
        self.listening = True
        self.stop_listening = self.recognizer.listen_in_background(sr.Microphone(), callback)

    # 🔹 Message Handling
    def process_user_message(self):
        user_text = self.user_input.text().strip()
        if not user_text:
            return
        self.show_message("user", user_text)
        self.user_input.clear()

        if any(word in user_text.lower() for word in ["description", "medication", "prevention", "diet"]):
            threading.Thread(target=self.query_info, args=(user_text,)).start()
        else:
            threading.Thread(target=self.query_predict, args=(user_text,)).start()

    def query_predict(self, text):
        try:
            resp = requests.post(f"{API_URL}/predict", json={"symptoms": text})
            data = resp.json()

            if "error" in data:
                self.message_ready.emit("bot", f"Error: {data['error']}")
                return

            if data.get("direct_match"):
                self.last_disease = data["disease"]
                self.message_ready.emit("bot", f"You mentioned {self.last_disease}.")
                self.message_ready.emit("bot", f"Description: {data['description']}")
                self.message_ready.emit("bot", data["ask_more"])
                return

            self.multiple_diseases = [d["disease"] for d in data.get("predictions", [])]
            self.last_disease = None
            self.message_ready.emit("bot", data.get("ask_more", "Which disease do you want details about?"))

        except Exception as e:
            self.message_ready.emit("bot", f"Error connecting to API: {e}")

    def query_info(self, text):
        try:
            info_type = None
            for option in ["description", "medication", "prevention", "diet plan"]:
                if option in text.lower():
                    info_type = option
                    break

            disease = None
            for d in getattr(self, "multiple_diseases", []):
                if d.lower() in text.lower():
                    disease = d
                    break
            if not disease:
                disease = getattr(self, "last_disease", None)

            resp = requests.post(f"{API_URL}/info", json={
                "disease": disease,
                "info_type": info_type
            })
            print("DEBUG /predict response:", resp.text)
            data = resp.json()
            if "error" in data:
                self.message_ready.emit("bot", f"Error: {data['error']}")
                return

            self.last_disease = data["disease"]
            self.message_ready.emit("bot", f"{info_type.capitalize()} for {self.last_disease}: {data['info']}")
            self.message_ready.emit("bot", data.get("ask_more", ""))

        except Exception as e:
            self.message_ready.emit("bot", f"Error connecting to API: {e}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            # Just exit fullscreen mode
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()


def open_chatbot(name="", age="", allergy=""):
    return HealthChatbotUI(name, age, allergy)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HealthChatbotUI("Ali", "22", "None")
    window.show()
    sys.exit(app.exec())