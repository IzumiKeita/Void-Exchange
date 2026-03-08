# Registro de Cambios

## 2026-03-08
- **Control de Versiones**: **INICIALIZACIÓN GIT**. Se ha inicializado el repositorio Git y configurado el archivo `.gitignore` para excluir entornos virtuales, cachés y la distribución de Python portátil (`python_portable/`), asegurando un repositorio limpio y ligero.
- **Documentación**: **README ACTUALIZADO**. Se ha reestructurado el archivo `README.md` para priorizar el inglés como idioma principal, moviendo la sección en español a la parte inferior.
    - Se han añadido instrucciones claras para el uso de la versión **Portátil** y **Standalone**.
- **Distribución**: **SOPORTE PORTÁTIL (EMBEDDABLE)**. Se ha añadido un script `setup_portable.bat` que descarga y configura una versión mínima de Python (Embeddable Package) dentro del proyecto.
    - Permite ejecutar la aplicación en cualquier PC sin necesidad de instalación previa de Python.
    - Incluye un lanzador `start_portable.bat` para iniciar la aplicación usando este Python portátil.
- **Distribución**: **SOPORTE STANDALONE**. Se ha añadido la capacidad de generar un ejecutable único (`.exe`) que no requiere Python ni Node.js instalados.
    - Script `build_exe.bat` automatiza la compilación del frontend y el empaquetado con PyInstaller.
    - Modificaciones en `backend/__init__.py`, `void_trader_service.py` y `ducats_service.py` para soportar rutas relativas en modo congelado (`sys._MEIPASS`).
- **Rebranding**: **CAMBIO DE NOMBRE**. El proyecto ha sido renombrado a **Void Exchange** para reflejar mejor su naturaleza de terminal financiera y evitar conflictos con marcas existentes.
    - Actualizado `index.html`, `package.json` y `run.bat` con la nueva identidad.
    - Actualizados textos de interfaz en `es.js` y `en.js`.
- **Frontend (Global)**: **INTERNACIONALIZACIÓN (I18N)**. Se ha implementado un sistema completo de internacionalización para soportar Español e Inglés en toda la aplicación.
    - Implementación de sistema i18n reactivo (basado en Composition API) con gestión centralizada de traducciones en `src/i18n/locales/es.js` y `en.js`.
    - Selector de idioma persistente en la barra de navegación que guarda la preferencia del usuario.
    - Adaptación de todas las vistas principales (`Dashboard`, `VoidTrader`, `FullChat`, `ItemDetail`, `VaultWeapons`, `TradingAdvisor`, `ChatAssistant`) para usar claves de traducción dinámicas.
    - Soporte para reactividad inmediata al cambiar de idioma sin recargar la página.

## 2026-02-13
- **Base de Datos (PostgreSQL Support)**: **MIGRACIÓN A SQLALCHEMY**. Se ha reescrito la capa de acceso a datos para utilizar `SQLAlchemy` (ORM) en lugar de consultas SQL crudas con `sqlite3`.
    - Esto permite la compatibilidad dual: **SQLite** para desarrollo local y **PostgreSQL** para despliegue en la nube (Render, etc.) sin cambiar código.
    - Se crearon modelos ORM (`Item`, `PriceHistory`, `VoidTraderHistory`) en `backend/models.py`.
    - Se actualizó `database_service.py` para usar sesiones de SQLAlchemy.
    - Se configuró la detección automática de `DATABASE_URL` en `backend/__init__.py`.
- **Scripting (run.bat)**: **CORRECCIÓN DE INICIO**. Se corrigió un error crítico en `run.bat` que impedía su ejecución debido a finales de línea incorrectos (LF en lugar de CRLF). El script ahora utiliza saltos de línea compatibles con Windows (`\r\n`) y codificación UTF-8, asegurando que `cmd.exe` interprete correctamente los comandos y lance los servicios de Backend y Frontend sin cierres inesperados.

