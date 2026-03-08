import requests
import datetime
import time
import json
from backend.services.market_service import get_all_items, get_market_data, get_item_by_game_ref, get_item_metadata
from backend.services.database_service import save_void_trader_inventory, get_void_trader_history

# URL oficial de estado del mundo (más robusta que api.warframestat.us)
WORLD_STATE_URL = "http://content.warframe.com/dynamic/worldState.php"

# Cargar traducciones manuales desde JSON
import os
import sys

# Ajustar BASE_DIR para aplicación congelada (PyInstaller)
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRANSLATIONS_FILE = os.path.join(BASE_DIR, 'data', 'translations.json')

COMMON_TRANSLATIONS = {
    "Prisma": "Prisma",
    "Vandal": "Vándalo",
    "Wraith": "Fantasma",
    "Skin": "Diseño",
    "Blueprint": "Plano",
    "Helmet": "Casco",
    "Chassis": "Chasis",
    "Systems": "Sistemas",
    "Neuroptics": "Neurópticas"
}

# Diccionario de corrección de nombres internos/feos a nombres bonitos en español
FIXED_ITEM_NAMES = {
    # --- MODS PRIME Y RAROS ---
    # Nombres internos API
    "Archwing Rifle Damage Amount Mod Expert": "Cañón revestido de rubedo Prime",
    "ArchwingRifleDamageAmountModExpert": "Cañón revestido de rubedo Prime",
    "Archwing Weapon Toxin Damage Mod Expert": "Clip venenoso",
    "ArchwingWeaponToxinDamageModExpert": "Clip venenoso",
    "Avatar Power Max Mod Expert": "Flujo Prime",
    "AvatarPowerMaxModExpert": "Flujo Prime",
    "Secondary Explosion Radius Mod Expert": "Fulminación Prime",
    "SecondaryExplosionRadiusModExpert": "Fulminación Prime",
    "Weapon Damage Amount Mod Expert": "Punto de presión Prime", 
    "WeaponDamageAmountModExpert": "Punto de presión Prime",
    "Weapon Event Shotgun Impact Damage Mod": "Contacto total",
    "WeaponEventShotgunImpactDamageMod": "Contacto total",
    "Weapon Fire Damage Mod Expert": "Carga incendiaria Prime",
    "WeaponFireDamageModExpert": "Carga incendiaria Prime",
    "Weapon Recoil Reduction Mod Expert": "Manos firmes Prime",
    "WeaponRecoilReductionModExpert": "Manos firmes Prime",
    "Weapon Reload Speed Mod Expert": "Manos rápidas Prime", 
    "WeaponReloadSpeedModExpert": "Manos rápidas Prime",
    "Weapon Crit Chance Mod Expert": "Gambito de pistola Prime",
    "WeaponCritChanceModExpert": "Gambito de pistola Prime",
    "Weapon Crit Damage Mod Expert": "Rompeobjetivos Prime", 
    "WeaponCritDamageModExpert": "Rompeobjetivos Prime",
    "Melee Reach Mod Expert": "Alcance Prime",
    "MeleeReachModExpert": "Alcance Prime",
    
    # Nombres en Inglés (Traducción directa)
    "Primed Flow": "Flujo Prime",
    "Primed Continuity": "Continuidad Prime",
    "Primed Reach": "Alcance Prime",
    "Primed Target Cracker": "Rompeobjetivos Prime",
    "Primed Pistol Gambit": "Gambito de pistola Prime",
    "Primed Heated Charge": "Carga incendiaria Prime",
    "Primed Cryo Rounds": "Cargador criogénico Prime",
    "Primed Point Blank": "Quemarropa Prime",
    "Primed Ravage": "Devastación Prime",
    "Primed Pressure Point": "Punto de presión Prime",
    "Primed Heavy Trauma": "Trauma pesado Prime",
    "Primed Fever Strike": "Golpe de fiebre Prime",
    "Primed Charged Shell": "Cartucho cargado Prime",
    "Primed Morphic Transformer": "Transformador mórfico Prime",
    "Primed Regen": "Regeneración Prime",
    "Primed Animal Instinct": "Instinto animal Prime",
    "Primed Chamber": "Cámara Prime",
    "Primed Tactical Pump": "Bombeo táctico Prime",
    "Primed Slip Magazine": "Cargador deslizante Prime",
    "Primed Rubedo Lined Barrel": "Cañón revestido de rubedo Prime",
    "Primed Shred": "Despedazar Prime", # Login, pero por si acaso
    "Primed Vigor": "Vigor Prime", # Login
    "Primed Fury": "Furia Prime", # Login
    "Primed Sure Footed": "Pies firmes Prime", # Login
    
    # Mods de Evento / Baro
    "Jolt": "Sacudida",
    "High Voltage": "Alto voltaje",
    "Voltaic Strike": "Golpe voltaico",
    "Shell Shock": "Conmoción",
    "Vermilion Storm": "Tormenta bermellón",
    "Astral Twilight": "Crepúsculo astral",
    "Tempo Royale": "Tempo real",
    "Fanged Fusillade": "Fusilada con colmillos",
    "Sweeping Serration": "Sierra de barrido",
    "Maim": "Mutilar",
    "Pummel": "Aporrear",
    "Collision Force": "Fuerza de colisión",
    "Full Contact": "Contacto total",
    "Crash Course": "Curso de colisión",
    "Buzz Kill": "Zumbido de muerte",
    "Piercing Caliber": "Calibre perforante",
    "Breach Loader": "Cargador de brecha",
    "Bore": "Taladro",
    "Auger Strike": "Golpe de barrena",
    "Magma Chamber": "Cámara de magma",
    "Searing Steel": "Acero incandescente",
    
    # --- ARMAS Y VARIANTES ---
    "Prisma Gorgon": "Gorgon Prisma",
    "Prisma Grakata": "Grakata Prisma",
    "Prisma Tetra": "Tetra Prisma",
    "Prisma Skana": "Skana Prisma",
    "Prisma Dual Cleavers": "Cuchillas dobles Prisma",
    "Prisma Obex": "Obex Prisma",
    "Prisma Angstrum": "Angstrum Prisma",
    "Prisma Veritux": "Veritux Prisma",
    "Prisma Shade": "Shade Prisma",
    "Prisma Burst Laser": "Láser de ráfaga Prisma",
    "Mara Detron": "Detron Mara",
    "Supra Vandal": "Supra Vándalo",
    "Prova Vandal": "Prova Vándalo",
    "Quanta Vandal": "Quanta Vándalo",
    "Glaxion Vandal": "Glaxion Vándalo",
    "Imperator Vandal": "Imperator Vándalo",
    "Latron Wraith": "Latron Fantasma",
    "Strun Wraith": "Strun Fantasma",
    "Twin Vipers Wraith": "Vipers gemelas Fantasma",
    "Karak Wraith": "Karak Fantasma",
    "Vulkar Wraith": "Vulkar Fantasma",
    "Ignis Wraith": "Ignis Fantasma",
    "Viper Wraith": "Viper Fantasma",
    "Halikar Wraith": "Halikar Fantasma",
    "Halikar Wraith Weapon": "Halikar Fantasma",
    "HalikarWraithWeapon": "Halikar Fantasma",
    "Crp Prisma Tonfa": "Ohma Prisma",
    "CrpPrismaTonfa": "Ohma Prisma",
    "Prisma Ohma": "Ohma Prisma",
    "Vastilok": "Vastilok",
    "Vericres": "Vericres",
    "Machete Wraith": "Machete Fantasma",
    "Furax Wraith": "Furax Fantasma",
    
    # --- OTROS ---
    "Axi A2 Relic": "Reliquia Axi A2",
    "Neo O1 Relic": "Reliquia Neo O1",
    "Sands Of Inaros": "Arenas de Inaros",
    "Stalker Beacon": "Baliza del Stalker",
    "Zanuka Hunter Beacon": "Baliza del Cazador Zanuka",
    "Grustrag Three Beacon": "Baliza de los Tres Grustrag",
    "Wolf Beacon": "Baliza del Lobo",
}

