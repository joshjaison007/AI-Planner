import json
import os
import csv
import io
import sys
# TIP: To run this app without a terminal popping up on Windows, rename this file to 'app.pyw' 
# or run it using: pythonw app.py
import threading
import time
import requests



import webview
from plyer import notification
import logging
import os

from flask import Flask, render_template, request, jsonify, make_response
from datetime import date, datetime, timedelta

# Global registry for windows to avoid recursion in the JS bridge
windows = {
    'main': None,
    'widget': None
}

class Api:
    def __init__(self):
        self.widget_visible = False

    def show_main_window(self):
        logging.info("show_main_window triggered")
        main_win = windows.get('main')
        if main_win:
            try:
                main_win.show()
                main_win.restore()
                def navigate():
                    time.sleep(0.3)
                    try:
                        logging.info("Evaluating JS goToToday")
                        main_win.evaluate_js('if(typeof goToToday === "function") goToToday()')
                    except Exception as je:
                        logging.error(f"JS Eval fail: {je}")
                threading.Thread(target=navigate, daemon=True).start()
            except Exception as e:
                logging.error(f"show_main_window error: {e}")

    def toggle_widget(self):
        logging.info("toggle_widget called")
        widget_win = windows.get('widget')
        if widget_win:
            try:
                if self.widget_visible:
                    widget_win.hide()
                    self.widget_visible = False
                else:
                    widget_win.show()
                    self.widget_visible = True
                return self.widget_visible
            except Exception as e:
                logging.error(f"Error toggling widget: {e}")
                self.widget_visible = False
        return self.widget_visible

class WidgetApi:
    def __init__(self, main_api):
        self.main_api = main_api

    def show_main_window(self):
        logging.info("WidgetApi: show_main_window triggered")
        self.main_api.show_main_window()








if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    application_path = os.path.dirname(sys.executable)
    data_path = os.path.join(application_path, "Resources")
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
    application_path = base_path
    data_path = base_path

DATA_FILE = os.path.join(data_path, "events.json")
CONFIG_FILE = os.path.join(data_path, "config.json")

app = Flask(__name__, template_folder=base_path, static_folder=base_path, static_url_path='')
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

@app.route("/widget")
def widget():
    return render_template("widget.html")

@app.route("/api/notify", methods=["POST", "OPTIONS"])
def trigger_notification():
    if request.method == "OPTIONS": return jsonify({}), 200
    data = request.json
    try:
        notification.notify(
            title=data.get("title", "Liquid AI Planner"),
            message=data.get("message", "You have an upcoming event!"),
            app_name="Liquid AI Planner",
            timeout=10
        )
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Notification error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/settings", methods=["GET", "POST", "OPTIONS"])
def manage_settings():
    if request.method == "OPTIONS": return jsonify({}), 200
    if request.method == "GET":
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return jsonify(json.load(f))
        return jsonify({})
    if request.method == "POST":
        data = request.json
        config = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
        if "ntfy_channel" in data: config["ntfy_channel"] = data.get("ntfy_channel")
        if "api_provider" in data: config["api_provider"] = data.get("api_provider")
        if "api_key" in data: config["api_key"] = data.get("api_key")
        if "api_model" in data: config["api_model"] = data.get("api_model")

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        return jsonify({"status": "ok"})

@app.route("/api/events", methods=["GET"])
def get_events():
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, "r") as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route("/api/add-event", methods=["POST", "OPTIONS"])
def add_event():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    incoming = request.json
    existing = []
    
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, "r") as f:
            existing = json.load(f)

    if "title" in incoming and "start_time" in incoming:
        existing.append(incoming)
        with open(DATA_FILE, "w") as f:
            json.dump(existing, f, indent=2)
        return jsonify({"status": "ok", "message": "Manual event added!"})