## 2026-02-08
- **Scripting (run.bat)**: **AUTOMATIZACIÓN DE INICIO MEJORADA**. Reemplazado script `run.ps1` por `run.bat` para mayor compatibilidad y facilidad de depuración.
    - El nuevo script utiliza `cmd /k` para mantener las ventanas abiertas en caso de error.
    - Verifica automáticamente la existencia del entorno virtual antes de iniciar.
    - Lanza Backend y Frontend en ventanas independientes tituladas.
- **Frontend (Dashboard.vue)**: **CORRECCIÓN ORDENAMIENTO POR PRECIO**. Solucionada una discrepancia en el ordenamiento de precios.
    - Se ajustó el helper `getPrice` para priorizar `avg_price` (precio promedio) sobre `price` para ítems no rankeados, ofreciendo un valor más representativo.
    - Se añadió robustez al manejo de formatos numéricos, asegurando la conversión correcta de strings con comas decimales (ej: "15,5") y garantizando siempre un valor numérico para el ordenamiento.
    - Se verificó la consistencia de datos entre el backend (`market_service.py`) y el frontend.

## 2026-02-03
- **Frontend (Dashboard.vue)**: **ORDENAMIENTO POR PRECIO**. Implementada funcionalidad de ordenamiento "Mayor a Menor Precio" en el Dashboard.
    - Se añadió un nuevo botón "💰 Mayor Precio" junto a los controles de tendencia.
    - El algoritmo utiliza el precio promedio (`avg_price`) para ítems estándar y el precio de rango máximo (`rank_max_stats.price`) para ítems con rango (Mods, Arcanos) para reflejar el valor más alto posible.
    - Se mejoró la lista de catálogo utilizando `<transition-group>` para proporcionar animaciones suaves al reordenar los elementos.

## 2025-12-28
- **Frontend (VoidTrader.vue & ChatAssistant.vue)**: **INTEGRACIÓN DE CONTEXTO VOID TRADER**. Se ha habilitado la capacidad de que la IA del asistente acceda al inventario actual (o historial) de Baro Ki'Teer cuando el usuario se encuentra en la vista `/void-trader`.
    - La IA ahora recibe la lista completa de ítems, precios en ducados/créditos y estadísticas de mercado (si están disponibles).
    - Esto permite realizar consultas como "¿Qué debería comprar hoy?" o "¿Cuál es el ítem más caro en ducados?".
- **Frontend (ItemDetail.vue)**: **MEJORA DE CONTEXTO IA**. Se ha actualizado la lógica de `updateChatContext` para enviar a la IA (Gemini) tanto las estadísticas del rango seleccionado actualmente como las estadísticas de referencia del **Rango 0** y **Rango Máximo** simultáneamente.
    - Esto permite que el asistente responda preguntas sobre precios "maxeados" incluso si el usuario está visualizando el gráfico de rango 0, y viceversa.
    - Se añadió un watcher para actualizar este contexto dinámicamente al cambiar de rango en la interfaz.

## 2025-12-27
- **Backend (market_service.py)**: **SOPORTE DE HISTORIAL POR RANGO**. Se ha implementado la función `get_item_history` y actualizado `get_full_item_details` para recuperar el historial completo de estadísticas (90 días y 48 horas) desglosado por rangos (para Mods) y refinamientos (para Reliquias). Esto soluciona la falta de datos en los gráficos de precios.
- **Frontend (ItemDetail.vue)**: **VISUALIZACIÓN DE RANGO MÁXIMO**. Se ha añadido lógica para etiquetar explícitamente el botón del rango máximo (ej. "Max (R10)") en los filtros del gráfico, facilitando al usuario la identificación de la opción de rango completo solicitada.
- **Backend (void_trader_service.py)**: **CORRECCIÓN FINAL DE NOMBRES**. Se ha implementado un sistema de saneamiento "a prueba de fallos" para los nombres de Baro Ki'Teer.
    1.  **Soporte Case-Insensitive y Spaceless**: Ahora el sistema reconoce los nombres aunque tengan mayúsculas/minúsculas diferentes o les falten espacios (ej. "ArchwingRifleDamageAmountModExpert" ahora se corrige correctamente a "Cañón revestido de rubedo Prime").
    2.  **Lista Negra Reforzada**: Añadidos términos como "scarf" (bufanda) y validación estricta para cosméticos Prisma/Vándalo (ej. "Prisma Razor Scarf" ahora se oculta correctamente).
    3.  **Diccionario Ampliado**: Incluidas variantes sin espacios de todos los Mods internos para garantizar que se traduzcan.
