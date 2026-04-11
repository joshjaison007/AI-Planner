// Ensure this is at the top of add-event.js
const style = document.createElement('style');
style.textContent = `
    .event-box {
        position: absolute; left: 10px; right: 10px;
        background: rgba(138, 180, 248, 0.4);
        border-left: 4px solid #8ab4f8; color: white;
        padding: 8px; border-radius: 6px; font-size: 12px;
        z-index: 20; backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.1);
        pointer-events: none;
    }
    .modal-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.7); backdrop-filter: blur(10px);
        display: none; justify-content: center; align-items: center; z-index: 2000;
    }
`;
document.head.appendChild(style);

// Inject the Popup HTML
const modalDiv = document.createElement('div');
modalDiv.id = 'eventModal';
modalDiv.className = 'modal-overlay';
modalDiv.innerHTML = `
    <div style="background: #1a1b2e; padding: 35px; border-radius: 30px; width: 400px; border: 1px solid rgba(255,255,255,0.1);">
        <h2 style="color:#8ab4f8; margin-bottom:20px;">New Event</h2>
        <input type="text" id="evTitle" placeholder="Title" style="width:100%; padding:12px; border-radius:20px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:white; margin-bottom:15px;">
        <input type="date" id="evDate" style="width:100%; padding:12px; border-radius:20px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:white; margin-bottom:15px; color-scheme:dark;">
        <input type="time" id="evTime" style="width:100%; padding:12px; border-radius:20px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:white; margin-bottom:25px; color-scheme:dark;">
        <div style="display:flex; gap:10px;">
            <button onclick="togglePopup(false)" style="flex:1; padding:10px; border-radius:20px; background:rgba(255,255,255,0.1); color:white; border:none; cursor:pointer;">Cancel</button>
            <button onclick="saveEvent()" style="flex:1; padding:10px; border-radius:20px; background:#8ab4f8; color:black; border:none; cursor:pointer; font-weight:bold;">Create</button>
        </div>
    </div>
`;
document.body.appendChild(modalDiv);

window.togglePopup = (show) => {
    document.getElementById('eventModal').style.display = show ? 'flex' : 'none';
};

window.saveEvent = async () => {
    const title = document.getElementById('evTitle').value;
    const date = document.getElementById('evDate').value;
    const time = document.getElementById('evTime').value;
    
    if(!title || !date || !time) return alert("Fill all fields");

    const eventData = {
        title: title,
        start_time: `${date}T${time}`,
        duration: 60
    };

    try {
        const res = await fetch('http://localhost:8000/api/add-event', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(eventData)
        });

        if (res.ok) {
            document.getElementById('evTitle').value = '';
            document.getElementById('evDate').value = '';
            document.getElementById('evTime').value = '';
            togglePopup(false);
            if (typeof syncWithMCP === 'function') {
                syncWithMCP();
            }
        } else {
            const errText = await res.text();
            alert("Failed to add event: " + errText);
        }
    } catch (err) {
        console.error("Fetch error:", err);
        alert("Could not connect to the backend server. Is app.py running?");
    }
};