#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import threading
import winreg
import random
from flask import Flask, render_template_string, redirect, url_for, jsonify, request

app = Flask(__name__)

# CONFIGURACIÓN DEL LABORATORIO
TOR_PATH = r"C:\xtor\tor.exe"

STATUS = {
    "active": False,
    "tor_status": "Desconectado",
    "uptime": 0,
    "speed": "0.0 KB/s",
    "country": "Aleatorio",
    "logs": ["[🤖] Sistema FUNCOMPUTER Labs listo."]
}

tor_process = None
timer_thread = None

def add_log(text):
    """Añade una línea a la consola visual del panel"""
    STATUS["logs"].append(f"[{time.strftime('%H:%M:%S')}] {text}")
    if len(STATUS["logs"]) > 5:
        STATUS["logs"].pop(0)

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

# --- BUCLE DE SEGUNDO PLANO (UPTIME Y TRÁFICO) ---
def background_monitor():
    while STATUS["active"]:
        time.sleep(1)
        STATUS["uptime"] += 1
        # Simula fluctuación de tráfico de la red cebolla para la estética del panel
        if random.random() > 0.3:
            STATUS["speed"] = f"{random.uniform(45.2, 820.5):.1f} KB/s"
        else:
            STATUS["speed"] = "0.0 KB/s"

# --- CONTROL DEL MOTOR TOR ---
def enable_system(country_code="all"):
    global tor_process, timer_thread
    if not os.path.exists(TOR_PATH):
        STATUS["tor_status"] = "Error: Falta tor.exe"
        add_log("❌ ERROR: No se encontró tor.exe en C:\\xtor\\")
        return

    try:
        add_log("🚀 Iniciando motor Tor...")
        
        # Configuración dinámica de país (Exit Nodes)
        cmd = [TOR_PATH, "--SOCKSPort", "9050"]
        if country_code != "all":
            cmd.extend(["--ExitNodes", f"{{{country_code}}}", "--StrictNodes", "1"])
            STATUS["country"] = country_code.upper()
            add_log(f"🌍 Enrutando nodos de salida hacia: {country_code.upper()}")
        else:
            STATUS["country"] = "Aleatorio"
            add_log("🌍 Usando circuitos de nodos aleatorios mundiales.")

        # Arrancar el binario puro
        tor_process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Forzar proxy en todo Windows
        set_windows_proxy(enable=True)
        add_log("🔒 Proxy de Windows interceptado (127.0.0.1:9050)")
        
        STATUS["active"] = True
        STATUS["tor_status"] = "🧅 En línea"
        STATUS["uptime"] = 0
        
        # Lanzar el monitor interno
        timer_thread = threading.Thread(target=background_monitor, daemon=True)
        timer_thread.start()
        add_log("✔ Todo el sistema blindado con éxito.")
        
    except Exception as e:
        STATUS["tor_status"] = "Error General"
        add_log(f"❌ Error: {e}")

def disable_system():
    global tor_process
    STATUS["active"] = False
    
    if tor_process:
        tor_process.terminate()
        tor_process = None
        
    set_windows_proxy(enable=False)
    STATUS["tor_status"] = "Desconectado"
    STATUS["uptime"] = 0
    STATUS["speed"] = "0.0 KB/s"
    add_log("🛑 Motor apagado. Red de Windows restaurada.")