# Términos comunes para traducción palabra por palabra
COMMON_TERMS = {
    "Prisma": "Prisma",
    "Vandal": "Vándalo",
    "Wraith": "Fantasma",
    "Mara": "Mara",
    "Prime": "Prime",
    "Blueprint": "Plano",
    "Receiver": "Receptor",
    "Barrel": "Cañón",
    "Stock": "Culata",
    "Blade": "Hoja",
    "Handle": "Empuñadura",
    "Link": "Enlace",
    "Heatsink": "Disipador",
    "Motor": "Motor",
    "Gauntlet": "Guantelete",
    "Disc": "Disco",
    "Grip": "Empuñadura",
    "String": "Cuerda",
    "Limb": "Pala",
    "Carapace": "Caparazón",
    "Cerebrum": "Cerebro",
    "Systems": "Sistemas",
    "Chassis": "Chasis",
    "Neuroptics": "Neurópticas",
    "Harness": "Arnés",
    "Wings": "Alas",
    "Skin": "Diseño",
    "Helmet": "Casco",
    "Relic": "Reliquia",
    "Intact": "(Intacta)",
    "Radiant": "(Radiante)",
    "Mod": "Mod",
    "Pack": "Paquete",
    "Bundle": "Pack",
    "Set": "Set",
    "Scene": "Escena",
    "Beacon": "Baliza",
}

