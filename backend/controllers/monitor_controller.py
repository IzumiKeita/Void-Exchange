from flask import Blueprint, jsonify, request
from backend.services.market_service import get_market_data, get_item_metadata, ensure_image_exists
from backend.utils.storage import load_watchlist
import concurrent.futures

monitor_bp = Blueprint('monitor', __name__)

def process_item(item):
    """Procesa un item individual para el monitor (se ejecutará en paralelo)"""
    # Soporte para la nueva estructura de objetos
    if isinstance(item, dict):
        item_url_name = item['url_name']
        rank = item.get('rank')
    else:
        item_url_name = item
        rank = None

    # Obtener datos de mercado (precio, volumen, tendencia)
    market_data = get_market_data(item_url_name, rank)
    
    # Obtener metadatos estáticos (nombre real, imagen, tags)
    metadata = get_item_metadata(item_url_name)
    
    # Gestionar imagen
    image_file = None
    if metadata.get('thumb'):
        image_file = ensure_image_exists(metadata['thumb'])
    
    # Combinar datos
    combined_data = {
        "url_name": item_url_name,
        "rank": rank,
        "name": metadata.get('item_name', item_url_name), # Usar nombre legible si existe
        "tags": metadata.get('tags', []),
        "image": image_file
    }

    if market_data.get('is_ranked'):
            combined_data.update({
            "is_ranked": True,
            "min_rank": market_data['min_rank'],
            "max_rank": market_data['max_rank'],
            "rank_min_stats": market_data['rank_0'],
            "rank_max_stats": market_data['rank_max'],
            # Valores por defecto para compatibilidad simple
            "price": market_data['rank_0']['price'] if market_data.get('rank_0') else 0,
            "trend": 0, 
            "volume": 0,
            "min_price": 0,
            "max_price": 0,
            "avg_price": 0
            })
    elif market_data.get('is_refined'):
        # Lógica para reliquias (Refined)
        # Usamos 'intact' como valor por defecto para la vista general
        refinements = market_data.get('refinements', [])
        default_ref = 'intact' if 'intact' in refinements else (refinements[0] if refinements else None)
        stats = market_data.get(default_ref) if default_ref else None
        
        combined_data.update({
            "is_refined": True,
            "refinements": refinements,
            "price": stats['price'] if stats else 0,
            "trend": stats['trend'] if stats else 0,
            "volume": stats['volume'] if stats else 0,
            "min_price": stats['min_price'] if stats else 0,
            "max_price": stats['max_price'] if stats else 0,
            "avg_price": stats['avg_price'] if stats else 0
        })
    else:
            combined_data.update({
            "is_ranked": False,
            "price": market_data.get('price', 0),
            "min_price": market_data.get('min_price', 0),
            "max_price": market_data.get('max_price', 0),
            "avg_price": market_data.get('avg_price', 0),
            "trend": market_data.get('trend', 0),
            "volume": market_data.get('volume', 0),
            })
    
    return combined_data

@monitor_bp.route('/api/monitor/batch', methods=['POST'])
def get_monitor_batch():
    """Obtiene datos de mercado para una lista específica de items (para historial reciente)"""
    data = request.json
    items_list = data.get('items', [])
    
    if not items_list:
        return jsonify([])
        
    results = []
    # Usar ThreadPoolExecutor para realizar peticiones en paralelo
    # Reducido a 3 workers para evitar saturar la API (Rate Limit 3req/s)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(process_item, items_list))
        
    return jsonify(results)

@monitor_bp.route('/api/monitor')
def get_monitor_data():
    items = load_watchlist()
    results = []
    
    # Usar ThreadPoolExecutor para realizar peticiones en paralelo
    # Reducido a 3 workers para evitar saturar la API
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(process_item, items))
        
    return jsonify(results)