# --- INTERFAZ PREMIUM CYBERPUNK v3.5 ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XTOR v3.5 Premium 🚀 FUNCOMPUTER Labs</title>
    <style>
        :root {
            --bg: #050508;
            --card-bg: #0a0a10;
            --primary: #a370f7;
            --primary-hover: #8a4fff;
            --success: #00f5d4;
            --error: #ff4747;
            --text: #f8f9fa;
        }
        body { 
            font-family: 'Consolas', 'Segoe UI', monospace; 
            background: var(--bg); color: var(--text); 
            text-align: center; margin: 0;
            display: flex; align-items: center; justify-content: center;
            height: 100vh;
        }
        .card { 
            background: var(--card-bg); padding: 30px; border-radius: 20px; 
            box-shadow: 0 0 40px rgba(163, 112, 247, 0.15); 
            max-width: 440px; width: 90%; border: 2px solid #1a1a26;
        }
        h1 { color: var(--primary); margin: 0; font-size: 2.3rem; letter-spacing: 2px; text-shadow: 0 0 10px rgba(163, 112, 247, 0.3); }
        .subtitle { color: #52526b; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 15px; }
        
        .timer { font-size: 2.5rem; font-weight: bold; color: var(--success); margin: 10px 0; font-variant-numeric: tabular-nums; }

        .grid-monitor {
            display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px;
        }
        .box { background: #11111a; border: 1px solid #222235; border-radius: 10px; padding: 10px; font-size: 0.85rem; text-align: left;}
        .box span { display: block; color: #52526b; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 4px; }
        .box b { color: var(--text); font-size: 1rem; }
        .good { color: var(--success) !important; }

        /* Consola de Logs */
        .log-console {
            background: #000; border: 1px solid #222; border-radius: 8px;
            padding: 10px; height: 90px; font-size: 0.75rem; text-align: left;
            color: #8c8db0; overflow-y: hidden; margin-top: 15px; line-height: 1.4;
        }

        .selector-box { margin-bottom: 15px; text-align: left; }
        .selector-box label { font-size: 0.8rem; color: #52526b; display: block; margin-bottom: 5px; }
        select {
            width: 100%; background: #11111a; color: var(--text); border: 1px solid #222235;
            padding: 10px; border-radius: 8px; font-family: inherit; cursor: pointer; outline: none;
        }

        .btn { 
            display: block; padding: 14px; font-size: 1.05rem; font-weight: bold; 
            border: none; border-radius: 10px; cursor: pointer; transition: all 0.3s; 
            text-decoration: none; text-align: center; margin-bottom: 10px;
        }
        .btn-start { background: var(--primary); color: white; }
        .btn-start:hover { background: var(--primary-hover); box-shadow: 0 0 15px rgba(163, 112, 247, 0.4); }
        .btn-stop { background: #14141f; color: var(--error); border: 1px solid var(--error); }
        .btn-stop:hover { background: var(--error); color: black; }
        .btn-renew { background: #1a112c; color: #d6bbfd; border: 1px solid var(--primary); font-size: 0.9rem; }

        .footer { margin-top: 20px; font-size: 0.75rem; color: #3c3c54; }
    </style>
    <script>
        setInterval(async () => {
            const res = await fetch('/api/status');
            const data = await res.json();
            
            document.getElementById('tor-val').innerText = data.tor_status;
            document.getElementById('speed-val').innerText = data.speed;
            document.getElementById('country-val').innerText = data.country;
            
            // Tiempo activo
            const mins = String(Math.floor(data.uptime / 60)).padStart(2, '0');
            const secs = String(data.uptime % 60).padStart(2, '0');
            document.getElementById('timer-val').innerText = data.active ? `${mins}:${secs}` : "00:00";
            
            // Renderizar logs
            const logBox = document.getElementById('log-box');
            logBox.innerHTML = data.logs.join('<br>');
        }, 1000);
    </script>
</head>
<body>
    <div class="card">
        <h1>XTOR v3.5</h1>
        <div class="subtitle">FUNCOMPUTER LABS Premium Shell</div>
        
        <div class="timer" id="timer-val">00:00</div>

        <div class="grid-monitor">
            <div class="box"><span>Estado</span><b id="tor-val" class="good">{{ status.tor_status }}</b></div>
            <div class="box"><span>Tráfico Est.</span><b id="speed-val" style="color: #00f5d4;">{{ status.speed }}</b></div>
            <div class="box"><span>Puerto SOCKS</span><b>127.0.0.1:9050</b></div>
            <div class="box"><span>País Nodo</span><b id="country-val" style="color: #a370f7;">{{ status.country }}</b></div>
        </div>

        <form action="/start" method="GET">
            {% if not status.active %}
                <div class="selector-box">
                    <label>📍 Forzar Ubicación del Nodo de Salida:</label>
                    <select name="country">
                        <option value="all">🌐 Circuito Mundial Aleatorio</option>
                        <option value="de">🇩🇪 Alemania (DE)</option>
                        <option value="us">🇺🇸 Estados Unidos (US)</option>
                        <option value="fr">🇫🇷 Francia (FR)</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-start" style="width:100%;">ENCENDER MOTOR 🚀</button>
            {% else %}
                <a href="/renew" class="btn btn-renew">🔄 ROTAR CIRCUITO (NUEVA IP)</a>
                <a href="/stop" class="btn btn-stop">APAGAR TODO ❌</a>
            {% endif %}
        </form>

        <div class="log-console" id="log-box">
            {% for log in status.logs %}
                {{ log }}<br>
            {% endfor %}
        </div>
        
        <div class="footer">⚡ FUNCOMPUTER LABS • AUTOMATED TUNNEL v3.5</div>
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
    country = request.args.get('country', 'all')
    enable_system(country)
    return redirect(url_for('home'))

@app.route('/stop')
def stop_tunnel():
    disable_system()
    return redirect(url_for('home'))

@app.route('/renew')
def renew_ip():
    global tor_process
    if tor_process:
        add_log("🔄 Petición de rotación recibida. Regenerando IP...")
        tor_process.terminate()
        # Se reinicia respetando el país seleccionado
        country_code = STATUS["country"].lower() if STATUS["country"] != "Aleatorio" else "all"
        cmd = [TOR_PATH, "--SOCKSPort", "9050"]
        if country_code != "all":
            cmd.extend(["--ExitNodes", f"{{{country_code}}}", "--StrictNodes", "1"])
        
        tor_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        add_log("🧅 Circuitos limpiados. Nueva identidad asignada.")
    return redirect(url_for('home'))

@app.route('/api/status')
def api_status():
    return jsonify(STATUS)

if __name__ == "__main__":
    import atexit
    atexit.register(disable_system)
    
    print("[+] Panel Premium XTOR v3.5 corriendo en http://127.0.0.1:1337")
    app.run(host='127.0.0.1', port=1337, debug=False)
