# XTOR 🧅 — Windows Tor Routing Engine

Un panel de control web minimalista y con estética *Cyberpunk* desarrollado por **FUNCOMPUTER Labs**. Este proyecto funciona como un *wrapper* para el **Tor Expert Bundle** en Windows, permitiendo encender y apagar el motor de enrutamiento de Tor y configurar el proxy de todo el sistema automáticamente con un solo clic.

![Licencia](https://img.shields.io/badge/License-MIT-purple.svg)
![Entorno](https://img.shields.io/badge/Environment-Windows-blue.svg)
![Desarrollado por](https://img.shields.io/badge/Labs-FUNCOMPUTER-00f5d4.svg)

---

## 🚀 Características
* **Interfaz Web Gráfica:** Panel de control visual moderno (Flask) corriendo en el puerto `1337`.
* **Automatización de Procesos:** Inicia y detiene el binario oculto `tor.exe` en segundo plano sin interfaces molestas.
* **Proxy de Sistema Automático:** Modifica de forma segura el Registro de Windows (`winreg`) al activar el motor para que **Brave, Firefox, Chrome, Edge y el sistema entero** naveguen bajo la red Tor de inmediato, sin extensiones ni configuraciones manuales.
* **Cierre Seguro:** Restaura la configuración de red original de Windows automáticamente si el script se cierra de golpe o con `Ctrl + C`.

---

## 🛠️ Requisitos e Instalación

### 1. Clonar o guardar el script
Asegúrate de tener guardado el archivo principal del servidor como `xtor.py`.

### 2. Instalar dependencias de Python
Este proyecto utiliza el micro-framework **Flask**. Puedes instalarlo abriendo una consola de PowerShell y ejecutando:
```powershell
pip install flask
Después, para ejecutarlo ejecuta el xtor.py y ve a la dirección que te indica.
