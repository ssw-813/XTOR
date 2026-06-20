#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import threading
import winreg
from flask import Flask, render_template_string, redirect, url_for, jsonify

app = Flask(__name__)

# CONFIGURACIÓN DEL LABORATORIO
TOR_PATH = r"C:\xtor\tor.exe"

STATUS = {
    "active": False,
    "tor_status": "Desconectado",
    "uptime": 0
}

tor_process = None
timer_thread = None

# --- REGISTRO DE WINDOWS PROXY ---
def set_windows_proxy(enable=True):
    INTERNET_SETTINGS = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, INTERNET_SETTINGS, 0, winreg.KEY_WRITE)
        if enable:
            winreg.SetValueEx(registry_key, "ProxyServer", 0, winreg.REG_SZ, "socks=127.0.0.1:9050")
            winreg.SetValueEx(registry_key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
        else:
            winreg.SetValueEx(registry_key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(registry_key)
    except Exception as e:
        print(f"[-] Error Proxy Registro: {e}")

# --- CONTADOR DE TIEMPO (UPTIME) ---
def track_uptime():
    while STATUS["active"]:
        time.sleep(1)
        STATUS["uptime"] += 1

# --- CONTROL DEL MOTOR ---
def enable_system():
    global tor_process, timer_thread
    if not os.path.exists(TOR_PATH):
        STATUS["tor_status"] = "Error: Falta tor.exe"
        return

    try:
        # 1. ARRANCAR TOR
        tor_process = subprocess.Popen(
            [TOR_PATH, "--SOCKSPort", "9050"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # 2. ACTIVAR PROXY EN EL SISTEMA
        set_windows_proxy(enable=True)
        
        STATUS["active"] = True
        STATUS["tor_status"] = "🧅 Red Tor Conectada"
        STATUS["uptime"] = 0
        
        # Lanzar el reloj del laboratorio en segundo plano
        timer_thread = threading.Thread(target=track_uptime, daemon=True)
        timer_thread.start()
        
    except Exception as e:
        STATUS["tor_status"] = f"Error General: {e}"

def disable_system():
    global tor_process
    STATUS["active"] = False
    
    if tor_process:
        tor_process.terminate()
        tor_process = None
        
    set_windows_proxy(enable=False)
    STATUS["tor_status"] = "Desconectado"
    STATUS["uptime"] = 0

# --- INTERFAZ PREMIUM CYBERPUNK ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XTOR v3.0 Premium 🚀 FUNCOMPUTER Labs</title>
    <style>
        :root {
            --bg: #060608;
            --card-bg: #0d0d14;
            --primary: #9b5de5;
            --primary-hover: #8338ec;
            --success: #00f5d4;
            --error: #ff5400;
            --text: #f8f9fa;
        }
        body { 
            font-family: 'Consolas', 'Segoe UI', monospace; 
            background: var(--bg); 
            color: var(--text); 
            text-align: center; 
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        .card { 
            background: var(--card-bg); 
            padding: 35px; 
            border-radius: 20px; 
            box-shadow: 0 0 50px rgba(155, 93, 229, 0.15); 
            max-width: 420px; 
            width: 90%; 
            border: 2px solid #1f1f2e;
            position: relative;
        }
        h1 { color: var(--primary); margin: 0; font-size: 2.5rem; letter-spacing: 2px; }
        .subtitle { color: #5c5c75; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 20px; }
        
        .main-icon { font-size: 4rem; margin-bottom: 10px; display: inline-block; }
        {% if status.active %}
        .main-icon { animation: spin 4s linear infinite; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        {% endif %}

        /* Panel de Monitorización Real */
        .monitor-panel {
            background: #13131f;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: left;
            border: 1px solid #252538;
        }
        .monitor-line { font-size: 0.9rem; margin: 8px 0; display: flex; justify-content: space-between; }
        .val-good { color: var(--success); font-weight: bold; }
        .val-bad { color: var(--error); font-weight: bold; }
        
        .timer { font-size: 2.2rem; font-weight: bold; color: var(--success); margin: 15px 0; font-variant-numeric: tabular-nums; text-shadow: 0 0 10px rgba(0, 245, 212, 0.3); }

        .btn { 
            display: block; padding: 15px; font-size: 1.1rem; font-weight: bold; 
            border: none; border-radius: 10px; cursor: pointer; transition: all 0.3s; 
            text-decoration: none; text-align: center; margin-bottom: 10px;
        }
        .btn-start { background: var(--primary); color: white; }
        .btn-start:hover { background: var(--primary-hover); box-shadow: 0 0 20px rgba(155, 93, 229, 0.5); }
        .btn-stop { background: #1a1a26; color: var(--error); border: 1px solid var(--error); }
        .btn-stop:hover { background: var(--error); color: black; }
        .btn-renew { background: #160f29; color: #e0aaff; border: 1px solid var(--primary); font-size: 0.95rem; }
        .btn-renew:hover { background: var(--primary); color: white; }

        .footer { margin-top: 25px; font-size: 0.75rem; color: #44445c; }
    </style>
    <script>
        // Auto-refrescar los datos del panel dinámicamente cada segundo
        setInterval(async () => {
            const res = await fetch('/api/status');
            const data = await res.json();
            
            document.getElementById('tor-val').innerText = data.tor_status;
            
            // Formatear Uptime (MM:SS)
            const mins = String(Math.floor(data.uptime / 60)).padStart(2, '0');
            const secs = String(data.uptime % 60).padStart(2, '0');
            if (data.active) {
                document.getElementById('timer-val').innerText = `${mins}:${secs}`;
            } else {
                document.getElementById('timer-val').innerText = `00:00`;
            }
        }, 1000);
    </script>
</head>
<body>
    <div class="card">
        <h1>XTOR v3.0</h1>
        <div class="subtitle">Onion Routing Panel</div>
        
        <div class="main-icon">🧅</div>

        <div class="timer" id="timer-val">00:00</div>

        <div class="monitor-panel">
            <div class="monitor-line"><span>⚡ Estado Motor:</span> <span id="tor-val" class="{% if status.active %}val-good{% else %}val-bad{% endif %}">{{ status.tor_status }}</span></div>
            <div class="monitor-line"><span>🌐 Puerto SOCKS5:</span> <span class="val-good">127.0.0.1:9050</span></div>
        </div>

        {% if not status.active %}
            <a href="/start" class="btn btn-start">ENCENDER MOTOR 🚀</a>
        {% else %}
            <a href="/renew" class="btn btn-renew">🔄 CAMBIAR IDENTIDAD (NUEVA IP)</a>
            <a href="/stop" class="btn btn-stop">APAGAR TODO ❌</a>
        {% endif %}
        
        <div class="footer">⚡ FUNCOMPUTER LABS • AUTOMATED TUNNEL</div>
    </div>
</body>
</html>
"""

# --- RUTAS DE FLASK ---
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, status=STATUS)

@app.route('/start')
def start_tunnel():
    enable_system()
    return redirect(url_for('home'))

@app.route('/stop')
def stop_tunnel():
    disable_system()
    return redirect(url_for('home'))

@app.route('/renew')
def renew_ip():
    global tor_process
    if tor_process:
        # Reinicio express para obligar a Tor a limpiar circuitos antiguos y renovar IP
        tor_process.terminate()
        tor_process = subprocess.Popen(
            [TOR_PATH, "--SOCKSPort", "9050"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        STATUS["tor_status"] = "🧅 IP Renovada Exitosamente"
    return redirect(url_for('home'))

@app.route('/api/status')
def api_status():
    return jsonify(STATUS)

if __name__ == "__main__":
    import atexit
    atexit.register(disable_system)
    
    print("[+] Panel Premium XTOR corriendo en http://127.0.0.1:1337")
    app.run(host='127.0.0.1', port=1337, debug=False)
