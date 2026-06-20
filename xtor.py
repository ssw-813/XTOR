#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import winreg # Para controlar el proxy de Windows directamente
from flask import Flask, render_template_string, redirect, url_for

app = Flask(__name__)

# Estado global de la aplicación
STATUS = {"active": False, "tor_status": "Desconectado"}
tor_process = None
TOR_PATH = r"C:\xtor\tor.exe" 

# --- FUNCIONES PARA EL PROXY AUTOMÁTICO DE WINDOWS ---
def set_windows_proxy(enable=True):
    """Activa o desactiva el proxy SOCKS5 en el registro de Windows"""
    INTERNET_SETTINGS = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, INTERNET_SETTINGS, 0, winreg.KEY_WRITE)
        if enable:
            # Configura todo el sistema para usar el puerto SOCKS de Tor
            winreg.SetValueEx(registry_key, "ProxyServer", 0, winreg.REG_SZ, "socks=127.0.0.1:9050")
            winreg.SetValueEx(registry_key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
            print("[✔] Proxy de Windows ACTIVADO automáticamente (127.0.0.1:9050)")
        else:
            # Desactiva el proxy por completo
            winreg.SetValueEx(registry_key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            print("[✔] Proxy de Windows DESACTIVADO automáticamente.")
        winreg.CloseKey(registry_key)
    except Exception as e:
        print(f"[-] No se pudo cambiar el proxy de Windows: {e}")

# --- ENCIÉNDELO TODO ---
def enable_tor():
    global tor_process
    if not os.path.exists(TOR_PATH):
        STATUS["tor_status"] = "Error: Falta tor.exe en C:\\xtor\\"
        return

    try:
        # Arrancamos el motor puro de Tor
        tor_process = subprocess.Popen(
            [TOR_PATH, "--SOCKSPort", "9050"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        STATUS["active"] = True
        STATUS["tor_status"] = "🧅 Red Tor Conectada"
        
        # Activamos el proxy del sistema para que Brave/Chrome/Edge vayan por Tor solos
        set_windows_proxy(enable=True)
        
    except Exception as e:
        STATUS["tor_status"] = f"Error: {e}"

# --- APÁGALO OUTRO ---
def disable_tor():
    global tor_process
    if tor_process:
        tor_process.terminate()
        tor_process = None
    
    # Dejar el internet de Windows normal
    set_windows_proxy(enable=False)
    
    STATUS["active"] = False
    STATUS["tor_status"] = "Desconectado"

# --- INTERFAZ PREMIUM DE CEBOLLAS ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XTOR 🧅 Onion Control Panel</title>
    <style>
        :root {
            --bg: #0b0b0e;
            --card-bg: #13131a;
            --primary: #9b5de5;
            --primary-hover: #8338ec;
            --success: #00f5d4;
            --error: #ff5400;
            --text: #f8f9fa;
        }
        body { 
            font-family: 'Segoe UI', system-ui, sans-serif; 
            background: var(--bg); 
            color: var(--text); 
            text-align: center; 
            padding: 0;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        .card { 
            background: var(--card-bg); 
            padding: 40px; 
            border-radius: 24px; 
            box-shadow: 0 20px 50px rgba(0,0,0,0.7), 0 0 40px rgba(155, 93, 229, 0.1); 
            max-width: 420px; 
            width: 90%; 
            border: 1px solid #23232f;
            position: relative;
            overflow: hidden;
        }
        /* Decoraciones de cebollas de fondo */
        .onion-bg {
            position: absolute;
            font-size: 8rem;
            opacity: 0.03;
            user-select: none;
            pointer-events: none;
        }
        .o-1 { top: -20px; left: -20px; transform: rotate(-20deg); }
        .o-2 { bottom: -20px; right: -20px; transform: rotate(20deg); }

        h1 { 
            color: var(--primary); 
            margin: 0; 
            font-size: 2.8rem; 
            font-weight: 900; 
            letter-spacing: 3px;
            text-shadow: 0 0 20px rgba(155, 93, 229, 0.4);
        }
        .subtitle { color: #6c757d; font-size: 0.9rem; letter-spacing: 1px; text-transform: uppercase; margin-top: 5px; margin-bottom: 25px; }
        
        /* El icono gigante de la cebolla del centro */
        .main-icon {
            font-size: 4.5rem;
            margin-bottom: 15px;
            display: inline-block;
            transition: transform 0.5s ease;
        }
        {% if status.active %}
        .main-icon {
            animation: pulse 2s infinite alternate;
        }
        @keyframes pulse {
            0% { transform: scale(1); filter: drop-shadow(0 0 5px var(--success)); }
            100% { transform: scale(1.1); filter: drop-shadow(0 0 25px var(--success)); }
        }
        {% endif %}

        .status { 
            font-size: 1.1rem; 
            margin: 25px 0; 
            padding: 14px; 
            border-radius: 12px; 
            font-weight: 700; 
            letter-spacing: 0.5px;
        }
        .active { background: rgba(0, 245, 212, 0.1); color: var(--success); border: 1px solid rgba(0, 245, 212, 0.3); }
        .inactive { background: rgba(255, 84, 0, 0.1); color: var(--error); border: 1px solid rgba(255, 84, 0, 0.3); }
        
        .btn { 
            display: block; 
            padding: 16px; 
            font-size: 1.1rem; 
            font-weight: 800; 
            border: none; 
            border-radius: 12px; 
            cursor: pointer; 
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
            text-decoration: none; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .btn-start { background: var(--primary); color: white; }
        .btn-start:hover { background: var(--primary-hover); transform: translateY(-2px); box-shadow: 0 8px 25px rgba(155, 93, 229, 0.4); }
        .btn-stop { background: #1c1c24; color: #ff5400; border: 1px solid var(--error); }
        .btn-stop:hover { background: var(--error); color: var(--bg); transform: translateY(-2px); box-shadow: 0 8px 25px rgba(255, 84, 0, 0.4); }
        
        .footer { margin-top: 30px; font-size: 0.8rem; color: #495057; font-weight: 600; }
    </style>
</head>
<body>
    <div class="card">
        <div class="onion-bg o-1">🧅</div>
        <div class="onion-bg o-2">🧅</div>

        <div class="main-icon">{% if status.active %}🧅{% else %}🧅💤{% endif %}</div>
        <h1>XTOR</h1>
        <div class="subtitle">Proxy Routing Engine</div>
        
        <div class="status {% if status.active %}active{% else %}inactive{% endif %}">
            {{ status.tor_status }}
        </div>

        {% if not status.active %}
            <a href="/start" class="btn btn-start">ENCENDER MOTOR🧅</a>
        {% else %}
            <a href="/stop" class="btn btn-stop">APAGAR CEBOLLA❌</a>
        {% endif %}
        
        <div class="footer">FUNCOMPUTER LABS • v2.0 Premium xd</div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, status=STATUS)

@app.route('/start')
def start_tunnel():
    enable_tor()
    return redirect(url_for('home'))

@app.route('/stop')
def stop_tunnel():
    disable_tor()
    return redirect(url_for('home'))

if __name__ == "__main__":
    # Nos aseguramos de limpiar el proxy de Windows si cerramos el script a lo bruto con Ctrl+C
    import atexit
    atexit.register(set_windows_proxy, enable=False)
    
    print("[+] Panel XTOR listo en http://127.0.0.1:1337")
    app.run(host='127.0.0.1', port=1337, debug=False)