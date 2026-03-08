# 🌌 Void Exchange

**[Español abajo]**

Complete web application to monitor prices, trends, and the Void Trader inventory in Warframe Market. Includes a robust Python (Flask) backend and a modern Vue 3 frontend.

## 🚀 Features

- **Price Dashboard**: Real-time visualization of prices, volumes, and trends.
- **Void Trader (Baro Ki'Teer)**: Current inventory with price analysis and AI-based buying recommendations.
- **Predictions**: Algorithms to detect investment opportunities (Ducats/Platinum).
- **Hybrid Database**:
  - **SQLite** for local development (zero configuration).
  - **PostgreSQL** for production/cloud.
- **Multilanguage (i18n)**: Full support for English (EN) and Spanish (ES).

## 📦 Distribution Options (No Installation Required)

You have two options to run the application on computers without Python installed:

### Option A: Single Executable (.exe) - Recommended
Generates a single file containing everything needed.
1. Run `build_exe.bat`.
2. Copy the `dist/VoidExchange.exe` file to the other PC.

### Option B: Portable Python (Embeddable)
Downloads a minimal version of Python inside the project folder. Useful if you want to edit the Python code on the other PC without installing anything.
1. Run `setup_portable.bat`.
2. This will create a `python_portable` folder and a `start_portable.bat` file.
3. Copy the **entire project folder** to the other PC.
4. Run `start_portable.bat` on the other PC.

**Note**: If you use AI features (Gemini), make sure to copy your `.env` file alongside the executable or in the project root.

## 🛠️ Installation and Usage (Development)

1.  **Clone the repository**:
    ```bash
<<<<<<< HEAD
    git clone <your-repo-url>
=======
    git clone <your-repo>
>>>>>>> 30bc0ba75a9925b10588866195f3e0c7f440cc3e
    cd Void-Exchange
    ```

2.  **Run the Application (Windows)**:
    - Simply run the automatic script:
      ```cmd
      run.bat
      ```
    - This script will install dependencies (Python/Node), configure the database, and launch both servers (Backend and Frontend).

3.  **Access**:
    - Frontend: `http://localhost:5173`
    - Backend API: `http://localhost:5000`

## ☁️ Git & Version Control

This project comes with a pre-configured local Git repository.
- **.gitignore**: Optimized to exclude virtual environments, build artifacts, and sensitive files.
- **Branch**: `master` (default).

To push to GitHub:
```bash
git remote add origin https://github.com/YOUR_USERNAME/Void-Exchange.git
git branch -M main
git push -u origin main
```

---

# 🌌 Void Exchange (Español)

Aplicación web completa para monitorear precios, tendencias y el inventario del Void Trader en Warframe Market. Incluye un backend robusto en Python (Flask) y un frontend moderno en Vue 3.

## 🚀 Características

- **Dashboard de Precios**: Visualización en tiempo real de precios, volúmenes y tendencias.
- **Void Trader (Baro Ki'Teer)**: Inventario actual con análisis de precios y recomendaciones de compra mediante IA.
- **Predicciones**: Algoritmos para detectar oportunidades de inversión (Ducados/Platino).
- **Base de Datos Híbrida**: 
  - **SQLite** para desarrollo local (sin configuración).
  - **PostgreSQL** para producción/nube.
- **Multilenguaje (i18n)**: Soporte completo para Inglés (EN) y Español (ES).

## 📦 Opciones de Distribución sin Instalación

Tienes dos opciones para ejecutar la aplicación en computadoras que no tienen Python instalado:

### Opción A: Ejecutable Único (.exe) - Recomendada
Genera un solo archivo que contiene todo lo necesario.
1. Ejecuta `build_exe.bat`.
2. Copia el archivo `dist/VoidExchange.exe` a la otra PC.

### Opción B: Python Portátil (Embeddable)
Descarga una versión mínima de Python dentro de la carpeta del proyecto. Útil si quieres poder editar el código Python en la otra PC sin instalar nada.
1. Ejecuta `setup_portable.bat`.
2. Esto creará una carpeta `python_portable` y un archivo `start_portable.bat`.
3. Copia **toda la carpeta del proyecto** a la otra PC.
4. Ejecuta `start_portable.bat` en la otra PC.

**Nota**: Si usas funcionalidades de IA (Gemini), asegúrate de copiar tu archivo `.env` junto al ejecutable o en la raíz del proyecto.

## 🛠️ Instalación y Uso (Desarrollo)

1.  **Clonar el repositorio**:
.    ```bash
    git clone <tu-url-del-repo>
    cd Void-Exchange
    ```

2.  **Configurar Variables de Entorno**:
    - Copia el archivo de ejemplo:
      ```bash
      cp .env.example .env
      ```
    - Edita `.env` con tus claves API (si usas Gemini, etc.).

3.  **Ejecutar la Aplicación**:
    ```cmd
    run.bat
    ```

## ☁️ Git y Control de Versiones

Este proyecto incluye un repositorio Git local preconfigurado.
- **.gitignore**: Optimizado para excluir entornos virtuales (`.venv`), artefactos de compilación y archivos sensibles.
- **Rama**: `master` (por defecto).

Para subir a GitHub:
```bash
git remote add origin https://github.com/TU_USUARIO/Void-Exchange.git
git branch -M main
git push -u origin main
```
    - (Opcional) Si deseas usar PostgreSQL local, edita `.env` y descomenta la línea `DATABASE_URL`. Por defecto usará SQLite.

3.  **Ejecutar la Aplicación (Windows)**:
    - Simplemente ejecuta el script automático:
      ```cmd
      run.bat
      ```
    - Este script instalará dependencias (Python/Node), configurará la base de datos y lanzará ambos servidores (Backend y Frontend).

4.  **Acceder**:
    - Frontend: `http://localhost:5173`
    - Backend API: `http://localhost:5000`

## 🌍 Internacionalización (i18n)

El proyecto soporta múltiples idiomas (actualmente EN y ES) mediante un sistema personalizado en Vue 3.

### Agregar un Nuevo Idioma

1.  **Crear archivo de traducción**:
    - Duplica `frontend/src/i18n/locales/en.js` y renómbralo (ej. `fr.js`).
    - Traduce los valores del objeto manteniendo las mismas claves.

2.  **Registrar el idioma**:
    - Edita `frontend/src/i18n/index.js`.
    - Importa el nuevo archivo: `import fr from './locales/fr';`
    - Agrégalo al objeto `messages`:
      ```javascript
      const messages = {
          en,
          es,
          fr // Nuevo idioma
      };
      ```

3.  **Actualizar el Selector**:
    - Edita `frontend/src/components/LanguageSelector.vue`.
    - Agrega la opción al template:
      ```html
      <span class="divider">|</span>
      <span @click="setLocale('fr')" :class="{ active: locale === 'fr' }" class="lang-option">FR</span>
      ```

## ☁️ Despliegue en Render

Este proyecto está configurado para desplegarse fácilmente en [Render.com](https://render.com).

1.  Crea un nuevo **Web Service** conectado a tu repositorio.
2.  Render detectará automáticamente la configuración en `render.yaml`.
3.  Agrega una base de datos PostgreSQL en Render y vinculala (la variable `DATABASE_URL` se configurará sola).

## 📂 Estructura del Proyecto

- `backend/`: API Flask, modelos de base de datos y lógica de negocio.
- `frontend/`: Interfaz de usuario Vue 3 + Vite.
- `data/`: Almacenamiento local (SQLite).
- `.Documentacion/`: Documentación detallada del desarrollo.

## 🤝 Contribución

1.  Haz un Fork.
2.  Crea tu rama (`git checkout -b feature/nueva-funcionalidad`).
3.  Commit (`git commit -m 'Agrega nueva funcionalidad'`).
4.  Push (`git push origin feature/nueva-funcionalidad`).
5.  Abre un Pull Request.
