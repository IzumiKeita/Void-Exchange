import requests
import time
import json
import os
from backend.services.market_service import get_all_items

# Configuración de persistencia
import sys

if getattr(sys, 'frozen', False):
    # En modo ejecutable, guardar caché junto al .exe
    DATA_DIR = os.path.dirname(sys.executable)
else:
    # En desarrollo, guardar en backend/data
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

DUCATS_FILE = os.path.join(DATA_DIR, 'ducats_cache.json')

# Cache para datos de ducados
DUCATS_CACHE = {
    'data': [],
    'last_update': 0
}
CACHE_DURATION = 3600 # 1 hora

def load_cache_from_disk():
    """Carga el caché desde el archivo JSON si existe."""
    global DUCATS_CACHE
    if os.path.exists(DUCATS_FILE):
        try:
            with open(DUCATS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Validar estructura básica
                if 'data' in data and 'last_update' in data:
                    DUCATS_CACHE = data
                    print(f"Caché de Ducados cargado desde disco ({len(DUCATS_CACHE['data'])} items)")
        except Exception as e:
            print(f"Error cargando caché de ducados: {e}")

def save_cache_to_disk():
    """Guarda el caché actual en archivo JSON."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(DUCATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(DUCATS_CACHE, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error guardando caché de ducados: {e}")

# Intentar cargar al iniciar el módulo
load_cache_from_disk()

def get_ducats_data():
    """
    Obtiene la lista de items con mejor relación Ducados/Platino.
    """
    global DUCATS_CACHE
    
    current_time = time.time()
    
    # Verificar si el caché en memoria (o cargado de disco) es válido
    if DUCATS_CACHE['data'] and (current_time - DUCATS_CACHE['last_update'] < CACHE_DURATION):
        return DUCATS_CACHE['data']
        
    url = "https://api.warframe.market/v1/tools/ducats"
    headers = {
        'Language': 'es',
        'Platform': 'pc',
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Payload contiene "previous_hour" (lista)
        raw_items = data.get('payload', {}).get('previous_hour', [])
        
        # Necesitamos cruzar el ID del item con nuestro diccionario de items para obtener nombres e imágenes
        # La API de ducats devuelve "item": "id_del_item"
        
        # Asegurar que tenemos el diccionario de items cargado
        all_items_list = get_all_items()
        # Crear mapa ID -> Data
        items_by_id = {item['id']: item for item in all_items_list}
        
        processed_items = []
        
        for entry in raw_items:
            item_id = entry.get('item')
            item_info = items_by_id.get(item_id)
            
            if item_info:
                # Calcular ratio si no viene (aunque viene como ducats_per_platinum_wa)
                ducats = entry.get('ducats', 0)
                plat_price = entry.get('wa_price', 0) # Precio promedio ponderado
                
                # Enriquecer datos
                processed_entry = {
                    'id': item_id,
                    'item_name': item_info['item_name'],
                    'url_name': item_info['url_name'],
                    'thumb': item_info.get('thumb'),
                    'ducats': ducats,
                    'plat_price': plat_price,
                    'volume': entry.get('volume', 0),
                    'ducats_per_plat': entry.get('ducats_per_platinum_wa', 0),
                    'position_change_day': entry.get('position_change_day', 0)
                }
                
                # No descargar imágenes síncronamente aquí para no bloquear la respuesta
                # El frontend solicitará la imagen y el controlador items_controller la descargará bajo demanda
                processed_entry['image'] = processed_entry['thumb']
                
                processed_items.append(processed_entry)
        
        # Ordenar por mejor ratio (más ducados por platino) descendente
        processed_items.sort(key=lambda x: x['ducats_per_plat'], reverse=True)
        
        # Actualizar caché y guardar en disco
        DUCATS_CACHE['data'] = processed_items
        DUCATS_CACHE['last_update'] = current_time
        save_cache_to_disk()
        
        return processed_items
        
    except Exception as e:
        print(f"Error fetching ducats data: {e}")
        # Si falla la API pero tenemos datos antiguos en caché (incluso expirados), mejor devolver eso que nada
        if DUCATS_CACHE['data']:
            print("Retornando datos en caché expirados debido a error en API.")
            return DUCATS_CACHE['data']
        return []
