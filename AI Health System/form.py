import sys
import psycopg2
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
from home import HealthDashboard


class FormScreen(QWidget):
    def __init__(self):
        super().__init__()

        # ✅ Window setup
        self.setWindowTitle("Health Care Assistant")

        # ✅ Fix black screen issue with palette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ecf0f1"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # ✅ Fonts + style
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
            }
        """)

        self.showFullScreen()

        # Force repaint after fullscreen
        QTimer.singleShot(100, self.repaint)

        # ✅ Main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(main_layout)

        # ---------------- Title ----------------
        title = QLabel("Patient Information")
        title.setFont(QFont("Segoe UI Semibold", 28))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-top: 20px;")
        main_layout.addWidget(title)

        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Segoe UI", 12))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        # ---------------- Returning Patient Section ----------------
        returning_label = QLabel("If you have visited before:")
        returning_label.setFont(QFont("Segoe UI", 14))
        returning_label.setStyleSheet("color: black;")
        returning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(returning_label)
        main_layout.addSpacing(15)

        # 🔹 Row: Phone + Search
        row_widget = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        phone_label = QLabel("Phone Number:")
        phone_label.setFont(QFont("Segoe UI", 12))
        row_layout.addWidget(phone_label)

        self.phone_entry = QLineEdit()
        self.phone_entry.setFont(QFont("Segoe UI", 13))
        self.phone_entry.setFixedWidth(250)
        row_layout.addWidget(self.phone_entry)

        search_btn = QPushButton("Search")
        search_btn.setFont(QFont("Segoe UI Semibold", 11))
        search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_btn.setFixedWidth(120)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #5DADE2;
                color: white;
                padding: 6px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3498DB;
            }
        """)
        search_btn.clicked.connect(self.fetch_patient)
        row_layout.addWidget(search_btn)

        row_widget.setLayout(row_layout)
        main_layout.addWidget(row_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(40)

        # ---------------- Separator ----------------
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #bdc3c7; margin: 15px 40px;")
        main_layout.addWidget(separator)
        main_layout.addSpacing(20)

        # ---------------- New Patient Section ----------------
        new_label = QLabel("New Patient")
        new_label.setFont(QFont("Segoe UI Semibold", 20))
        new_label.setStyleSheet("color: #2c3e50;")
        new_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(new_label)
        main_layout.addSpacing(20)

        # Row 1: Name + Phone
        row1 = QHBoxLayout()
        row1.setSpacing(40)

        name_lbl = QLabel("Name")
        name_lbl.setStyleSheet("color: black;")
        row1.addWidget(name_lbl)

        self.name_entry = QLineEdit()
        self.name_entry.setFont(QFont("Segoe UI", 13))
        self.name_entry.setFixedWidth(300)
        row1.addWidget(self.name_entry)

        ph_lbl = QLabel("Phone No")
        ph_lbl.setStyleSheet("color: black;")
        row1.addWidget(ph_lbl)

        self.ph_entry = QLineEdit()
        self.ph_entry.setFont(QFont("Segoe UI", 13))
        self.ph_entry.setFixedWidth(300)
        row1.addWidget(self.ph_entry)

        row1_widget = QWidget()
        row1_widget.setLayout(row1)
        main_layout.addWidget(row1_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(35)

        # Row 2: Age + Allergy
        row2 = QHBoxLayout()
        row2.setSpacing(40)

        age_lbl = QLabel("Age")
        age_lbl.setStyleSheet("color: black;")
        row2.addWidget(age_lbl)

        self.age_entry = QLineEdit()
        self.age_entry.setFont(QFont("Segoe UI", 13))
        self.age_entry.setFixedWidth(300)
        row2.addWidget(self.age_entry)

        allergy_lbl = QLabel("Allergy")
        allergy_lbl.setStyleSheet("color: black;")
        row2.addWidget(allergy_lbl)

        self.allergy_entry = QLineEdit()
        self.allergy_entry.setFont(QFont("Segoe UI", 13))
        self.allergy_entry.setFixedWidth(300)
        row2.addWidget(self.allergy_entry)

        row2_widget = QWidget()
        row2_widget.setLayout(row2)
        main_layout.addWidget(row2_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(20)

        # Register button
        register_btn = QPushButton("Register")
        register_btn.setFont(QFont("Segoe UI Semibold", 12))
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #5DADE2;
                color: white;
                padding: 8px 20px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #3498DB;
            }
        """)
        main_layout.addWidget(register_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # ✅ Fade-in Animation
        self.fade_in_effect(self)

    # ---------------- Animations ----------------
    def fade_in_effect(self, widget):
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(1200)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.start()
        self._anim = anim

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()  # exit fullscreen

    # ---------------- Database ----------------
    def connect_db(self):
        return psycopg2.connect(
            host="localhost",
            database="healthcare",
            user="postgres",
            password="ali"
        )

    def fetch_patient(self):
        phone = self.phone_entry.text()
        if not phone:
            self.status_label.setText("❌ Please enter phone number")
            self.status_label.setStyleSheet("color: red;")
            return


def open_form():
    app = QApplication(sys.argv)
    form = FormScreen()
    form.show()
    sys.exit(app.exec())
