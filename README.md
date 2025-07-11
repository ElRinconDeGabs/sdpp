# 📘 Sistema de Seguimiento Digital de Prácticas Profesionales (SDPP)

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-black?logo=flask)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?logo=mysql)](https://www.mysql.com/)
[![HTML](https://img.shields.io/badge/HTML-5-orange?logo=html5)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS](https://img.shields.io/badge/CSS-3-blue?logo=css3)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![License](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)

Este proyecto corresponde a una tesina teórico-práctica para la Universidad Tecnológica de Panamá. El sistema permite a las instituciones de educación superior dar seguimiento digital a las prácticas profesionales de sus estudiantes, facilitando la interacción entre estudiantes, tutores académicos y tutores empresariales.

---

## 🛠️ Tecnologías utilizadas

- **Backend:** Python con Flask
- **Base de datos:** MySQL con procedimientos almacenados
- **Frontend:** HTML, CSS y JavaScript (separado del backend)
- **Gestión de dependencias:** `pip`, `requirements.txt`
- **Control de versiones:** Git + GitHub

---
---

## 🚀 Instalación y ejecución local

Sigue estos pasos para ejecutar el proyecto localmente en cualquier sistema operativo:

### 1. Clona el repositorio


```
bash
# 1. Clonar el repositorio
git clone https://github.com/ElRinconDeGabs/sdpp.git
cd sdpp

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual (PowerShell)
.\venv\Scripts\Activate.ps1

# ⚠️ Si ves un error sobre ejecución de scripts:
# Ejecuta esto una sola vez para permitirlo:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

venv\Scripts\activate.bat "En Windows CMD"
source venv/bin/activate  "En macOS / Linux"

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar la aplicación
python run.py
```

🧑‍💻 Autores
- Isaac Samaniego
- Ambar Hernández

Proyecto desarrollado para el curso Tópicos Especiales

📍 Universidad Tecnológica de Panamá – 2025
