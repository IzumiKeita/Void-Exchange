# Warframe Market Monitor - Backend

Este proyecto sigue una arquitectura modular para el backend desarrollado en Flask.

## Estructura del Proyecto

La lógica del backend se encuentra dentro de la carpeta `backend/` y se organiza de la siguiente manera:

- **`main.py`**: Punto de entrada de la aplicación. Se encarga únicamente de importar la factory de la app y ejecutar el servidor.
- **`backend/`**: Paquete principal del backend.
    - **`__init__.py`**: Contiene la función `create_app()` (Application Factory pattern) que inicializa la app Flask, configura extensiones (como CORS) y registra Blueprints.
    - **`controllers/`**: Manejadores de rutas (endpoints).
        - `monitor_controller.py`: Define las rutas relacionadas con el monitoreo de precios (`/api/monitor`). Utiliza `Blueprint` para agrupar rutas.
    - **`services/`**: Lógica de negocio y llamadas a APIs externas.
        - `market_service.py`: Contiene la lógica para consultar la API de Warframe Market y procesar los datos estadísticos.

## Cómo añadir nuevos módulos

1.  **Nueva Funcionalidad**:
    - Crea un nuevo servicio en `backend/services/` si necesitas lógica compleja o acceso a datos externos.
    - Crea un nuevo controlador en `backend/controllers/` usando un Blueprint.

2.  **Registrar el Blueprint**:
    - Importa el nuevo Blueprint en `backend/__init__.py`.
    - Regístralo en la función `create_app` usando `app.register_blueprint(nuevo_bp)`.

## Convenciones

- **Blueprints**: Usar para agrupar rutas relacionadas.
- **Servicios**: Funciones puras o clases que manejan la lógica de negocio, independientes del contexto HTTP de Flask siempre que sea posible.
- **Imports**: Usar imports absolutos desde la raíz del paquete (ej: `from backend.services.market_service import ...`).

## Dependencias Clave

- `flask`: Framework web.
- `flask-cors`: Manejo de Cross-Origin Resource Sharing.
- `requests`: Para realizar peticiones HTTP a la API de Warframe Market.