def load_translations():
    global COMMON_TRANSLATIONS
    try:
        with open(TRANSLATIONS_FILE, 'r', encoding='utf-8') as f:
            COMMON_TRANSLATIONS = json.load(f)
    except Exception as e:
        print(f"Error loading translations from {TRANSLATIONS_FILE}: {e}")
        # Fallback mínimo si falla el archivo
        COMMON_TRANSLATIONS = {
            "Prisma": "Prisma",
            "Vandal": "Vándalo",
            "Wraith": "Fantasma",
            "Skin": "Diseño",
            "Blueprint": "Plano"
        }

# Cargar al inicio
load_translations()

def _translate_manual(text):
    """Traduce palabras clave en un texto usando el diccionario manual"""
    # Primero reemplazos de frases completas (keys con espacios)
    for key, value in COMMON_TRANSLATIONS.items():
        if " " in key and key in text:
            text = text.replace(key, value)
            
    words = text.split()
    translated_words = []
    for word in words:
        # Intento simple de traducción palabra por palabra manteniendo mayúsculas
        clean_word = word.strip()
        trans = COMMON_TRANSLATIONS.get(clean_word)
        if not trans:
            # Probar singular/plural básico
            if clean_word.endswith('s'):
                trans = COMMON_TRANSLATIONS.get(clean_word[:-1])
                if trans: trans += 's'
        
        translated_words.append(trans if trans else word)
    
    return " ".join(translated_words)

def _determine_category(item_name, is_tradeable):
    """Clasifica el ítem en una categoría"""
    name_lower = item_name.lower()
    
    # Mods: 
    # 1. Tienen "mod" en el nombre (ej. "Mod de daño").
    # 2. Empiezan con "primed" (inglés).
    # 3. Son versiones "Prime" de mods conocidos (ej. "Flujo Prime", "Punto de presión Prime").
    #    Para evitar confundir con armas "Prime", chequeamos palabras clave típicas de mods.
    is_mod = False
    
    if "mod" in name_lower:
        is_mod = True
    elif "primed" in name_lower and "plano" not in name_lower and "cañón" not in name_lower:
        is_mod = True
    elif "prime" in name_lower:
        # Lista de palabras clave que sugieren que ES un mod si lleva Prime
        mod_keywords = [
            "flujo", "continuidad", "alcance", "rompeobjetivos", "gambito", 
            "carga", "cargador", "quemarropa", "devastación", "punto de presión",
            "trauma", "golpe", "cartucho", "transformador", "regeneración",
            "instinto", "cámara", "bombeo", "rubedo", "vigor", "furia", "pies firmes",
            "manos", "clip", "fulminación", "contacto", "cañón revestido"
        ]
        if any(kw in name_lower for kw in mod_keywords):
            is_mod = True
            
    if is_mod:
        return "Mods"
            
    if "relic" in name_lower or "reliquia" in name_lower:
        return "Reliquias"
        
    if is_tradeable:
        # Si es tradeable y no es mod ni reliquia, probablemente es arma o parte de arma
        if any(x in name_lower for x in ['vandal', 'wraith', 'prisma', 'prime', 'mara', 'vándalo', 'fantasma']):
            return "Armas"
        return "Otros (Tradeables)"
        
    return "Cosméticos/Otros"

