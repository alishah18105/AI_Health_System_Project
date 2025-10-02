import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QFont
from tts_manager import speak
from form import FormScreen


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()

        # ✅ Window setup
        self.setWindowTitle("Health Care AI Project")
        self.showFullScreen()
        self.setStyleSheet("background-color: #ecf0f1;")

        # ✅ Layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ✅ Image
        self.image_label = QLabel(self)
        pixmap = QPixmap("assets/images/robot.png")
        pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ✅ Text
        self.full_text = "Welcome to AI Health Care Assistant"
        self.words = self.full_text.split()
        self.current_index = 0
        self.text_label = QLabel("", self)
        self.text_label.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        self.text_label.setStyleSheet("color: #2c3e50;")  # ✅ grey text for light background
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.image_label)
        layout.addWidget(self.text_label)
        self.setLayout(layout)

        # ✅ Fade-in effect for logo
        self.image_opacity = QGraphicsOpacityEffect()
        self.image_label.setGraphicsEffect(self.image_opacity)
        self.image_opacity.setOpacity(0)
        self.animate_fade_in(self.image_opacity, duration=2000)

        # ✅ Start typing + speaking after fade-in
        QTimer.singleShot(2000, self.start_typing_effect)

        # ✅ Close splash after 6s (not 12, your code already uses 6000ms)
        QTimer.singleShot(6000, self.open_main_form)

    def animate_fade_in(self, target, duration=2000, delay=0):
        anim = QPropertyAnimation(target, b"opacity", self)
        anim.setDuration(duration)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.Type.Linear)  # ✅ PyQt6 uses .Type
        setattr(self, f"anim_{id(target)}", anim)  # Keep reference

        if delay > 0:
            QTimer.singleShot(delay, anim.start)
        else:
            anim.start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()  # exit fullscreen

    def start_typing_effect(self):
        """Typing effect while speaking full text"""
        # 🔊 Speak whole sentence once
        speak(self.full_text)

        # ⌨️ Typing effect
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_text)
        self.timer.start(300)  # interval (ms) per word

    def update_text(self):
        if self.current_index < len(self.words):
            word = self.words[self.current_index]
            self.text_label.setText(self.text_label.text() + " " + word)
            self.current_index += 1
        else:
            self.timer.stop()

    def open_main_form(self):
        self.close()
        self.form = FormScreen()   # ✅ Keep reference so it's not garbage collected
        self.form.show()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec())
