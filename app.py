import json
import os
import ollama
from flask import Flask, render_template, request, jsonify
from datetime import date, datetime

app = Flask(__name__)
today = date.today()

@app.route("/")
def index():
    return render_template("index2.html")

@app.route("/events", methods=["GET"])
def get_events():
    if os.path.exists("events.json") and os.path.getsize("events.json") > 0:
        with open("events.json", "r") as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route("/add-event", methods=["POST"])
def add_event():
    text = request.json["text"]
    existing = []
    if os.path.exists("events.json") and os.path.getsize("events.json") > 0:
        with open("events.json", "r") as f:
            existing = json.load(f)

    response = ollama.generate('llama3.1:8b', 'Extract event details from the following text: ' + text + 
        ". Format it as JSON with keys: title, date, time, duration in minutes.  Format the date as MM-DD and time as HH:MM.  Today is " 
        + today.strftime("%m-%d") + ". Here are the existing events:" + json.dumps(existing, indent=2) 
        + "If any event conflicts with existing ones, adjust the time accordingly and let the user know.")
    try:
        event = json.loads(response['response'])
        existing.append(event)
        with open("events.json", "w") as f:
            json.dump(existing, f, indent=2)
        return jsonify({"status": "ok", "event": event})
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": response['response']})

if __name__ == "__main__":
    app.run(debug=True)