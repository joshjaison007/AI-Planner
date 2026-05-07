window.toggleSettings = function() { 
    document.getElementById('settingsOverlay').classList.toggle('active'); 
};

window.toggleLightMode = function() {
    const isLight = document.body.classList.toggle('light-mode');
    document.getElementById('modeBtn').innerText = isLight ? 'Light Mode' : 'Dark Mode';
};

window.toggleTimeFormat = function() {
    window.use24Hour = !window.use24Hour;
    document.getElementById('timeFormatBtn').innerText = window.use24Hour ? '24 Hour' : '12 Hour';
    if(typeof window.updateClock === 'function') window.updateClock();
    if(typeof window.renderDayGrid === 'function') window.renderDayGrid();
};

window.saveEmailSettings = async function() {
    const ntfy_channel = document.getElementById('ntfyChannel').value;
    
    try {
        const res = await fetch('http://localhost:8000/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ntfy_channel })
        });
        if(res.ok) {
            alert('Push configuration saved successfully!');
            // Send a test notification
            if(ntfy_channel) {
                fetch(`https://ntfy.sh/${ntfy_channel}`, {
                    method: 'POST',
                    body: 'Push notifications are now active for Liquid AI Planner!',
                    headers: {'Title': 'Setup Complete'}
                });
            }
        } else {
            alert('Failed to save configuration.');
        }
    } catch (e) {
        console.error(e);
        alert('Error saving configuration.');
    }
};



window.loadEmailSettings = async function() {
    try {
        const res = await fetch('http://localhost:8000/api/settings');
        if(res.ok) {
            const data = await res.json();
            if(data.ntfy_channel) document.getElementById('ntfyChannel').value = data.ntfy_channel;
            
            if(data.api_provider) {
                document.getElementById('apiProvider').value = data.api_provider;
            }
            if(data.api_key) {
                document.getElementById('apiKey').value = data.api_key;
            }
            if(data.api_model) {
                document.getElementById('apiModel').value = data.api_model;
            }
            window.handleProviderChange();
        }
    } catch(e) {
        console.error("Could not load push settings");
    }
};

window.handleProviderChange = function() {
    const provider = document.getElementById('apiProvider').value;
    const settingsFields = document.getElementById('apiSettingsFields');
    const modelContainer = document.getElementById('modelNameContainer');
    
    if (provider === 'gemini_default') {
        settingsFields.style.display = 'none';
    } else {
        settingsFields.style.display = 'flex';
        if (provider === 'gemini') {
            modelContainer.style.display = 'none';
        } else {
            modelContainer.style.display = 'flex';
        }
    }
};

window.saveApiSettings = async function() {
    const provider = document.getElementById('apiProvider').value;
    const key = document.getElementById('apiKey').value;
    const model = document.getElementById('apiModel').value;
    
    try {
        const res = await fetch('http://localhost:8000/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                api_provider: provider,
                api_key: key,
                api_model: model
            })
        });
        if(res.ok) {
            alert('AI Configuration saved successfully!');
        } else {
            alert('Failed to save AI configuration.');
        }
    } catch (e) {
        console.error(e);
        alert('Error saving AI configuration.');
    }
};

document.addEventListener('DOMContentLoaded', window.loadEmailSettings);