- **Backend (void_trader_service.py)**: **CORRECCIÓN DE PERSISTENCIA**. Se ha modificado `get_baro_history` y la carga de caché para aplicar el saneamiento, filtrado y categorización **en tiempo de lectura**. Esto asegura que los datos antiguos almacenados en la base de datos se muestren corregidos sin necesidad de borrarlos o volver a descargarlos.
- **Backend (void_trader_service.py)**: **DEDUPLICACIÓN Y RE-CATEGORIZACIÓN**.
    1.  **Deduplicación**: Agregado control `seen_names` en `get_baro_history` para evitar que variantes del mismo ítem (ej. "Grakata Prisma" vs "Prisma Grakata") aparezcan dos veces tras ser traducidas al mismo nombre.
    2.  **Categorización de Mods**: Mejorada la lógica en `_determine_category` para identificar correctamente los Mods Prime en español (ej. "Flujo Prime") usando una lista de palabras clave, solucionando que desaparecieran de la categoría "Mods".
- **Backend (void_trader_service.py)**: **CAMBIO A SISTEMA JSON**. Implementada la lógica sugerida por el usuario para manejar el historial.
    1.  **Fuente de Verdad**: Se crea `void_trader_history.json`. Cada vez que se procesa el "Inventario Actual" (que ya está limpio y traducido), se guarda una copia exacta en este JSON, sobrescribiendo cualquier versión anterior para esa fecha.
    2.  **Migración Automática**: Si el JSON no existe, el sistema lee la base de datos antigua, la limpia, la deduplica y genera el archivo JSON inicial automáticamente.
    3.  **Resultado**: Esto elimina permanentemente los problemas de items duplicados o nombres sucios en el historial, ya que el JSON actúa como un "snapshot" limpio de cada visita.
- **Backend (void_trader_service.py)**: **HISTORIAL COMPLETO**.
    1.  **Lógica Ajustada**: Se eliminó el filtrado excesivo en `fetch_void_trader_data` que impedía guardar ciertos ítems tradeables en el historial. Ahora se respeta estrictamente la bandera `is_tradeable` y la blacklist, asegurando que el JSON guarde *exactamente* lo que se muestra en el "Inventario Actual".
    2.  **Consistencia**: Se garantiza que si un ítem aparece en la tarjeta del Baro hoy, aparecerá idéntico en el historial mañana.
- **Backend (void_trader_service.py)**: **EXPANSIÓN CRÍTICA DE NOMBRES**. Ampliado masivamente el diccionario `FIXED_ITEM_NAMES` y creada una lista `COMMON_TERMS` para la traducción palabra por palabra. Ahora se cubren nombres complejos como "Prisma Dual Cleavers" -> "Cuchillas dobles Prisma", "Primed Heated Charge" -> "Carga incendiaria Prime", y se maneja automáticamente el reordenamiento de "Relic" (ej. "Axi A2 Relic" -> "Reliquia Axi A2").
  - **Frontend (VoidTrader.vue)**: **CORRECCIÓN DE VISIBILIDAD**. Se detectó que el filtro de seguridad `getVisibleHistoryItems` estaba ocultando ítems válidos (como Mods Prime en español) por ser demasiado restrictivo y no confiar en la flag `tradeable` del JSON. Se ha modificado para que **siempre** muestre los ítems marcados como `tradeable: true` en el backend, garantizando que el historial web coincida exactamente con el archivo JSON.
  - **Frontend (VoidTrader.vue)**: **NAVEGACIÓN INTEGRADA**. Se ha añadido interactividad a las tarjetas del inventario actual y a las filas del historial. Ahora, al hacer clic en cualquier ítem, la aplicación redirige a la vista de detalles `/item/{url_name}`, permitiendo consultar rápidamente las estadísticas de mercado completas.
  - **Frontend (VoidTrader.vue)**: **CORRECCIÓN DE DATOS DE MERCADO**. Solucionado el problema de visualización "N/A pl" en Mods y Reliquias. Se ha implementado una función `getPriceStats` que normaliza la extracción de precios desde estructuras anidadas (`rank_0` para Mods, `intact` para Reliquias) que anteriormente no eran leídas correctamente por la interfaz plana.
  - **Frontend (ItemDetail.vue)**: **CORRECCIÓN DE GRÁFICOS DE RANGO**. Modificada la lógica de selección de datos históricos para priorizar **Rango 0** (Unranked) en lugar del Rango Máximo. Esto corrige la discrepancia donde el resumen mostraba precios de mods sin rango (ej: 23pl) pero la gráfica mostraba precios de mods maxeados (ej: 200pl).
  - **Frontend (VoidTrader.vue)**: **CORRECCIÓN DE EMERGENCIA**. Solucionado el bloqueo de "Cargando historial..." restaurando las variables faltantes `processedHistory`, `warning` y `toggleVisit` que se habían perdido durante la refactorización anterior. Ahora el historial se renderiza correctamente y es interactivo.
