import json
from datetime import datetime
from backend.extensions import db
from backend.models import Item, PriceHistory, VoidTraderHistory
from sqlalchemy import desc

def upsert_item(item_data):
    tags_json = json.dumps(item_data.get('tags', []))
    now = datetime.now().isoformat()
    
    # Usamos merge que actúa como un UPSERT basado en la Primary Key (url_name)
    item = Item(
        url_name=item_data['url_name'],
        item_name=item_data.get('item_name'),
        thumb=item_data.get('thumb'),
        tags=tags_json,
        last_updated=now
    )
    
    db.session.merge(item)
    db.session.commit()

def save_price_history(url_name, history_data, variant='default'):
    """
    history_data: lista de dicts con keys {datetime/date, avg_price, min_price, max_price, volume}
    variant: identificador del subtipo (ej: 'rank_max', 'radiant')
    """
    for entry in history_data:
        # Normalizar fecha
        raw_date = entry.get('datetime', entry.get('date'))
        if not raw_date: continue
        
        date_str = raw_date.split('T')[0] if 'T' in str(raw_date) else str(raw_date)
        
        # Buscar si ya existe
        history_entry = PriceHistory.query.filter_by(
            url_name=url_name,
            variant=variant,
            date=date_str
        ).first()
        
        if history_entry:
            # Actualizar existente
            history_entry.avg_price = entry.get('avg_price', 0)
            history_entry.min_price = entry.get('min_price', 0)
            history_entry.max_price = entry.get('max_price', 0)
            history_entry.volume = entry.get('volume', 0)
        else:
            # Crear nuevo
            new_entry = PriceHistory(
                url_name=url_name,
                variant=variant,
                date=date_str,
                avg_price=entry.get('avg_price', 0),
                min_price=entry.get('min_price', 0),
                max_price=entry.get('max_price', 0),
                volume=entry.get('volume', 0)
            )
            db.session.add(new_entry)
    
    db.session.commit()

def get_local_history(url_name, variant='default', days=90):
    entries = PriceHistory.query.filter_by(
        url_name=url_name, 
        variant=variant
    ).order_by(PriceHistory.date.asc()).limit(days).all()
    
    return [{
        'date': entry.date,
        'avg_price': entry.avg_price,
        'min_price': entry.min_price,
        'max_price': entry.max_price,
        'volume': entry.volume
    } for entry in entries]

def save_void_trader_inventory(inventory_list, arrival_date):
    """
    Guarda el inventario de Baro Ki'Teer.
    inventory_list: lista de dicts {item_name, url_name, ducats, credits, market_stats}
    """
    for item in inventory_list:
        market_price = 0
        if item.get('market_stats'):
            market_price = item['market_stats'].get('avg_price', 0)

        # Buscar si existe
        entry = VoidTraderHistory.query.filter_by(
            arrival_date=arrival_date,
            item_name=item.get('item_name')
        ).first()

        if entry:
            # Actualizar
            entry.market_price = market_price
            # Podríamos actualizar otros campos si fuera necesario, pero item_name es parte de la clave única lógica junto con fecha
        else:
            # Crear
            new_entry = VoidTraderHistory(
                arrival_date=arrival_date,
                item_name=item.get('item_name'),
                url_name=item.get('url_name'),
                ducats=item.get('ducats', 0),
                credits=item.get('credits', 0),
                market_price=market_price
            )
            db.session.add(new_entry)
        
    db.session.commit()

def get_void_trader_history(limit=100):
    """
    Obtiene el historial de Baro, agrupado por fecha.
    Devuelve lista de objetos con fecha e items.
    """
    # Obtener fechas únicas ordenadas
    dates_query = db.session.query(VoidTraderHistory.arrival_date)\
        .distinct()\
        .order_by(desc(VoidTraderHistory.arrival_date))\
        .limit(limit)\
        .all()
    
    dates = [row[0] for row in dates_query]
    
    history = []
    for date in dates:
        items_query = VoidTraderHistory.query.filter_by(arrival_date=date).all()
        items = [{
            'item_name': item.item_name,
            'url_name': item.url_name,
            'ducats': item.ducats,
            'credits': item.credits,
            'market_price': item.market_price
        } for item in items_query]
        
        history.append({
            'date': date,
            'items': items
        })
        
    return history
