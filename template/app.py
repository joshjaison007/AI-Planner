import json
import os
import ollama
from flask import Flask, render_template, request, jsonify
from datetime import date, datetime

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')
today = date.today()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route("/")
def index():
    return render_template("index3_5.html")  

@app.route("/api/events", methods=["GET"]) # Adjusted route to match JS fetch
def get_events():
    if os.path.exists("events.json") and os.path.getsize("events.json") > 0:
        with open("events.json", "r") as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route("/api/add-event", methods=["POST", "OPTIONS"]) # Adjusted route to match JS fetch
def add_event():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    # Handle both AI text and Manual form data
    incoming = request.json
    existing = []
    
    if os.path.exists("events.json") and os.path.getsize("events.json") > 0:
        with open("events.json", "r") as f:
            existing = json.load(f)

    # If it's a manual entry from the "+" button form
    if "title" in incoming and "start_time" in incoming:
        existing.append(incoming)
        with open("events.json", "w") as f:
            json.dump(existing, f, indent=2)
        return jsonify({"status": "ok", "message": "Manual event added!"})

    # If it's an AI text query
    text = incoming.get("text", "")
    response = ollama.generate('llama3.1:8b', 
        f'Extract event details from: {text}. '
        f'Today is {today.strftime("%Y-%m-%d")}. '
        f'Return JSON only: {{"event": {{"title": "str", "start_time": "YYYY-MM-DDTHH:MM", "duration": 60}}, "message": "str"}}')

    try:
        data = json.loads(response['response'])
        event = data["event"]
        existing.append(event)
        with open("events.json", "w") as f:
            json.dump(existing, f, indent=2)
        return jsonify({"status": "ok", "event": event, "message": data["message"]})
    except:
        return jsonify({"status": "error", "message": "AI failed to format JSON"})

if __name__ == "__main__":
    app.run(port=8000, debug=True) # Standardizing to port 8000