def _is_blacklisted(item_name):
    """Detecta si un ítem debe ser excluido explícitamente (cosméticos, etc)"""
    n = item_name.lower()
    
    # Lista negra de términos de cosméticos y no tradeables comunes de Baro
    blacklist = [
        'skin', 'diseño', 'aspecto', 'helmet', 'casco',
        'glyph', 'glifo', 'sigil', 'sello', 'emblem', 'emblema',
        'armor', 'armadura', 'syandana', 'sugatra', 'scarf', 'bufanda',
        'decoration', 'decoración', 'noggle', 'estatua', 'statue', 'pedestal',
        'color', 'palette', 'paleta',
        'scene', 'escena', # Algunas escenas son tradeables, pero la mayoría de baro son relleno. Revisar si usuario quiere estricto.
        'emote', 'gesto', 'action', 'acción',
        'mask', 'máscara', 'diadema', 'earpiece', 'auricular',
        'kavat', 'kubrow', 'sentinel', # Cuidado con armas de centinela (Prisma Burst Laser)
        'poster', 'cartel', 'prex',
        'fluff', 'peluche',
        'ephemera', 'efímero', 'efímera',
        'song', 'canción', 'mandachord',
        'drone', 'domestik',
        'transmuter', 'transmutador', # A veces trae transmutadores de núcleos?
        'beacon', 'baliza', # Stalker beacons SON tradeables? No.
        'fireworks', 'fuegos',
        'specter', 'espectro'
    ]
    
    # Excepciones a la regla (Whitelisting parcial para cosas que coinciden con blacklist pero son útiles/tradeables)
    # Ej: "Prisma Shade" (Sentinel) es tradeable (el arma y el propio centinela).
    if 'prisma' in n or 'vandal' in n or 'wraith' in n:
        # Pero si es skin prisma, sigue siendo skin.
        if 'skin' in n or 'diseño' in n or 'sigil' in n or 'glyph' in n or 'scarf' in n:
            return True
        return False
        
    # Chequeo
    for term in blacklist:
        if term in n:
            return True
            
    return False

def _sanitize_item_name(name):
    """Limpia y corrige nombres de items usando el diccionario fijo y lógica de limpieza"""
    if not name:
        return name
        
    # Limpieza básica inicial
    clean_name = name.strip()
    
    # 1. Corrección directa (Exacta)
    if clean_name in FIXED_ITEM_NAMES:
        return FIXED_ITEM_NAMES[clean_name]
        
    # 1b. Corrección case-insensitive y fallback sin espacios
    clean_name_lower = clean_name.lower()
    for key, val in FIXED_ITEM_NAMES.items():
        if key.lower() == clean_name_lower:
            return val
            
    # Fallback: probar quitando espacios (para casos como ArchwingRifle...)
    clean_name_nospace = clean_name.replace(" ", "")
    if clean_name_nospace in FIXED_ITEM_NAMES:
        return FIXED_ITEM_NAMES[clean_name_nospace]
        
    for key, val in FIXED_ITEM_NAMES.items():
        if key.lower() == clean_name_nospace.lower():
            return val
    
    # 2. Reliquias (Caso especial de orden: "Axi A2 Relic" -> "Reliquia Axi A2")
    if "Relic" in clean_name and not clean_name.startswith("Relic") and not clean_name.startswith("Reliquia"):
        # Asumimos formato "Tipo X Relic"
        clean = clean_name.replace("Relic", "").strip()
        return f"Reliquia {clean}"

    # 3. Traducción y Reordenamiento palabra por palabra
    words = clean_name.split()
    
    # Detectar prefijo Prisma/Mara para moverlo al final (Prisma Grakata -> Grakata Prisma)
    prefix_move = None
    if words and words[0] in ["Prisma", "Mara"]:
        prefix_move = words[0]
        words = words[1:]
        
    translated_words = []
    for w in words:
        # Limpiar puntuación básica si la hubiera
        clean_w = w.strip()
        # Buscar en diccionario común
        trans = COMMON_TERMS.get(clean_w, clean_w)
        translated_words.append(trans)
        
    result = " ".join(translated_words)
    
    if prefix_move:
        trans_prefix = COMMON_TERMS.get(prefix_move, prefix_move)
        result = f"{result} {trans_prefix}"
    
    return result

def _parse_wf_date(date_obj):
    """Convierte el formato de fecha de Warframe { "$date": { "$numberLong": "ms" } } a ISO string"""
    try:
        if isinstance(date_obj, dict) and "$date" in date_obj:
            timestamp_ms = int(date_obj["$date"]["$numberLong"])
            dt = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0, tz=datetime.timezone.utc)
            return dt.isoformat()
    except Exception as e:
        print(f"Error parsing date {date_obj}: {e}")
    return None