- **Frontend (VoidTrader.vue)**: **CORRECCIÓN CRÍTICA** en el filtrado de historial. Se ha reemplazado el filtrado en tiempo de renderizado por una propiedad computada `processedHistory` que pre-procesa todo el historial al cargarlo. Esto soluciona el problema de conteo de ítems (ahora muestra "X ítems tradeables" en lugar del total bruto) y asegura que los ítems basura (cosméticos) sean eliminados antes de que la interfaz los vea.
- **Backend (void_trader_service.py)**: **CORRECCIÓN CRÍTICA** en la recolección de datos. Se ha insertado la llamada a `_is_blacklisted` dentro del bucle de procesamiento de `fetch_void_trader_data`. Anteriormente, la función de blacklist existía pero no se invocaba, permitiendo que cosméticos "con nombre parecido" o erróneos entraran a la base de datos.
- **Backend (void_trader_service.py)**: **MEJORA DE NOMBRES**. Implementada la función `_sanitize_item_name` y un diccionario `FIXED_ITEM_NAMES` para traducir automáticamente nombres internos o en inglés (ej. "Archwing Rifle Damage Amount Mod Expert" -> "Cañón revestido de rubedo Prime", "Supra Vandal" -> "Supra Vándalo"). Esta corrección se aplica tanto a nuevos datos como al historial existente al momento de consultarlo.
- **Frontend/Backend**: Expandida la lista negra de exclusión para incluir términos como "song", "canción", "blueprint" (sueltos), "earpiece", etc., y añadida normalización de acentos (NFD) para evitar que "Canción" se escape del filtro "canción".
- **Frontend (VoidTrader.vue)**: Unificada la lógica de filtrado de inventario. Ahora, los botones de categoría (Todos, Mods, Armas, Reliquias, Otros) controlan tanto el inventario actual como la lista de "Historial Completo". Si seleccionas "Mods", el historial también filtrará y mostrará solo los mods de visitas anteriores.
- **Frontend (VoidTrader.vue)**: Refactorizado el código de filtrado creando una función reutilizable `itemMatchesCategory`. Esto garantiza que las reglas de categorización sean consistentes en toda la vista de Baro Ki'Teer.
- **Backend (void_trader_service.py)**: Implementado filtro estricto por lista negra (`_is_blacklisted`) para excluir explícitamente cosméticos (glifos, diseños, armaduras, decoraciones, etc.) del procesamiento de inventario. Esto refuerza la regla de "solo tradeable" incluso si el sistema encuentra coincidencias parciales en Warframe Market.
- **Frontend (VoidTrader.vue)**: Agregado filtro visual `getVisibleHistoryItems` en la sección de historial. Esto limpia retroactivamente los datos antiguos guardados en la base de datos, ocultando cualquier ítem cosmético o no tradeable que se hubiera registrado anteriormente, asegurando que el usuario solo vea Mods, Armas y Reliquias.
- **Backend (void_trader_service.py)**: Implementada lógica de respaldo y modo offline para Baro Ki'Teer. Ahora el inventario se guarda automáticamente en un archivo JSON local (`void_trader_last_inventory.json`). Si la API de Warframe falla, el sistema carga este respaldo, verificando la fecha de expiración para simular el estado "Activo" si corresponde, o mostrando los datos como referencia histórica.
- **Frontend (VoidTrader.vue)**: Añadido soporte visual para el modo offline/caché, mostrando una alerta advertencia cuando los datos provienen del respaldo local.
- **Frontend (VoidTrader.vue)**: Implementada sección de "Historial Completo" con tarjetas desplegables que permiten consultar los inventarios de visitas anteriores sin necesidad de búsquedas externas.
- **Frontend (VoidTrader.vue)**: Mejorada la persistencia de visualización: cuando Baro se marcha (inactivo), la interfaz carga automáticamente el inventario de su última visita conocida desde la base de datos, cumpliendo con el requisito de mantener los ítems visibles hasta la próxima llegada.
- **Backend (void_trader_service.py)**: Corregida la lógica de procesamiento de inventario para solucionar la falta de visualización de ítems tradeables (Mods, Armas, Reliquias). Se ha implementado una normalización de referencias de juego (`game_ref`) para eliminar el segmento `/StoreItems` (usado por la API oficial) y los sufijos de calidad de reliquias (Bronze, Silver, etc.) que no coinciden con Warframe Market. Esto asegura que ítems como "Vastilok", "Primed Mods" y "Reliquias Axi" sean reconocidos correctamente.
- **Backend (void_trader_service.py)**: Aplicado filtro estricto en el inventario de Baro Ki'Teer para descartar automáticamente cualquier ítem que no sea comerciable (cosméticos, diseños, etc.), mostrando únicamente Mods, Armas y Reliquias con correspondencia en Warframe Market.
- **Frontend (VoidTrader.vue)**: Eliminada la categoría "Cosméticos" del filtro visual, ya que estos ítems han sido removidos del procesamiento de datos.
- **Backend (void_trader_service.py)**: Implementada carga dinámica de traducciones desde `backend/data/translations.json`. Esto permite editar y ampliar el diccionario de traducción de Baro Ki'Teer sin modificar el código fuente.
- **Backend (void_trader_service.py)**: Ampliado significativamente el diccionario de traducción manual (`COMMON_TRANSLATIONS`) para cubrir una amplia gama de cosméticos y objetos de Baro Ki'Teer, mejorando la localización al español.
- **Frontend (VoidTrader.vue)**: Agregada funcionalidad de búsqueda en el historial de visitas para filtrar por nombre de ítem, facilitando el análisis de precios históricos.
- **Frontend (VoidTrader.vue)**: Añadido botón de actualización manual "Refrescar" en la sección de inventario actual.
- **Backend (void_trader_service.py)**: Optimizada la lógica de traducción manual para manejar frases de múltiples palabras (ej. "Bobble Head") antes de procesar palabras individuales.
- **Backend (void_trader_service.py)**: Cambiado el proveedor de datos del Comerciante del Vacío a la API oficial (`content.warframe.com/dynamic/worldState.php`) debido a errores persistentes (502 Bad Gateway) en `api.warframestat.us`. Implementada lógica de parseo de fechas y estructura específica de la API oficial.
- **Backend (void_trader_service.py)**: Mejorada la lógica de detección de ítems tradeables mediante limpieza de nombres internos (eliminación de sufijos "Blueprint", "Receiver", etc.) y soporte para variaciones de nombres.
- **Backend (market_service.py)**: Optimizado el mapeo de ítems agregando un caché de búsqueda por referencia interna del juego (`game_ref`), lo que mejora la precisión al identificar objetos del inventario de Baro.
- **Backend (void_trader_service.py)**: Implementada lógica completa para el Comerciante del Vacío (Baro Ki'Teer). Se ha creado un nuevo servicio que consulta la API externa `https://api.warframestat.us/pc/voidTrader` para obtener el estado actual, ubicación y cronómetro de llegada/salida.
- **Backend (void_trader_service.py)**: Agregado sistema de procesamiento de inventario que mapea los nombres de ítems (en inglés) a los slugs de Warframe Market usando el campo `item_name_en`. Esto permite integrar datos de precios y tendencias de mercado directamente en la vista del inventario de Baro.
- **Backend (database_service.py)**: Extendida la base de datos con la tabla `void_trader_history` para persistir el historial de visitas de Baro, almacenando fecha, ítems, costos (ducados/créditos) y slugs asociados.
- **Backend (void_trader_controller.py)**: Expuestos nuevos endpoints `/api/void-trader/current` y `/api/void-trader/history` para consumo del frontend.
- **Frontend (VoidTrader.vue)**: Creada nueva vista dedicada para el Comerciante del Vacío. Muestra estado en tiempo real (Activo/Ausente), temporizador dinámico, inventario con precios en Ducados/Créditos y datos de mercado integrados (mínimo, promedio) para ítems tradeables. Incluye sección de historial de visitas anteriores.
- **Frontend (Dashboard.vue)**: Agregado acceso directo "💠 Void Trader" en la barra de navegación principal.

## 2025-12-25
- **Backend (trends_service.py)**: Corregida la lógica de cálculo de tendencias. Se ha migrado de usar estadísticas cerradas (`statistics_closed`) a estadísticas en vivo (`statistics_live`) para poder distinguir correctamente entre volumen de oferta (Sell Orders) y demanda (Buy Orders), ya que los datos históricos agregados no incluían el tipo de orden. Esto soluciona el problema de que la lista de tendencias apareciera vacía.
- **Backend (trends_service.py)**: Optimizado el servicio de actualización de tendencias para solucionar el problema de "pocos elementos". Se ha cambiado a un procesamiento secuencial (`max_workers=1`) con control estricto de tasa de peticiones (sleep 0.35s) y lógica de reintento para errores 429 (Rate Limit). Esto asegura que se recuperen todos los datos sin ser bloqueados por la API de Warframe Market. Además, se implementó un guardado incremental cada 50 ítems para mostrar progreso visual al usuario.
- **Frontend (ItemDetail.vue)**: Implementado campo "Valor en Ducados" condicional. Se muestra solo cuando el ítem tiene un valor de ducados asociado (ej. partes Prime) y se oculta para otros tipos (Mods, Arcanos). Incluye validación de datos desde el backend y estilo visual específico (texto dorado).
- **Backend (market_service.py)**: Reforzada la extracción de valores de ducados desde las APIs v1 y v2 de Warframe Market, asegurando que el campo solo se incluya en la respuesta cuando sea aplicable.
- **Documentación**: Creado archivo `trend_arrows_explanation.md` detallando la lógica matemática (`((precio_actual - anterior) / anterior) * 100`) y visual de las flechas de tendencia (Verde/Positivo, Rojo/Negativo) para referencia del usuario.
- **Frontend (Dashboard.vue)**: Implementado sistema de captura de contexto "Dashboard" que guarda en `sessionStorage` un resumen de los 5 principales ítems visibles (con precios y tendencias) para que el Asistente IA pueda "ver" lo que el usuario ve en la pantalla principal.
- **Frontend (Dashboard.vue)**: Implementada persistencia del estado de navegación. Ahora el Dashboard recuerda la pestaña activa, los filtros, la página actual y la búsqueda al navegar hacia otros detalles y volver, utilizando `sessionStorage`. Esto soluciona el problema de que la aplicación siempre regresaba a la pestaña "Recientes".
- **Frontend (Dashboard.vue)**: Solucionado un error crítico donde la aplicación se quedaba "pegada" en estado de carga al regresar al Dashboard si la última pestaña visitada no era "Recientes". Se ha corregido la lógica de inicialización en `onMounted` para asegurar que el indicador de carga se desactive correctamente después de recuperar el catálogo completo.
- **Frontend (ChatAssistant.vue)**: Actualizada la lógica de inyección de contexto para leer y enviar los datos del Dashboard al backend cuando el usuario no está en la vista de detalle de un ítem, permitiendo consultas generales como "¿qué compro de lo que veo?".
- **Backend (ai_service.py)**: Modificado el prompt del sistema en `chat_trading` para reconocer y procesar contextos de tipo "dashboard", instruyendo a la IA para sugerir oportunidades basadas en los ítems destacados visibles.
