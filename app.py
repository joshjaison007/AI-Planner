import sys
import json
import os
import ollama
import pyscript

from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QScrollArea, QVBoxLayout, QWidget, QCalendarWidget
from datetime import date, datetime, timedelta

today = date.today() #date
now = datetime.now() #time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.days = {
            today.strftime("%m-%d"):                    today.strftime("%m-%d"),
            (today + timedelta(days=1)).strftime("%m-%d"): (today + timedelta(days=1)).strftime("%m-%d"),
            (today + timedelta(days=2)).strftime("%m-%d"): (today + timedelta(days=2)).strftime("%m-%d")
        } 

    def on_button_click(self):
        text = self.input.text() 
        response = ollama.generate('llama3.1:8b', 'Extract event details from the following text: ' + text + 
        ". Format it as JSON with keys: title, date, time, duration in minutes.  Format the date as MM-DD and time as HH:MM.  Today is " + today.strftime("%m-%d") + ". Here are the existing events:" 
        + json.dumps(self.load_events(), indent=2) + "If any event conflicts with existing ones, adjust the time accordingly and let the user know.")
        self.save_event(response['response'])
        print(response['response'])

    
    def save_event(self, response):
        # load existing events
        if os.path.exists("events.json") and os.path.getsize("events.json") > 0:
            with open("events.json", "r") as f:
                events = json.load(f)
        else:
            events = []

        # parse and add new event
        try:
            event = json.loads(response)
            events.append(event)
            with open("events.json", "w") as f:
                json.dump(events, f, indent=2)
            print("Event saved!")
        except json.JSONDecodeError:
            print("Couldn't parse response as JSON:", response)

    def load_events(self):
        if os.path.exists("events.json") and os.path.getsize("events.json") > 0:
            with open("events.json", "r") as f:
                return json.load(f)
        return []
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())