@app.route("/api/ai-command", methods=["POST", "OPTIONS"])
def ai_command():
    if request.method == "OPTIONS": return jsonify({}), 200
    incoming = request.json
    existing = []
    
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, "r") as f:
            existing = json.load(f)

    try:
        text = incoming.get("text", "")
        system_prompt = (
            f"SYSTEM ROLE: You are an expert calendar AI agent. "
            f"INSTRUCTION: Process the user command: '{text}'. Today is {today.strftime('%Y-%m-%d')}. "
            f"CONTEXT: Current events are {json.dumps(existing)}. "
            f"CAPABILITIES: You can 'add' new events or 'delete' existing ones. "
            f"If the user asks to remove, delete, cancel, or clear an event, identify the event in the context and issue a 'delete' action. "
            f"If a duration is provided (e.g. '2 hours'), convert it to minutes and include it in the 'duration' field. "
            f"MANDATORY OUTPUT: Return ONLY a JSON object with this structure: "
            f"{{\"actions\": ["
            f"{{\"type\": \"add\", \"event\": {{\"title\": \"...\", \"start_time\": \"YYYY-MM-DDTHH:MM\", \"duration\": 60}}}}, "
            f"{{\"type\": \"delete\", \"title\": \"...\", \"start_time\": \"YYYY-MM-DDTHH:MM\"}}"
            f"], \"message\": \"Summary of actions taken\"}}"
        )

        config = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                
        provider = config.get("api_provider", "gemini_default")
        
        if provider == "gemini_default" or provider == "gemini":
            import google.generativeai as genai
            api_key = config.get("api_key") if provider == "gemini" else "AIzaSyAQHeNU-u-Jvu6ix5nqGQInc4cGJdpL93g"
            if not api_key: raise Exception("API Key is required for Custom Gemini")
            genai.configure(api_key=api_key)
            local_model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
            response = local_model.generate_content(system_prompt)
            data = json.loads(response.text)
            
        elif provider in ["openai", "groq"]:
            api_key = config.get("api_key")
            if not api_key: raise Exception("API Key is required")
            
            base_url = "https://api.openai.com/v1/chat/completions"
            if provider == "groq": base_url = "https://api.groq.com/openai/v1/chat/completions"
            
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": config.get("api_model") or ("gpt-3.5-turbo" if provider == "openai" else "llama3-8b-8192"),
                "messages": [{"role": "system", "content": system_prompt}],
                "response_format": {"type": "json_object"}
            }
            r = requests.post(base_url, headers=headers, json=payload)
            if r.status_code != 200: raise Exception(f"API Error {r.status_code}: {r.text}")
            response_text = r.json()["choices"][0]["message"]["content"]
            data = json.loads(response_text)
            
        actions = data.get("actions", [])
        for action in actions:
            if action.get("type") == "add":
                existing.append(action["event"])
            elif action.get("type") == "delete":
                del_title = action.get("title")
                del_time = action.get("start_time")
                existing = [e for e in existing if not (e.get("title") == del_title and (e.get("start_time") == del_time or e.get("start") == del_time))]
        
        with open(DATA_FILE, "w") as f:
            json.dump(existing, f, indent=2)
            
        return jsonify({"status": "ok", "message": data.get("message", "Tasks completed.")})
            
    except Exception as e:
        error_msg = str(e)
        print(f"Failed AI Response: {error_msg}")
        if "429" in error_msg or "quota" in error_msg.lower():
            return jsonify({"status": "error", "message": "API Limit Exceeded: You've reached your free tier limit for today. Please wait a bit or try again later!"})
        return jsonify({"status": "error", "message": "AI failed to process request: " + error_msg})


@app.route("/api/delete-event", methods=["POST", "OPTIONS"])
def delete_event():
    if request.method == "OPTIONS": return jsonify({}), 200
    data = request.json
    title_to_delete = data.get("title")
    start_time_to_delete = data.get("start_time")
    
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, "r") as f:
            existing = json.load(f)
            
        new_list = [evt for evt in existing if not (evt.get("title") == title_to_delete and (evt.get("start_time") == start_time_to_delete or evt.get("start") == start_time_to_delete))]
        
        with open(DATA_FILE, "w") as f:
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
    
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, "r") as f:
            existing = json.load(f)
            
        for evt in existing:
            if evt.get("title") == old_title and (evt.get("start_time") == old_time or evt.get("start") == old_time):
                evt["start_time"] = new_time
                evt["title"] = new_title
                break
                
        with open(DATA_FILE, "w") as f:
            json.dump(existing, f, indent=2)
    return jsonify({"status": "ok"})

