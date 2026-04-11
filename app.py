import sys
import json
import os
import ollama
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QScrollArea, QVBoxLayout, QWidget, QCalendarWidget
from datetime import date, timedelta

today = date.today()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.days = {
            today.strftime("%m-%d"):                    today.strftime("%m-%d"),
            (today + timedelta(days=1)).strftime("%m-%d"): (today + timedelta(days=1)).strftime("%m-%d"),
            (today + timedelta(days=2)).strftime("%m-%d"): (today + timedelta(days=2)).strftime("%m-%d")
        }

        self.setWindowTitle("My Planner")
        self.setGeometry(100, 100, 400, 300)
        
        self.input = QLineEdit()  
        
        submit = QPushButton("Submit")
        submit.clicked.connect(self.on_button_click)

        self.columns = {}
        day_layout = QHBoxLayout()

        for date_key, label in self.days.items():
            col_widget = QWidget()
            col_layout = QVBoxLayout()
            col_layout.addWidget(QLabel(f"<b>{label}</b>"))  # header

            self.columns[date_key] = col_layout  # save for later

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(col_widget)
            col_widget.setLayout(col_layout)

            day_layout.addWidget(scroll)

        # add the 3 columns to your main layout

    def on_button_click(self):
        text = self.input.text() 
        response = ollama.generate('llama3.1:8b', 'Extract event details from the following text: ' + text + 
        ". Format it as JSON with keys: title, date, time, location.  Format the date as MM-DD and time as HH:MM.  Today is " + today.strftime("%m-%d") + ".")
        print(response['response'])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())