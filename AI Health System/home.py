import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

from chatbot import open_chatbot
from cbc_screen import CBCReportScreen
from tts_manager import speak


class HealthDashboard(QWidget):
    def __init__(self, patient_id=None, name="", age="", allergy=""):
        super().__init__()

        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.allergy = allergy

        self.setWindowTitle("Health Dashboard")
        self.showFullScreen()
        self.setStyleSheet("background-color: #ecf0f1;")

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # 🔹 Patient info at top-right
        info_text = f"🆔 ID: {patient_id}   👤 Name: {name}   🎂 Age: {age}"
        info_label = QLabel(info_text)
        info_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_label.setStyleSheet("color: #2c3e50;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(info_label)

        # 🔹 Spacer before title/cards (center vertically)
        main_layout.addStretch(1)

        # 🔹 Center content layout
        center_layout = QVBoxLayout()
        center_layout.setSpacing(40)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


        # Title
        title = QLabel("🏥 Health Management Dashboard")
        title.setFont(QFont("Helvetica", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(title)

        # 🔹 Horizontal layout for cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(60)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Two cards with images
        card1 = self.create_card(
            "assets/images/chatbot1.png",   # replace with your image path
            "Emergency Services",
            "Get immediate help with medicines and instructions in emergency cases.",
            "  Open Emergency  ",
            lambda: open_chatbot(name=self.name, age=self.age, allergy=self.allergy)
        )
        card2 = self.create_card(
            "assets/images/report.png",   # replace with your image path
            "CBC Report",
            "Check your Complete Blood Count report against reference values.",
            "  Open CBC Report  ",
            self.open_cbc_screen
        )

        cards_layout.addWidget(card1)
        cards_layout.addWidget(card2)

        center_layout.addLayout(cards_layout)
        motivation_label = QLabel("💡 Stay healthy, stay strong – your health is your real wealth!")
        motivation_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        motivation_label.setStyleSheet("color: #16a085;")   # greenish shade
        motivation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        center_layout.addWidget(motivation_label)
        main_layout.addLayout(center_layout)

        # 🔹 Spacer after cards (center vertically)
        main_layout.addStretch(1)
    def open_cbc_screen(self):
        self.cbc_window = CBCReportScreen()  # keep a reference
        self.cbc_window.show()

    # 🔹 Create card function (with image at top)
    def create_card(self, icon_path, title_text, description, button_text, command):
        card = QFrame()
        card.setFixedSize(400, 360)   # height thodi increase ki
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #bdc3c7;   
                border-radius: 15px;
            }
            QLabel, QPushButton {
        border: none;   
    }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)

        # 🔹 Icon (Image) - bigger now
        lbl_icon = QLabel()
        pixmap = QPixmap(icon_path).scaled(
            120, 120,   # 👈 increased size
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        lbl_icon.setPixmap(pixmap)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title (no border)
        lbl_title = QLabel(title_text)
        lbl_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))  # bigger font
        lbl_title.setStyleSheet("color: #2c3e50;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Description (no border)
        lbl_desc = QLabel(description)
        lbl_desc.setFont(QFont("Arial", 13))
        lbl_desc.setStyleSheet("color: #7f8c8d;")
        lbl_desc.setWordWrap(True)
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Button
        btn = QPushButton(button_text)
        btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        btn.setFixedHeight(45)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn.clicked.connect(lambda: (speak(button_text), self.close(), command()))

        # Add widgets to layout
        card_layout.addWidget(lbl_icon)
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_desc)
        card_layout.setSpacing(8)
        card_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return card
    

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()  # exit fullscreen


# Run App
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = HealthDashboard(patient_id=1, name="Ali", age="22", allergy="None")
    dashboard.show()
    sys.exit(app.exec())
