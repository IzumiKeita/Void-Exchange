# Guía de Ejecución del Proyecto

Este documento explica cómo iniciar los servicios del backend (Python/Flask) y el frontend (Vue.js) para ejecutar la aplicación localmente.

## Requisitos Previos

Asegúrate de tener instalados:
1.  **Python 3.8+**
2.  **Node.js 18+** y **npm**

---

## 1. Iniciar el Backend (API)

El backend maneja la lógica de negocio, la conexión con la API de Warframe Market y la base de datos local.

1.  Abre una terminal en la carpeta raíz del proyecto (`f:\proyecto python\market waframe`).
2.  Activa el entorno virtual (si no lo has hecho):
    *   **Windows (PowerShell):**
        ```powershell
        .venv\Scripts\activate
        ```
    *   **Linux/Mac:**
        ```bash
        source .venv/bin/activate
        ```
3.  Instala las dependencias (si es la primera vez):
    ```bash
    pip install -r requirements.txt
    ```
4.  Ejecuta el servidor:
    ```bash
    python main.py
    ```
    *   El servidor se iniciará en `http://localhost:5000`.

---

## 2. Iniciar el Frontend (Web)

El frontend es la interfaz de usuario construida con Vue.js.

1.  Abre una **nueva** terminal (mantén la del backend corriendo).
2.  Navega a la carpeta `frontend`:
    ```bash
    cd frontend
    ```
3.  Instala las dependencias (si es la primera vez):
    ```bash
    npm install
    ```
4.  Inicia el servidor de desarrollo:
    ```bash
    npm run dev
    ```
    *   La aplicación estará disponible en `http://localhost:5173`.

---

## Resumen de Comandos

| Servicio | Carpeta | Comando | URL |
| :--- | :--- | :--- | :--- |
| **Backend** | Raíz (`/`) | `python main.py` | [http://localhost:5000](http://localhost:5000) |
| **Frontend** | `/frontend` | `npm run dev` | [http://localhost:5173](http://localhost:5173) |

> **Nota:** Ambos servicios deben estar ejecutándose simultáneamente en terminales separadas para que la aplicación funcione correctamente.