def fetch_void_trader_data():
    """
    Obtiene los datos actuales del Comerciante del Vacío usando la API oficial.
    Si está activo, cruza los datos con Warframe Market para obtener precios.
    """
    try:
        # Headers básicos
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(WORLD_STATE_URL, headers=headers, timeout=20)
        response.raise_for_status()
        world_state = response.json()
        
        # Buscar VoidTraders
        void_traders = world_state.get('VoidTraders', [])
        if not void_traders:
             return {
                "active": False, 
                "message": "Información de Baro Ki'Teer no disponible en este momento.",
                "location": "Desconocido",
                "startString": "Desconocido",
                "activation": None
            }
            
        # Tomar el primer Void Trader (normalmente solo hay uno activo o programado)
        baro = void_traders[0]
        
        # Parsear fechas
        activation = _parse_wf_date(baro.get('Activation'))
        expiry = _parse_wf_date(baro.get('Expiry'))
        location = baro.get('Node', 'Desconocido')
        
        # Determinar si está activo
        now = datetime.datetime.now(datetime.timezone.utc)
        is_active = False
        
        if activation and expiry:
            act_dt = datetime.datetime.fromisoformat(activation)
            exp_dt = datetime.datetime.fromisoformat(expiry)
            if act_dt <= now <= exp_dt:
                is_active = True
        
        if not is_active:
             return {
                "active": False, 
                "message": "Baro Ki'Teer no está presente.",
                "location": location,
                "activation": activation,
                "expiry": expiry
            }

        # Procesar Inventario (Manifest)
        manifest = baro.get('Manifest', [])
        processed_inventory = []
        
        # Aseguramos que el caché de items por gameRef esté cargado
        market_items_list = get_all_items()
        
        # Construir mapa auxiliar de Nombre -> Slug para fallback
        name_to_slug = {}
        for m_item in market_items_list:
            if m_item.get('item_name_en'):
                name_to_slug[m_item['item_name_en'].lower()] = m_item['url_name']
            if m_item.get('item_name'):
                name_to_slug[m_item['item_name'].lower()] = m_item['url_name']

        for item in manifest:
            item_type = item.get('ItemType') # Ej: /Lotus/StoreItems/...
            ducats = item.get('PrimePrice', 0)
            credits = item.get('RegularPrice', 0)
            
            # --- LÓGICA DE MATCHING MEJORADA ---
            # 1. Intentar match exacto primero (por si acaso)
            market_item = get_item_by_game_ref(item_type)
            
            # 2. Si falla, intentar limpiar '/StoreItems' que añade la API de World State
            if not market_item and item_type:
                # API: /Lotus/StoreItems/Weapons/... -> WFM: /Lotus/Weapons/...
                clean_type = item_type.replace('/StoreItems', '')
                market_item = get_item_by_game_ref(clean_type)
            
            # 3. Si sigue fallando, intentar limpiar sufijos de calidad (Bronze, Silver, Gold, Radiant, Intact)
            # Especialmente para Reliquias
            if not market_item and item_type:
                clean_type = item_type.replace('/StoreItems', '')
                suffixes = ['Bronze', 'Silver', 'Gold', 'Radiant', 'Intact']
                for suffix in suffixes:
                    if clean_type.endswith(suffix):
                        clean_type_no_suffix = clean_type[:-len(suffix)]
                        market_item = get_item_by_game_ref(clean_type_no_suffix)
                        if market_item:
                            break

            item_name = "Desconocido"
            slug = None
            
            if market_item:
                item_name = market_item['item_name']
                slug = market_item['url_name']
            else:
                # Intento de prettify si no se encuentra mapeo
                if item_type:
                    parts = item_type.split('/')
                    raw_name = parts[-1]
                    # Eliminar sufijos comunes de paths internos
                    raw_name = raw_name.replace('Blueprint', '').replace('Receiver', '').replace('Barrel', '').replace('Stock', '')
                    
                    # Separar CamelCase básico
                    import re
                    # "SupraVandal" -> "Supra Vandal"
                    clean_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', raw_name)
                    item_name = clean_name.strip()
                    
                    # Intentar buscar por nombre en el mapa auxiliar
                    # Probamos variaciones
                    variations = [
                        item_name.lower(),
                        item_name.lower() + " blueprint",
                        item_name.lower() + " receiver",
                        item_name.lower() + " stock",
                        item_name.lower() + " barrel"
                    ]
                    
                    for var in variations:
                        if var in name_to_slug:
                            slug = name_to_slug[var]
                            # Si encontramos el slug, actualizamos el nombre visual al nombre oficial del mercado (Español)
                            meta = get_item_metadata(slug)
                            if meta and meta.get('item_name'):
                                item_name = meta['item_name']
                            break
                    
                    # Si no encontramos slug, significa que NO es tradeable (o no está en WFM)
                    # El usuario solicitó EXCLUIR todo lo que no sea comerciable.
                    # Así que si no hay slug, no procesamos este ítem.
                    if not slug:
                        continue
            
            is_tradeable = slug is not None
            
            # --- SANITIZE NAME FIRST ---
            # Saneamos ANTES de filtrar para que la blacklist funcione con nombres en español
            item_name = _sanitize_item_name(item_name)

            # --- CHECK BLACKLIST ---
            if _is_blacklisted(item_name):
                # NO filtrar aquí si queremos guardar el inventario COMPLETO para el historial
                # Pero el usuario pidió "tomar lo que está en Inventario Actual" y "solo lo no tradeable, quede afuera"
                # Requisito contradictorio? 
                # "pero el historico muesta solo pocas cosas, deberia de tomar 'todo lo que se muestra' en el inventario actual"
                # --> Significa que quiere ver en el historial EXACTAMENTE lo mismo que ve en "Inventario Actual".
                # "Inventario Actual" ya filtra blacklist.
                # Así que si filtramos aquí, está bien.
                # PERO tal vez estamos filtrando demasiado?
                # Revisemos la lógica de Inventario Actual.
                continue
            
            # Clasificar
            category = _determine_category(item_name, is_tradeable)
            
            # Filtrar items no tradeables (SOLO si el usuario insiste en que no quiere ver basura)
            # El usuario dijo: "quedemonos con la idea de que solo lo no tradeable, quede afuera"
            # Y luego: "historico muesta solo pocas cosas"
            # Quizás hay cosas tradeables que estamos filtrando por error?
            # O cosas que NO son tradeables pero él quiere ver (como Ducados/Créditos, pero esos no son items).
            # Vamos a confiar en la flag 'is_tradeable' de la API + nuestra blacklist.
            
            if not is_tradeable and category == "Cosméticos/Otros":
                 # Si no es tradeable y es cosmético, fuera.
                 continue
                 
            # Construir objeto
            entry = {
                'item_name': item_name,
                'ducats': ducats,
                'credits': credits,
                'url_name': slug,
                'tradeable': is_tradeable, # Guardar el estado real
                'category': category,
                'market_stats': None
            }
            
            if is_tradeable:
                # Obtener estadísticas de mercado para items tradeables
                # Usamos rank 0 solo para Mods (Baro vende mods sin rango)
                rank = 0 if category == 'Mods' else None
                stats = get_market_data(slug, rank=rank)
                if stats:
                        entry['market_stats'] = stats
                        
            processed_inventory.append(entry)
            
        # Guardar en base de datos para historial
        if processed_inventory:
            # Mantener guardado en DB por si acaso (legacy)
            save_void_trader_inventory(processed_inventory, activation)
            
            # NUEVO: Guardar en Historial JSON (Fuente de verdad limpia)
            _save_history_json(processed_inventory, activation)
            
            # Guardar también en JSON local como respaldo solicitado (Last Inventory)
            try:
                json_path = os.path.join(BASE_DIR, 'data', 'void_trader_last_inventory.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "date": activation,
                        "expiry": expiry,
                        "location": location,
                        "inventory": processed_inventory
                    }, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Error saving local JSON: {e}")
        
        return {
            "active": True,
            "location": location,
            "arrival": activation,
            "expiry": expiry,
            "inventory": processed_inventory
        }
        
    except Exception as e:
        print(f"Error fetching Void Trader data: {e}")
        
        # Intentar cargar respaldo local en caso de error de conexión
        try:
            json_path = os.path.join(BASE_DIR, 'data', 'void_trader_last_inventory.json')
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                
                # Verificar si el caché sigue siendo válido (dentro del periodo de visita)
                expiry_str = cached.get('expiry')
                is_active_cached = False
                if expiry_str:
                    exp_dt = datetime.datetime.fromisoformat(expiry_str)
                    if datetime.datetime.now(datetime.timezone.utc) <= exp_dt:
                        is_active_cached = True
                
                # Sanear inventario en caché por si tiene nombres viejos
                cached_inventory = cached.get('inventory', [])
                clean_cached_inventory = []
                for item in cached_inventory:
                    item['item_name'] = _sanitize_item_name(item.get('item_name', ''))
                    if _is_blacklisted(item['item_name']):
                        continue
                    # Recalcular categoría por si acaso
                    item['category'] = _determine_category(item['item_name'], item.get('tradeable', True))
                    clean_cached_inventory.append(item)
                
                return {
                    "active": is_active_cached,
                    "using_cached": True,
                    "message": "Sin conexión. Mostrando datos guardados.",
                    "location": cached.get('location', 'Desconocido (Caché)'),
                    "arrival": cached.get('date'),
                    "expiry": cached.get('expiry'),
                    "inventory": clean_cached_inventory
                }
        except Exception as cache_e:
            print(f"Error reading cache: {cache_e}")

        return {"error": f"Error de conexión con Warframe: {str(e)}"}

