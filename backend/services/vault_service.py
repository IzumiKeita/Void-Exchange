import requests
import json
import requests
import time
from datetime import datetime
from backend.services.market_service import get_all_items

# Lista manual de Primes Activos (Ordenados por fecha de salida: Nuevo -> Viejo)
# Esta lista debe actualizarse cuando salga un nuevo Prime.
# Última actualización: Diciembre 2025
ACTIVE_PRIMES = [
    "Gyre Prime",     # Dic 2025
    "Yareli Prime",   # May 2025
    "Lavos Prime",    # Feb 2025
    "Xaku Prime",     # Nov 2024
    "Sevagoth Prime", # Ago 2024
    "Protea Prime",   # May 2024
    "Gauss Prime"     # Ene 2024 -> Próximo a Vault
]

# Lista manual de Armas Prime Activas (Mapeadas a su Warframe para heredar fecha)
# Esto es más seguro que intentar deducirlo programáticamente sin una DB relacional.
ACTIVE_WEAPONS = [
    # Gyre Prime
    "Alternox Prime", "Kestrel Prime",
    # Yareli Prime
    "Kompressa Prime", 
    # Lavos Prime
    "Cedo Prime",
    # Xaku Prime
    "Quassus Prime", "Trumna Prime",
    # Sevagoth Prime
    "Epitaph Prime", "Nautilus Prime",
    # Protea Prime
    "Velox Prime", "Okina Prime",
    # Gauss Prime
    "Acceltra Prime", "Akarius Prime"
]

WEAPONS_NEXT_TO_VAULT = ["Acceltra Prime", "Akarius Prime"]

VAULT_CACHE = {
    'data': {},
    'weapons_data': {},
    'last_update': 0
}
CACHE_DURATION = 3600 * 4 # 4 horas

