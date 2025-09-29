import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush

from cbc_analyzer import analyze_cbc_report


class CBCReportScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CBC Report Analyzer")
        self.showFullScreen() # Default window size
        self.setStyleSheet("background-color: #ecf0f1;")

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.create_top_bar()
        self.create_title()
        self.create_main_content()

    def create_top_bar(self):
        top_bar = QHBoxLayout()
        self.layout.addLayout(top_bar)

        # Back Button
        back_btn = QPushButton("← Back")
        back_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        back_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 5px 10px;")
        back_btn.clicked.connect(self.go_back)
        top_bar.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # Upload Button
        upload_btn = QPushButton("📂 Upload CBC Report")
        upload_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        upload_btn.setStyleSheet("""
            background-color: #3498db; color: white; padding: 5px 15px;
        """)
        upload_btn.clicked.connect(self.upload_and_analyze)
        top_bar.addWidget(upload_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def create_title(self):
        title = QLabel("🩸 CBC Report Analyzer")
        title.setFont(QFont("Helvetica", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)
    
    def create_main_content(self):
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Test", "Value", "Unit", "Status"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setColumnWidth(0, 400)  # Test column
        self.table.setColumnWidth(1, 150)  # Value column
        self.table.setColumnWidth(2, 150)  # Unit column
        self.table.setColumnWidth(3, 150)
        self.layout.addWidget(self.table)

        # --- Spacer before remarks ---
        spacer_label = QLabel("")  # empty label as spacer
        spacer_label.setFixedHeight(20)  # increase height to push remarks down
        self.layout.addWidget(spacer_label)

        # Remarks
        remarks_label = QLabel("📝 Remarks:")
        remarks_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        remarks_label.setStyleSheet("color: #2c3e50;")
        self.layout.addWidget(remarks_label)

        self.remarks_box = QTextEdit()
        self.remarks_box.setFont(QFont("Arial", 12))
        self.remarks_box.setReadOnly(True)
        self.remarks_box.setStyleSheet("background-color: white; color: black;")
        self.layout.addWidget(self.remarks_box)


    def go_back(self):
        self.close()
        from home import open_health_dashboard
        open_health_dashboard()

    def upload_and_analyze(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CBC Report",
            "",
            "PDF or Image Files (*.pdf *.jpg *.jpeg *.png);;PDF Files (*.pdf);;Image Files (*.jpg *.jpeg *.png)"
        )
        if file_path:
            results, remarks = analyze_cbc_report(file_path)
            self.populate_table(results)
            self.populate_remarks(remarks)

    def populate_table(self, results):
        self.table.setRowCount(0)
        for r in results:
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            self.table.setItem(row_pos, 0, QTableWidgetItem(str(r["Test"])))
            self.table.setItem(row_pos, 1, QTableWidgetItem(str(r["Value"])))
            self.table.setItem(row_pos, 2, QTableWidgetItem(str(r["Unit"])))
            status_item = QTableWidgetItem(str(r["Status"]))
            status_lower = str(r["Status"]).lower()
            if status_lower == "low":
                status_item.setBackground(QBrush(QColor("#ff4d4d")))
            elif status_lower == "high":
                status_item.setBackground(QBrush(QColor("#ffb84d")))
            else:  # normal
                status_item.setBackground(QBrush(QColor("#99e699")))
            self.table.setItem(row_pos, 3, status_item)

    def populate_remarks(self, remarks):
        self.remarks_box.clear()
        for rem in remarks:
            self.remarks_box.append(f"• {rem}")
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()  # exit fullscreen



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CBCReportScreen()
    window.show()
    sys.exit(app.exec())
