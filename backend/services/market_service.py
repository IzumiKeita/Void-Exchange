import os
import requests
import time
import concurrent.futures
from threading import Lock
from flask import send_from_directory
from backend.services.database_service import save_price_history


# Caché simple en memoria para la lista de items
ITEMS_CACHE = []
ITEMS_DICT = {} # Diccionario para búsqueda rápida por slug
ITEMS_BY_GAME_REF = {} # Diccionario para búsqueda por gameRef (path interno del juego)

# Caché para datos de mercado (estadísticas)
# Formato: { "item_name|rank": (timestamp, data) }
MARKET_DATA_CACHE = {}
CACHE_DURATION = 300 # 5 minutos en segundos

# Rate Limiter Global
_request_lock = Lock()
_last_request_time = 0
MIN_REQUEST_INTERVAL = 0.5  # 2 peticiones por segundo máx para estar seguros

def _make_request(url, headers=None, stream=False):
    """
    Wrapper para requests.get que respeta el rate limit y maneja reintentos 429.
    """
    global _last_request_time
    
    # Control de tasa básico
    with _request_lock:
        current_time = time.time()
        time_since_last = current_time - _last_request_time
        if time_since_last < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - time_since_last)
        _last_request_time = time.time()
    
    # Reintento con backoff para 429
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, stream=stream)
            
            if response.status_code == 429:
                # Si recibimos 429, esperar y reintentar
                wait_time = int(response.headers.get('Retry-After', 2)) + 1 + (attempt * 2)
                print(f"Rate limit hit (429) for {url}. Waiting {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
                continue
                
            return response
            
        except requests.RequestException as e:
            print(f"Request error for {url}: {e}")
            if attempt == max_retries - 1:
                raise e
            time.sleep(1)
            
    return response

def get_all_items():
    global ITEMS_CACHE, ITEMS_DICT, ITEMS_BY_GAME_REF
    if ITEMS_CACHE:
        return ITEMS_CACHE
        
    url = "https://api.warframe.market/v2/items"
    headers = {
        'Language': 'es',
        'Platform': 'pc',
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        response = _make_request(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Parseamos la respuesta de la API v2
        raw_items = data.get('data', [])
        ITEMS_CACHE = []
        ITEMS_DICT = {}
        ITEMS_BY_GAME_REF = {}
        
        for item in raw_items:
            # Intentamos obtener el nombre en español, si no, en inglés
            i18n = item.get('i18n', {})
            name_es = i18n.get('es', {}).get('name')
            name_en = i18n.get('en', {}).get('name')
            name = name_es or name_en
            slug = item.get('slug')
            game_ref = item.get('gameRef') # Path interno (ej: /Lotus/StoreItems/...)
            
            if name and slug:
                # Extraer thumb e icon desde i18n
                thumb = i18n.get('es', {}).get('thumb') or i18n.get('en', {}).get('thumb') or ''
                
                item_data = {
                    'item_name': name,
                    'item_name_en': name_en, # Guardamos nombre en inglés para mapeo con otras APIs
                    'url_name': slug,
                    'id': item.get('id'),
                    'thumb': thumb,
                    'tags': item.get('tags', []),
                    'max_rank': item.get('maxRank', None),
                    'game_ref': game_ref
                }
                ITEMS_CACHE.append(item_data)
                ITEMS_DICT[slug] = item_data
                if game_ref:
                    ITEMS_BY_GAME_REF[game_ref] = item_data
                
        return ITEMS_CACHE
    except Exception as e:
        print(f"Error fetching items list: {e}")
        return []

def get_item_by_game_ref(game_ref):
    """Busca un item por su referencia interna del juego"""
    global ITEMS_BY_GAME_REF
    if not ITEMS_BY_GAME_REF:
        get_all_items()
    return ITEMS_BY_GAME_REF.get(game_ref)


def get_item_metadata(slug):
    """Obtiene los metadatos de un item (imagen, tags, nombre) usando el caché"""
    global ITEMS_DICT
    if not ITEMS_DICT:
        get_all_items() # Aseguramos que el caché esté cargado
    return ITEMS_DICT.get(slug, {})

def get_image_path(filename):
    """Devuelve la ruta absoluta de almacenamiento de imágenes"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'static', 'images', filename)

def ensure_image_exists(image_url_fragment):
    """
    Verifica si la imagen existe localmente. Si no, la descarga.
    image_url_fragment ejemplo: items/images/en/dual_rounds.png
    Devuelve el nombre del archivo local.
    """
    if not image_url_fragment:
        return None
        
    filename = os.path.basename(image_url_fragment)
    local_path = get_image_path(filename)
    
    if os.path.exists(local_path):
        return filename
        
    # Si no existe, descargar
    base_assets_url = "https://warframe.market/static/assets/"
    full_url = base_assets_url + image_url_fragment
    
    try:
        response = _make_request(full_url, stream=True)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return filename
    except Exception as e:
        print(f"Error descargando imagen {full_url}: {e}")
        return None

def get_market_data(item_name, rank=None):
    """
    Obtiene estadísticas de mercado para un item.
    Utiliza caché en memoria por 5 minutos para evitar spam a la API.
    """
    global MARKET_DATA_CACHE
    
    # Clave de caché única
    cache_key = f"{item_name}|{rank}"
    current_time = time.time()
    
    # Verificar caché
    if cache_key in MARKET_DATA_CACHE:
        timestamp, cached_data = MARKET_DATA_CACHE[cache_key]
        if current_time - timestamp < CACHE_DURATION:
            return cached_data

    # Seguimos usando v1 para estadísticas
    url = f"https://api.warframe.market/v1/items/{item_name}/statistics"
    headers = {
        'Language': 'es', 
        'Platform': 'pc',
        'User-Agent': 'Mozilla/5.0'
    }
    
    result_data = {
        "price": 0, "trend": 0, "volume": 0,
        "min_price": 0, "max_price": 0, "avg_price": 0
    }

    try:
        response = _make_request(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Tomamos los últimos 2 días
        stats = data.get('payload', {}).get('statistics_closed', {}).get('48hours', [])
        
        # Filtrar por rango si se especifica
        if rank is not None:
            try:
                target_rank = int(rank)
                stats = [s for s in stats if s.get('mod_rank') == target_rank]
            except (ValueError, TypeError):
                pass
        
        # Helper para procesar estadísticas
        def process_stats_entries(entries):
            if not entries: return None
            last = entries[-1]
            prev = entries[-2] if len(entries) >= 2 else last
            trend = ((last['avg_price'] - prev['avg_price']) / prev['avg_price'] * 100) if prev['avg_price'] > 0 else 0
            
            return {
                "price": last['avg_price'],
                "trend": round(trend, 2),
                "volume": last.get('volume', 0),
                "min_price": last.get('min_price', 0),
                "max_price": last.get('max_price', 0),
                "avg_price": last.get('avg_price', 0)
            }

        # Detección de Reliquias (Refinement/Subtype)
        if not rank and stats and 'subtype' in stats[0]:
            subtypes_data = {}
            for s in stats:
                st = s.get('subtype')
                if st:
                    if st not in subtypes_data:
                        subtypes_data[st] = []
                    subtypes_data[st].append(s)
            
            if subtypes_data:
                result_data = {
                    "is_refined": True,
                    "refinements": list(subtypes_data.keys()),
                }
                # Procesar cada subtipo
                for st, entries in subtypes_data.items():
                    result_data[st] = process_stats_entries(entries)
                
                MARKET_DATA_CACHE[cache_key] = (current_time, result_data)
                return result_data

        # Si no se especifica rango, pero el item tiene rangos (detectamos mod_rank en stats)
        if not rank and stats and 'mod_rank' in stats[0]:
            ranks_data = {}
            for s in stats:
                r = s.get('mod_rank')
                if r is not None:
                    if r not in ranks_data:
                        ranks_data[r] = []
                    ranks_data[r].append(s)
            
            if ranks_data:
                available_ranks = sorted(list(ranks_data.keys()))
                min_rank = available_ranks[0]
                max_rank = available_ranks[-1]
                
                result_data = {
                    "is_ranked": True,
                    "min_rank": min_rank,
                    "max_rank": max_rank,
                    "rank_0": process_stats_entries(ranks_data.get(min_rank)),
                    "rank_max": process_stats_entries(ranks_data.get(max_rank))
                }
                MARKET_DATA_CACHE[cache_key] = (current_time, result_data)
                return result_data

        if len(stats) >= 1:
             processed = process_stats_entries(stats)
             if processed:
                 result_data = processed
            
    except Exception as e:
        print(f"Error fetching data for {item_name}: {e}")
        
    MARKET_DATA_CACHE[cache_key] = (current_time, result_data)
    return result_data

def get_item_orders(url_name):
    """
    Obtiene las órdenes de compra y venta activas para un item usando la API v2.
    Filtra usuarios online/ingame y ordena por mejor precio.
    """
    # Usamos v2 que devuelve órdenes de usuarios activos en los últimos 7 días (menos datos innecesarios)
    url = f"https://api.warframe.market/v2/orders/item/{url_name}"
    headers = {
        'Language': 'es',
        'Platform': 'pc',
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        response = _make_request(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        # En v2 la estructura es data['data'] que es una lista de órdenes con usuario incluido
        orders = data.get('data', [])
        
        # Filtrar solo usuarios activos
        active_orders = [
            o for o in orders 
            if o.get('user', {}).get('status') in ['ingame', 'online']
        ]
        
        sell_orders = []
        buy_orders = []
        
        for o in active_orders:
            user_data = o.get('user', {})
            order_data = {
                'platinum': o.get('platinum'),
                'quantity': o.get('quantity'),
                'user': {
                    'name': user_data.get('ingameName'),
                    'status': user_data.get('status'),
                    'reputation': user_data.get('reputation')
                },
                'platform': user_data.get('platform', 'pc'),
                'region': user_data.get('region', 'en'),
                'creation_date': o.get('createdAt'),
                'last_update': o.get('updatedAt'),
                # Campos adicionales útiles
                'rank': o.get('rank'),  # Para mods/arcanos
                'subtype': o.get('subtype')  # Para reliquias/otros
            }
            
            if o.get('type') == 'sell':
                sell_orders.append(order_data)
            else:
                buy_orders.append(order_data)
        
        # Ordenar: Vendedores (menor precio primero), Compradores (mayor precio primero)
        sell_orders.sort(key=lambda x: x['platinum'])
        buy_orders.sort(key=lambda x: x['platinum'], reverse=True)
        
        return {
            'sell': sell_orders[:10], # Top 10 más baratos
            'buy': buy_orders[:10]    # Top 10 pagan más
        }
        
    except Exception as e:
        print(f"Error fetching orders for {url_name}: {e}")
        return {'sell': [], 'buy': []}

def get_full_item_details(url_name):
    """
    Intenta obtener detalles completos del item.
    Primero busca en caché, luego intenta la API v1 (si funciona), 
    o devuelve lo que tiene en caché enriquecido con estadísticas.
    """
    metadata = get_item_metadata(url_name)
    
    # Si no hay metadatos en caché, inicializamos con datos básicos
    # Esto permite que funcione incluso si get_all_items falló o el ítem es nuevo
    if not metadata:
        metadata = {
            'url_name': url_name,
            'item_name': url_name.replace('_', ' ').title(),
            'thumb': None,
            'tags': []
        }
        
    # Estructura base
    details = {
        **metadata,
        "description": "No disponible",
        "wiki_link": None,
        "drop_locations": [],
        "related_items": [],
        "set_components": [],
        "icon": None
    }
    
    # Fix para items sin imagen (común en Sets): intentar usar el blueprint
    if not details.get('thumb') and '_set' in url_name:
        bp_name = url_name.replace('_set', '_blueprint')
        bp_metadata = get_item_metadata(bp_name)
        if bp_metadata and bp_metadata.get('thumb'):
            details['thumb'] = bp_metadata['thumb']

    # Intentar obtener más info de la API v1 o v2
    # Nota: El endpoint v1/items/<url_name> falla para sets (404), pero v2 funciona.
    url = f"https://api.warframe.market/v1/items/{url_name}"
    headers = {
        'Language': 'es', 
        'Platform': 'pc',
        'User-Agent': 'Mozilla/5.0'
    }
    
    def process_payload(payload):
        # Si es un set, el payload tiene 'items_in_set'
        if 'items_in_set' in payload:
            # Guardar los componentes del set
            components = []
            for comp in payload['items_in_set']:
                # Identificar si es el "Set" principal (usualmente items_in_set tiene todo)
                comp_name = comp.get('es', {}).get('item_name') or comp.get('en', {}).get('item_name')
                components.append({
                    'item_name': comp_name,
                    'url_name': comp.get('url_name'),
                    'thumb': comp.get('thumb'),
                    'set_root': comp.get('set_root'),
                    'quantity': comp.get('quantity_for_set') # A veces útil
                })
            
            details['set_components'] = components

            # Buscar el item específico dentro del set para obtener SU descripción
            target_item = next((i for i in payload['items_in_set'] if i.get('url_name') == url_name), None)
            if target_item:
                return target_item
        return payload

    try:
        response = _make_request(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            payload = data.get('payload', {}).get('item', {})
            payload = process_payload(payload)
        else:
            # Fallback to V2
            url_v2 = f"https://api.warframe.market/v2/items/{url_name}"
            response_v2 = _make_request(url_v2, headers=headers)
            if response_v2.status_code == 200:
                data_v2 = response_v2.json()
                
                # V2 Structure: data.data.{i18n, setParts (ids), ...}
                v2_data = data_v2.get('data', {})
                
                # Extract basic info from V2 i18n
                if 'i18n' in v2_data:
                    i18n = v2_data['i18n']
                    lang_data = i18n.get('es', {}) or i18n.get('en', {})
                    details["description"] = lang_data.get('description', "No disponible")
                    details["wiki_link"] = lang_data.get('wikiLink')
                    details["icon"] = lang_data.get('icon')
                    # V2 thumb is often in i18n too
                    if 'thumb' in lang_data:
                         details['thumb'] = lang_data['thumb']
                    
                    if 'ducats' in v2_data:
                        details['ducats'] = v2_data['ducats']

                # Handle V2 setParts (list of IDs)
                if 'setParts' in v2_data and isinstance(v2_data['setParts'], list):
                    part_ids = v2_data['setParts']
                    
                    def fetch_part_info(part_id):
                        try:
                            p_url = f"https://api.warframe.market/v2/items/{part_id}"
                            p_res = _make_request(p_url, headers=headers)
                            if p_res.status_code == 200:
                                p_data = p_res.json().get('data', {})
                                p_i18n = p_data.get('i18n', {}).get('es', {}) or p_data.get('i18n', {}).get('en', {})
                                # Prefer subIcon for components as main thumb often points to the set image
                                thumb = p_i18n.get('subIcon') or p_i18n.get('thumb')
                                return {
                                    'item_name': p_i18n.get('name'),
                                    'url_name': p_data.get('slug'),
                                    'thumb': thumb,
                                    'set_root': p_data.get('setRoot'),
                                    'quantity': p_data.get('quantityInSet')
                                }
                        except Exception as e:
                            print(f"Error fetching part {part_id}: {e}")
                            return None
                        return None

                    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                        results = executor.map(fetch_part_info, part_ids)
                    
                    components = [r for r in results if r is not None]
                    
                    # Filter out the set itself if desired, or keep it. 
                    # Usually we want to show parts. The set itself has setRoot=True?
                    # Let's keep all for now, maybe filter by slug != current url_name
                    components = [c for c in components if c['url_name'] != url_name]
                    
                    details['set_components'] = components
                
                # Prevent overwriting details below with empty payload
                payload = {} 

        # Common assignment after getting payload (from v1 or v2)
        if payload:
             # Intentar mejorar nombre e imagen si el payload tiene info (especialmente útil si no estaba en caché)
             name_es = payload.get('es', {}).get('item_name')
             name_en = payload.get('en', {}).get('item_name')
             if name_es or name_en:
                 details['item_name'] = name_es or name_en
                 
             if not details.get('thumb'):
                 details['thumb'] = payload.get('thumb')

             if 'description' in payload or 'description_es' in payload or 'es' in payload:
                 # Extraer descripción con prioridad: es > en > campo directo
                 desc_es = payload.get('es', {}).get('description')
                 desc_en = payload.get('en', {}).get('description')
                 details["description"] = payload.get('description_es') or desc_es or payload.get('description_en') or desc_en or payload.get('description') or "No disponible"
                 
                 details["wiki_link"] = payload.get('wiki_link')
                 details["drop_locations"] = payload.get('drop_locations', [])
                 details["icon"] = payload.get('icon')
                 
                 # Extraer valor en ducados si existe (común en partes Prime)
                 if payload.get('ducats'):
                     details['ducats'] = payload.get('ducats')
            
    except Exception as e:
        print(f"Warning: Could not fetch extra details for {url_name}: {e}")

    # Asegurar que la imagen principal esté disponible localmente
    if details.get('thumb'):
        details['image'] = ensure_image_exists(details['thumb'])
        
    # Fetch Stats and History
    stats = get_market_data(url_name)
    if stats:
        details['stats'] = stats
        
    history = get_item_history(url_name)
    if history:
        details['history'] = history

    # Verificar estado de Vault (Vaulted/Active/Resurgence)
    try:
        from backend.services.vault_service import get_vault_status, get_vault_weapons_status
        
        tags = details.get('tags', [])
        is_vaulted = False
        is_resurgence = False
        
        if 'prime' in tags and 'set' in tags:
            vault_data = None
            if 'warframe' in tags:
                vault_data = get_vault_status()
            elif any(t in tags for t in ['weapon', 'primary', 'secondary', 'melee', 'archgun', 'sentinel', 'archwing']):
                vault_data = get_vault_weapons_status()
            
            if vault_data:
                # Verificar si está en la lista de vaulted
                # vault_data['vaulted'] es una lista de dicts: [{'slug': '...', ...}]
                if any(v['slug'] == url_name for v in vault_data.get('vaulted', [])):
                    is_vaulted = True
                
                # Verificar si está en resurgence
                if any(v['slug'] == url_name for v in vault_data.get('resurgence', [])):
                    is_resurgence = True
                    
        details['is_vaulted'] = is_vaulted
        details['is_resurgence'] = is_resurgence

    except Exception as e:
        print(f"Error checking vault status for {url_name}: {e}")
        details['is_vaulted'] = False
        details['is_resurgence'] = False

    return details

def get_item_history(item_name):
    """
    Obtiene el historial de 90 días y 48 horas para gráficas.
    Separa por rangos si es un mod.
    """
    url = f"https://api.warframe.market/v1/items/{item_name}/statistics"
    headers = {
        'Language': 'es', 
        'Platform': 'pc',
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        response = _make_request(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        stats_closed = data.get('payload', {}).get('statistics_closed', {})
        stats_90 = stats_closed.get('90days', [])
        stats_48 = stats_closed.get('48hours', [])
        
        def process_stats_list(stats_list):
            if not stats_list:
                return {}
                
            # Check if it has subtypes (Relics)
            has_subtypes = 'subtype' in stats_list[0]

            if has_subtypes:
                subtypes_data = {}
                for s in stats_list:
                    st = s.get('subtype')
                    if st:
                        if st not in subtypes_data:
                            subtypes_data[st] = []
                        subtypes_data[st].append(s)
                
                result = {}
                if subtypes_data:
                    for st, entries in subtypes_data.items():
                        result[st] = entries
                    result['refinements'] = list(subtypes_data.keys())
                return result

            # Check if it has ranks
            has_ranks = 'mod_rank' in stats_list[0]
            
            if not has_ranks:
                return {"general": stats_list}
                
            # Group by rank
            ranks_data = {}
            for s in stats_list:
                r = s.get('mod_rank')
                if r is not None:
                    if r not in ranks_data:
                        ranks_data[r] = []
                    ranks_data[r].append(s)
            
            result = {}
            for r, entries in ranks_data.items():
                key = f"rank_{r}"
                result[key] = entries
                
            if ranks_data:
                result['ranks'] = sorted(list(ranks_data.keys()))
                
            return result

        # Procesar ambos periodos
        result_90d = process_stats_list(stats_90)
        result_48h = process_stats_list(stats_48)

        # Guardar en BD local (solo 90d por simplicidad o ambos)
        # Por compatibilidad y evitar complejidad, guardamos 'general' de 90d si existe
        if 'general' in result_90d:
             save_price_history(item_name, result_90d['general'], variant='default')
        
        return {
            "90d": result_90d,
            "48h": result_48h
        }
        
    except Exception as e:
        print(f"Error fetching history for {item_name}: {e}")
        return {}