@app.route("/api/export-csv")
def export_csv():
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, "r") as f:
            events = json.load(f)
    else:
        events = []

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Subject", "Start Date", "Start Time", "End Date", "End Time", "Description"])

    for evt in events:
        try:
            start_str = evt.get("start_time") or evt.get("start")
            if not start_str: continue
            
            start_dt = datetime.fromisoformat(start_str)
            duration = int(evt.get("duration", 60))
            end_dt = start_dt + timedelta(minutes=duration)
            
            subject = evt.get("title", "Untitled Event")
            start_date = start_dt.strftime("%m/%d/%Y")
            start_time = start_dt.strftime("%I:%M %p")
            end_date = end_dt.strftime("%m/%d/%Y")
            end_time = end_dt.strftime("%I:%M %p")
            description = f"Exported from Liquid AI. Duration: {duration} mins."
            
            writer.writerow([subject, start_date, start_time, end_date, end_time, description])
        except Exception as e:
            print(f"Skipping event in export: {e}")

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=calendar_export.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@app.route("/api/import-csv", methods=["POST"])
def import_csv():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No file selected"}), 400
    
    try:
        content = file.read().decode("utf-8")
        stream = io.StringIO(content)
        reader = csv.DictReader(stream)
        
        new_events = []
        for row in reader:
            subject = row.get("Subject")
            start_date = row.get("Start Date")
            start_time = row.get("Start Time", "12:00 AM")
            end_date = row.get("End Date", start_date)
            end_time = row.get("End Time", start_time)
            
            if not subject or not start_date: continue
            
            start_dt = None
            fmts = ["%m/%d/%Y %I:%M %p", "%Y-%m-%d %I:%M %p", "%m/%d/%Y %H:%M", "%Y-%m-%d %H:%M"]
            for fmt in fmts:
                try:
                    start_dt = datetime.strptime(f"{start_date} {start_time}", fmt)
                    break
                except: continue
            
            if not start_dt: continue
            
            end_dt = None
            for fmt in fmts:
                try:
                    end_dt = datetime.strptime(f"{end_date} {end_time}", fmt)
                    break
                except: continue
            
            duration = 60
            if end_dt and end_dt > start_dt:
                duration = int((end_dt - start_dt).total_seconds() / 60)
            
            new_events.append({
                "title": subject,
                "start_time": start_dt.strftime("%Y-%m-%dT%H:%M"),
                "duration": duration
            })
            
        if not new_events:
            return jsonify({"status": "error", "message": "No valid events found in CSV. Please check headers and date format."}), 400

        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
            with open(DATA_FILE, "r") as f:
                existing = json.load(f)
        else:
            existing = []
            
        existing.extend(new_events)
        with open(DATA_FILE, "w") as f:
            json.dump(existing, f, indent=2)
            
        return jsonify({"status": "ok", "message": f"Successfully imported {len(new_events)} events!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def ntfy_scheduler():
    while True:
        try:
            if not os.path.exists(CONFIG_FILE):
                time.sleep(60)
                continue
                
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                
            channel = config.get("ntfy_channel")
            last_sent_date = config.get("last_sent_date")
            
            now = datetime.now()
            today_str = now.strftime("%Y-%m-%d")
            
            if channel and now.hour >= 8 and last_sent_date != today_str:
                if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
                    with open(DATA_FILE, "r") as f:
                        events = json.load(f)
                        
                    today_events = []
                    for e in events:
                        start_str = e.get("start_time") or e.get("start")
                        if start_str and start_str.startswith(today_str):
                            today_events.append(e)
                            
                    if today_events:
                        today_events.sort(key=lambda x: x.get("start_time") or x.get("start"))
                        
                        msg = f"Your Plan for {now.strftime('%A, %b %d')}:\n"
                        for e in today_events:
                            try:
                                t = datetime.fromisoformat(e.get("start_time") or e.get("start")).strftime("%I:%M %p")
                            except:
                                t = "Unknown time"
                            dur = e.get("duration", 60)
                            msg += f"• {t} - {e.get('title')} ({dur} mins)\n"
                        
                        requests.post(f"https://ntfy.sh/{channel}", 
                            data=msg.encode('utf-8'),
                            headers={"Title": f"Liquid Planner - {today_str}", "Tags": "calendar"},
                            timeout=10
                        )
                        
                config["last_sent_date"] = today_str
                with open(CONFIG_FILE, "w") as f:
                    json.dump(config, f)
                    
        except Exception as e:
            print(f"Scheduler error: {e}")
            
        time.sleep(60)



def start_server():
    app.run(host='127.0.0.1', port=8000, debug=False, use_reloader=False)

if __name__ == "__main__":
    import ctypes
    # Prevent multiple instances of the app
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "LiquidAIPlannerSingleInstanceMutex")
    if ctypes.windll.kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
        print("Application is already running.")
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == '--server':
        app.run(host='0.0.0.0', port=8000, debug=True)
    else:
        t = threading.Thread(target=start_server)
        t.daemon = True
        t.start()
        
        t2 = threading.Thread(target=ntfy_scheduler)
        t2.daemon = True
        t2.start()


        
        api = Api()
        main_window = webview.create_window('Liquid AI', 'http://127.0.0.1:8000', width=1200, height=800, js_api=api)
        windows['main'] = main_window
        def on_closing(window):
            logging.info("Main window closing event")
            window.hide()
            return False

        main_window.events.closing += on_closing
        
        widget_api = WidgetApi(api)
        widget_window = webview.create_window('Liquid Task Widget', 'http://127.0.0.1:8000/widget', width=190, height=330, frameless=True, on_top=True, background_color='#0f0f0f', hidden=True, js_api=widget_api)
        windows['widget'] = widget_window
        api.widget_visible = False

        def on_widget_closing(window):
            logging.info("Widget window closing event")
            window.hide()
            return False

        widget_window.events.closing += on_widget_closing
        
        webview.start()
