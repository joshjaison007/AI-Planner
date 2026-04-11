/**
 * ADD-EVENT.JS 
 * Merged Styles, UI, and Logic
 */

// 1. INJECT STYLES
const style = document.createElement('style');
style.textContent = `
    .event-box {
        position: absolute; left: 10px; right: 10px;
        background: rgba(138, 180, 248, 0.2);
        border-left: 4px solid #8ab4f8; color: white;
        padding: 8px; border-radius: 6px; font-size: 12px;
        z-index: 20; backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.1);
    }
    #addEventFab {
        position: fixed; bottom: 30px; right: 380px; 
        width: 60px; height: 60px; border-radius: 50%; 
        background: #8ab4f8; color: #000; font-size: 30px; 
        cursor: pointer; z-index: 99; border: none;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .modal-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.7); backdrop-filter: blur(10px);
        display: none; justify-content: center; align-items: center; z-index: 2000;
    }
`;
document.head.appendChild(style);

// 2. INJECT UI ELEMENTS (Button and Modal)
const uiContainer = document.createElement('div');
uiContainer.innerHTML = `
    <button id="addEventFab" onclick="togglePopup(true)">+</button>
    <div class="modal-overlay" id="eventModal">
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
    </div>
`;
document.body.appendChild(uiContainer);

// 3. LOGIC: SAVE & EXTRACT
window.togglePopup = (show) => {
    document.getElementById('eventModal').style.display = show ? 'flex' : 'none';
};

window.saveEvent = async () => {
    const eventData = {
        title: document.getElementById('evTitle').value,
        start_time: `${document.getElementById('evDate').value}T${document.getElementById('evTime').value}`,
        duration: 60
    };

    const res = await fetch('http://localhost:8000/api/add-event', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(eventData)
    });

    if (res.ok) {
        togglePopup(false);
        loadEvents(); 
    }
};

window.loadEvents = async () => {
    try {
        const res = await fetch('http://localhost:8000/api/events');
        const events = await res.json();
        
        // Remove existing boxes
        document.querySelectorAll('.event-box').forEach(b => b.remove());

        const dayContent = document.getElementById('dayContent');
        const rows = document.querySelectorAll('.time-row');

        events.forEach(ev => {
            const date = new Date(ev.start_time);
            const hour = date.getHours();
            const mins = date.getMinutes();
            
            const box = document.createElement('div');
            box.className = 'event-box';
            box.innerText = ev.title;
            
            // Positioning (100px per hour logic)
            const top = (hour * 100) + (mins * 1.66);
            box.style.top = top + 'px';
            box.style.height = '60px'; 

            if(rows[hour]) {
                rows[hour].querySelector('.time-content').appendChild(box);
            }
        });
    } catch (e) { console.log("Backend not connected yet."); }
};

// Initial load
setTimeout(loadEvents, 500);