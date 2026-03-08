import json
import os

DATA_FILE = 'watchlist.json'

def load_watchlist():
    if not os.path.exists(DATA_FILE):
        # Datos por defecto (migrados a objetos)
        default_data = [
            {'url_name': 'arcane_energize', 'rank': None},
            {'url_name': 'glaive_prime_set', 'rank': None},
            {'url_name': 'blind_rage', 'rank': None}
        ]
        save_watchlist(default_data)
        return default_data
    
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            # Migración al vuelo: si encontramos strings, convertirlos
            migrated = []
            needs_save = False
            for item in data:
                if isinstance(item, str):
                    migrated.append({'url_name': item, 'rank': None})
                    needs_save = True
                else:
                    migrated.append(item)
            
            if needs_save:
                save_watchlist(migrated)
                return migrated
            return data
    except:
        return []

def save_watchlist(items):
    with open(DATA_FILE, 'w') as f:
        json.dump(items, f, indent=2)

def add_item(item_url_name, rank=None):
    items = load_watchlist()
    # Verificar si ya existe el par (url_name, rank)
    for item in items:
        if item['url_name'] == item_url_name and item.get('rank') == rank:
            return False
            
    items.append({'url_name': item_url_name, 'rank': rank})
    save_watchlist(items)
    return True

def remove_item(item_url_name, rank=None):
    items = load_watchlist()
    original_len = len(items)
    # Filtramos para quitar el que coincida exactamente
    # Nota: rank puede ser None en el json y None en el argumento
    items = [i for i in items if not (i['url_name'] == item_url_name and i.get('rank') == rank)]
    
    if len(items) < original_len:
        save_watchlist(items)
        return True
    return False
