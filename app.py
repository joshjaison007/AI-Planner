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
        raw = response['response'].strip()
        # remove markdown fences if present
        raw = raw.replace('```json', '').replace('```', '').strip()
        # find outermost braces
        start = raw.index('{')
        end = raw.rindex('}') + 1
        raw = raw[start:end]
        data = json.loads(raw)
        event = data["event"]
        existing.append(event)
        with open("events.json", "w") as f:
            json.dump(existing, f, indent=2)
        return jsonify({"status": "ok", "event": event, "message": data.get("message", "Event added!")})
    except Exception as e:
        print("AI raw response:", response['response'])
        print("Error:", e)
        return jsonify({"status": "error", "message": "AI failed to format JSON"})

@app.route("/api/delete-event", methods=["POST", "OPTIONS"])
def delete_event():
    if request.method == "OPTIONS": return jsonify({}), 200
    data = request.json
    title_to_delete = data.get("title")
    start_time_to_delete = data.get("start_time")
    
    if os.path.exists("events.json") and os.path.getsize("events.json") > 0:
        with open("events.json", "r") as f:
            existing = json.load(f)
            
        new_list = [evt for evt in existing if not (evt.get("title") == title_to_delete and (evt.get("start_time") == start_time_to_delete or evt.get("start") == start_time_to_delete))]
        
        with open("events.json", "w") as f:
            json.dump(new_list, f, indent=2)
    return jsonify({"status": "ok"})

@app.route("/api/update-event", methods=["POST", "OPTIONS"])
def update_event():
    if request.method == "OPTIONS": return jsonify({}), 200
    data = request.json
    old_title = data.get("title")
    old_time = data.get("old_start_time")
    new_time = data.get("new_start_time")
    new_title = data.get("new_title", old_title)
    
    if os.path.exists("events.json") and os.path.getsize("events.json") > 0:
        with open("events.json", "r") as f:
            existing = json.load(f)
            
        for evt in existing:
            if evt.get("title") == old_title and (evt.get("start_time") == old_time or evt.get("start") == old_time):
                evt["start_time"] = new_time
                evt["title"] = new_title
                break
                
        with open("events.json", "w") as f:
            json.dump(existing, f, indent=2)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=8000, debug=True) # Standardizing to port 8000
