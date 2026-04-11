import sys
import json
import os
import ollama
from PyQt5.QtWidgets import QApplication, QLineEdit, QMainWindow, QPushButton, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Planner")
        self.setGeometry(100, 100, 400, 300)
        
        self.input = QLineEdit()  
        
        submit = QPushButton("Submit")
        submit.clicked.connect(self.on_button_click)
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.input) 
        layout.addWidget(submit)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def on_button_click(self):
        text = self.input.text() 
        response = ollama.generate('llama3.1:8b', 'Extract event details from the following text: ' + text + 
        ". Format it as JSON with keys: title, date, time, location.")
        print(response['response'])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())