def get_vault_weapons_status():
    global VAULT_CACHE
    current_time = time.time()
    
    if VAULT_CACHE['weapons_data'] and (current_time - VAULT_CACHE['last_update'] < CACHE_DURATION):
        return VAULT_CACHE['weapons_data']

    # 1. Obtener Resurgimiento (Varzia) - Reutilizamos lógica pero filtramos armas
    resurgence_weapons = []
    try:
        response = requests.get("https://api.warframestat.us/pc")
        if response.status_code == 200:
            data = response.json()
            inventory = data.get('vaultTrader', {}).get('inventory', [])
            
            for item in inventory:
                name = item.get('item', '')
                # Buscamos items que sean Prime pero NO Warframes (ni cosméticos puros)
                # La API de WorldState a veces devuelve "Lex Prime" tal cual.
                # Filtramos cosméticos comunes
                if 'Prime' in name and not any(x in name for x in ['Pack', 'Skin', 'Glyph', 'Noggle', 'Bobble', 'Accessories', 'Syandana', 'Armor', 'Sugatra', 'Dangle', 'Statue', 'Sigil']):
                     # Si no está en ACTIVE_PRIMES (Warframes), asumimos que podría ser arma o centinela
                     if not any(wf in name for wf in ACTIVE_PRIMES):
                         # Ojo: Aquí también entran Warframes Vaulted que están en Resurgence.
                         # Necesitamos filtrar los que NO son Warframes.
                         # Lo haremos más adelante validando contra Market Tags.
                         resurgence_weapons.append(name)
            
            resurgence_weapons = list(set(resurgence_weapons))
    except Exception as e:
        print(f"Error fetching WorldState for Vault Weapons: {e}")

    # 2. Clasificar todas las Armas Prime
    all_items = get_all_items()
    items_map = {i['url_name']: i for i in all_items}

    # Función auxiliar find_slug (reutilizable si la sacamos fuera, pero la copio por ahora o la muevo al scope global si fuera necesario, aquí la defino local para armas)
    def find_slug(english_name):
        # Intento 1: Construcción estándar de slug + '_set'
        slug = english_name.lower().replace(' ', '_').replace('&', 'and') + '_set'
        if slug in items_map:
            return slug
        # Intento 2: Sin suffix
        slug = english_name.lower().replace(' ', '_').replace('&', 'and')
        if slug in items_map:
            return slug
        return None

    active_list = []
    resurgence_list = []
    vaulted_list = []

    # A. Active Weapons
    for name in ACTIVE_WEAPONS:
        slug = find_slug(name)
        if slug:
            item_data = items_map.get(slug)
            active_list.append({
                'name': item_data['item_name'],
                'slug': slug,
                'thumb': item_data.get('thumb'),
                'type': 'Active',
                'next_to_vault': name in WEAPONS_NEXT_TO_VAULT
            })

    # B. Resurgence Weapons
    for name in resurgence_weapons:
        slug = find_slug(name)
        if slug:
            # Validar si ya está en active
            if any(x['slug'] == slug for x in active_list):
                continue
                
            item_data = items_map.get(slug)
            tags = item_data.get('tags', [])
            
            # FILTRO CRÍTICO: Debe ser arma (weapon, primary, secondary, melee, archgun) o sentinel
            # Y NO debe ser Warframe
            if 'warframe' in tags:
                continue
                
            # Aceptar si tiene tag weapon o es sentinel
            is_weapon_or_sentinel = any(t in tags for t in ['weapon', 'primary', 'secondary', 'melee', 'archgun', 'sentinel'])
            
            if is_weapon_or_sentinel:
                resurgence_list.append({
                    'name': item_data['item_name'],
                    'slug': slug,
                    'thumb': item_data.get('thumb'),
                    'type': 'Resurgence'
                })

    # C. Vaulted Weapons
    # Iteramos sobre TODOS los items de market buscando Sets de Armas Prime
    for item in all_items:
        tags = item.get('tags', [])
        name = item.get('item_name', '')
        slug = item.get('url_name', '')
        
        # Debe ser Prime y Set
        if 'prime' in tags and 'set' in tags:
            # Debe ser arma o centinela, y NO warframe
            if 'warframe' in tags:
                continue
                
            is_weapon = any(t in tags for t in ['weapon', 'primary', 'secondary', 'melee', 'archgun', 'sentinel', 'archwing'])
            
            if is_weapon:
                # Verificar si ya está en active o resurgence
                if any(x['slug'] == slug for x in active_list) or any(x['slug'] == slug for x in resurgence_list):
                    continue
                
                # Es Vaulted
                clean_name = name.replace("Set de ", "").replace(" Set", "")
                
                # Exclusiones especiales (Armas Founder o Login Rewards que no son tradeables o nunca vuelven igual)
                # Skana Prime, Lato Prime (Founders) -> No tradeables? Market las lista. Son vaulted eternas.
                # Las incluimos como Vaulted.
                
                vaulted_list.append({
                    'name': clean_name,
                    'slug': slug,
                    'thumb': item.get('thumb'),
                    'type': 'Vaulted'
                })

    # Ordenar
    vaulted_list.sort(key=lambda x: x['name'])
    
    result = {
        'active': active_list,
        'resurgence': resurgence_list,
        'vaulted': vaulted_list
    }
    
    VAULT_CACHE['weapons_data'] = result
    # No actualizamos last_update aquí para no invalidar el caché de frames si se llama por separado, 
    # pero como comparten CACHE_DURATION, idealmente deberían sincronizarse. 
    # Simplificación: Usamos el mismo last_update.
    if VAULT_CACHE['last_update'] == 0:
        VAULT_CACHE['last_update'] = current_time
        
    return result