HISTORY_JSON_PATH = os.path.join(BASE_DIR, 'data', 'void_trader_history.json')

def _save_history_json(inventory, date_str):
    """Guarda el inventario limpio de una visita en el historial JSON"""
    try:
        history_data = {}
        if os.path.exists(HISTORY_JSON_PATH):
            with open(HISTORY_JSON_PATH, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
        
        # Guardar/Sobreescribir la entrada de esta fecha
        history_data[date_str] = inventory
        
        with open(HISTORY_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Error saving history JSON: {e}")

def _load_history_json():
    """Carga el historial desde JSON. Si no existe, intenta migrar desde DB."""
    if not os.path.exists(HISTORY_JSON_PATH):
        # Migración inicial: Tomar lo que hay en DB, limpiarlo y guardarlo en JSON
        print("Migrating DB history to JSON...")
        db_history = _get_history_from_db_sanitized()
        if db_history:
            history_data = {}
            for visit in db_history:
                history_data[visit['date']] = visit['items']
            
            try:
                with open(HISTORY_JSON_PATH, 'w', encoding='utf-8') as f:
                    json.dump(history_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Error migrating DB to JSON: {e}")
            return db_history
        return []

    try:
        with open(HISTORY_JSON_PATH, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
            
        # Convertir dict {date: items} a lista ordenada [{date, items}]
        history_list = []
        for date_str, items in history_data.items():
            history_list.append({
                'date': date_str,
                'items': items
            })
        
        # Ordenar por fecha descendente
        history_list.sort(key=lambda x: x['date'], reverse=True)
        return history_list
            
    except Exception as e:
        print(f"Error loading history JSON: {e}")
        return []

def _get_history_from_db_sanitized():
    """Retorna el historial guardado en base de datos con nombres saneados, filtrados y categorizados (Versión Legacy)"""
    history = get_void_trader_history()
    
    clean_history = []
    
    for visit in history:
        # database_service devuelve {'date': ..., 'items': [...]}
        raw_items = visit.get('items', [])
        clean_items = []
        seen_names = set()
        
        for item in raw_items:
            # Crear copia para no mutar referencias extrañas
            item_copy = item.copy()
            
            original_name = item_copy.get('item_name', '')
            
            # 1. Sanear nombre (Corrige nombres viejos/feos)
            new_name = _sanitize_item_name(original_name)
            
            # Deduplicación: Si ya hemos procesado un item que resultó en este nombre, saltar
            if new_name in seen_names:
                continue
            
            # 2. Check Blacklist (Filtrar cosméticos persistentes)
            # COMENTADO: El historial DB es legacy. Si queremos verlo completo, confiamos en la migración.
            # Pero para el "Inventario Actual" -> JSON, ya filtramos la blacklist.
            # Para DB -> JSON migración, SÍ debemos filtrar porque la DB vieja tiene basura.
            if _is_blacklisted(new_name) or _is_blacklisted(original_name):
                continue
            
            # 3. Categorizar
            category = _determine_category(new_name, True)
            
            item_copy['item_name'] = new_name
            item_copy['category'] = category
            
            clean_items.append(item_copy)
            seen_names.add(new_name)
            
        # Solo añadir visitas que tengan items válidos tras el filtrado
        if clean_items:
            # Ordenar items alfabéticamente para mejor presentación
            clean_items.sort(key=lambda x: x['item_name'])
            
            visit_copy = visit.copy()
            visit_copy['items'] = clean_items
            clean_history.append(visit_copy)
            
    return clean_history

def get_baro_history():
    """Retorna el historial desde el archivo JSON consolidado"""
    return _load_history_json()