def get_vault_status():
    global VAULT_CACHE
    current_time = time.time()
    
    if VAULT_CACHE['data'] and (current_time - VAULT_CACHE['last_update'] < CACHE_DURATION):
        return VAULT_CACHE['data']
    
    # 1. Obtener Resurgimiento (Varzia)
    resurgence_primes = []
    try:
        response = requests.get("https://api.warframestat.us/pc")
        if response.status_code == 200:
            data = response.json()
            inventory = data.get('vaultTrader', {}).get('inventory', [])
            
            for item in inventory:
                name = item.get('item', '')
                # Filtrar solo Warframes Prime (evitar skins, accesorios, packs)
                if 'Prime' in name and not any(x in name for x in ['Pack', 'Skin', 'Glyph', 'Noggle', 'Bobble', 'Accessories', 'Syandana', 'Armor', 'Sugatra', 'Weapon', 'Dangle']):
                     # A veces el nombre viene como "Mesa Prime" limpio
                     resurgence_primes.append(name)
                # También buscar en los Packs para extraer nombres si es necesario, 
                # pero Varzia suele vender los frames sueltos también.
                # Nota: En el log vimos "Mesa Prime", "Hydroid Prime" limpios.
            
            # Limpiar duplicados
            resurgence_primes = list(set(resurgence_primes))
    except Exception as e:
        print(f"Error fetching WorldState for Vault: {e}")
        
    # 2. Clasificar todos los Warframes Prime
    all_items = get_all_items()
    
    active_list = []
    resurgence_list = []
    vaulted_list = []
    
    # Mapa para enriquecer con imágenes
    items_map = {i['url_name']: i for i in all_items}
    
    # Función auxiliar para encontrar slug
    def find_slug(english_name):
        # Intento 1: Construcción estándar de slug
        slug = english_name.lower().replace(' ', '_') + '_set'
        if slug in items_map:
            return slug
        
        # Intento 2: Sin suffix '_set' (para frames que no tienen set? Raro en primes)
        slug = english_name.lower().replace(' ', '_')
        if slug in items_map:
            return slug
            
        # Intento 3: Búsqueda parcial en items_map (lento pero seguro)
        # Buscar si algún slug contiene el nombre normalizado
        normalized = english_name.lower().replace(' ', '_')
        for s in items_map.keys():
            if normalized in s and 'set' in s:
                return s
        return None

    # Procesar ACTIVE_PRIMES
    for name in ACTIVE_PRIMES:
        slug = find_slug(name)
             
        if slug:
            item_data = items_map.get(slug)
            active_list.append({
                'name': item_data['item_name'], # Usar nombre real (ES)
                'slug': slug,
                'thumb': item_data.get('thumb'),
                'type': 'Active',
                'next_to_vault': name == ACTIVE_PRIMES[-1] # El último es el más viejo
            })

    # Procesar WEAPONS_NEXT_TO_VAULT (Agregarlas a Active List marcadas como next_to_vault)
    for name in WEAPONS_NEXT_TO_VAULT:
        slug = find_slug(name)
        if slug:
            item_data = items_map.get(slug)
            # Verificar si ya está para no duplicar (aunque active_list tiene frames)
            if not any(x['slug'] == slug for x in active_list):
                active_list.append({
                    'name': item_data['item_name'],
                    'slug': slug,
                    'thumb': item_data.get('thumb'),
                    'type': 'Active',
                    'next_to_vault': True
                })

    # Procesar RESURGENCE
    for name in resurgence_primes:
        slug = find_slug(name)
        
        # Evitar duplicados si ya está en active (aunque no debería)
        if slug and slug not in [x['slug'] for x in active_list]:
            item_data = items_map.get(slug)
            
            # Verificar que sea un Warframe (filtrar armas que pasaron el filtro de nombre)
            if 'warframe' not in item_data.get('tags', []):
                continue
                
            resurgence_list.append({
                'name': item_data['item_name'],
                'slug': slug,
                'thumb': item_data.get('thumb'),
                'type': 'Resurgence'
            })

    # Procesar VAULTED (El resto de Warframes Prime)
    # Identificar todos los Sets de Warframes Prime
    for item in all_items:
        name = item.get('item_name', '')
        slug = item.get('url_name', '')
        tags = item.get('tags', [])
        
        if 'warframe' in tags and 'prime' in tags and 'set' in tags:
            # Verificar si ya está en active o resurgence
            is_active = any(x['slug'] == slug for x in active_list)
            is_resurgence = any(x['slug'] == slug for x in resurgence_list)
            
            if not is_active and not is_resurgence:
                # Es Vaulted
                # Limpiar nombre "Set de "
                clean_name = name.replace("Set de ", "").replace(" Set", "")
                
                # Excluir Excalibur Prime (Founder exclusive, nunca vuelve)
                if "Excalibur" in clean_name:
                    continue
                    
                vaulted_list.append({
                    'name': clean_name,
                    'slug': slug,
                    'thumb': item.get('thumb'),
                    'type': 'Vaulted'
                })
    
    # Ordenar alfabéticamente
    vaulted_list.sort(key=lambda x: x['name'])
    
    result = {
        'active': active_list,
        'resurgence': resurgence_list,
        'vaulted': vaulted_list,
        'next_vaulting': ACTIVE_PRIMES[-1] if ACTIVE_PRIMES else None
    }
    
    VAULT_CACHE['data'] = result
    VAULT_CACHE['last_update'] = current_time
    
    return result
