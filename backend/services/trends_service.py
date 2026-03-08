import json
import os
import time
import threading
import requests
import concurrent.futures
from backend.services.market_service import get_all_items, get_item_metadata, ensure_image_exists

TRENDS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'trends.json')
UPDATING = False
LAST_UPDATE = 0
UPDATE_INTERVAL = 300  # 5 minutes

def load_trends():
    if os.path.exists(TRENDS_FILE):
        try:
            with open(TRENDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_trends(trends):
    os.makedirs(os.path.dirname(TRENDS_FILE), exist_ok=True)
    with open(TRENDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(trends, f, ensure_ascii=False, indent=2)

def fetch_item_volume(item):
    """
    Fetches volume for a single item.
    Returns (slug, sell_volume, buy_volume)
    """
    slug = item.get('url_name')
    url = f"https://api.warframe.market/v1/items/{slug}/statistics"
    headers = {
        'Platform': 'pc', 
        'Language': 'es',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Enforce minimum delay to respect 3 req/s limit
    # Sleeping 0.35s ensures we never exceed ~2.8 req/s per thread
    time.sleep(0.35)

    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Get 48hours stats from LIVE statistics (Open Orders) to distinguish Sell vs Buy
                # statistics_closed (Completed Trades) does not have order_type
                stats = data.get('payload', {}).get('statistics_live', {}).get('48hours', [])
                
                if not stats:
                     # Fallback to 90days if 48hours is empty
                     stats = data.get('payload', {}).get('statistics_live', {}).get('90days', [])

                if stats:
                    # Filter by order type
                    sell_stats = [s for s in stats if s.get('order_type') == 'sell']
                    buy_stats = [s for s in stats if s.get('order_type') == 'buy']

                    # Calculate "Volume" score (sum of average volume over last 24 points)
                    # For live stats, volume is the number of open orders/items.
                    # Summing them gives a magnitude of supply/demand over the last day.
                    sell_volume = sum(s.get('volume', 0) for s in sell_stats[-24:])
                    buy_volume = sum(s.get('volume', 0) for s in buy_stats[-24:])
                    
                    return slug, sell_volume, buy_volume
                return slug, 0, 0
                
            elif response.status_code == 429:
                # Rate limit exceeded
                wait_time = 5 * (attempt + 1)
                print(f"Rate limit hit for {slug}. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue # Retry
                
            else:
                # Other error
                return slug, 0, 0

        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
                continue
            return slug, 0, 0
    
    return slug, 0, 0

def update_trends_logic():
    global UPDATING, LAST_UPDATE
    if UPDATING:
        return
    
    UPDATING = True
    print("Iniciando actualización de tendencias...")
    
    try:
        items = get_all_items()
        
        target_items = []
        for i in items:
            slug = i.get('url_name', '')
            tags = i.get('tags', [])
            
            # Incluir Sets, Mods, Arcanos y Reliquias
            if slug.endswith('_set'):
                target_items.append(i)
            elif 'mod' in tags:
                target_items.append(i)
            elif 'arcane_enhancement' in tags:
                target_items.append(i)
            elif 'relic' in tags:
                target_items.append(i)
        
        # Load previous trends to compare ranks
        prev_data = load_trends()
        prev_ranks_sell = {}
        prev_ranks_buy = {}
        
        if isinstance(prev_data, dict):
            for item in prev_data.get('sell', []):
                prev_ranks_sell[item['url_name']] = item['rank']
            for item in prev_data.get('buy', []):
                prev_ranks_buy[item['url_name']] = item['rank']
        elif isinstance(prev_data, list):
            for item in prev_data:
                prev_ranks_sell[item['url_name']] = item['rank']
        
        results = []
        processed_count = 0
        
        # Usamos max_workers=1 para respetar estrictamente el rate limit de 3 req/s
        # y evitar baneos (429 Too Many Requests).
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            # Future to item map
            future_to_item = {executor.submit(fetch_item_volume, item): item for item in target_items}
            
            for future in concurrent.futures.as_completed(future_to_item):
                slug, sell_vol, buy_vol = future.result()
                if sell_vol > 0 or buy_vol > 0:
                    results.append((slug, sell_vol, buy_vol))
                
                processed_count += 1
                
                # Feedback inmediato: Guardar frecuentemente al inicio, luego cada 50
                if (processed_count <= 100 and processed_count % 5 == 0) or processed_count % 50 == 0:
                    print(f"Progreso tendencias: {processed_count}/{len(target_items)} items procesados...")
                    save_partial_trends(results, prev_ranks_sell, prev_ranks_buy)
                
        # Guardado final
        save_partial_trends(results, prev_ranks_sell, prev_ranks_buy)
        
        LAST_UPDATE = time.time()
        print("Tendencias actualizadas con éxito (Final).")
        
    except Exception as e:
        print(f"Error actualizando tendencias: {e}")
    finally:
        UPDATING = False

def save_partial_trends(results, prev_ranks_sell, prev_ranks_buy):
    sell_results = sorted([(r[0], r[1]) for r in results if r[1] > 0], key=lambda x: x[1], reverse=True)
    buy_results = sorted([(r[0], r[2]) for r in results if r[2] > 0], key=lambda x: x[1], reverse=True)

    def build_trend_list(sorted_items, prev_ranks):
        trend_list = []
        for index, (slug, volume) in enumerate(sorted_items):
            rank = index + 1
            prev_rank = prev_ranks.get(slug)
            
            trend = 'same'
            if prev_rank:
                if rank < prev_rank:
                    trend = 'up'
                elif rank > prev_rank:
                    trend = 'down'
            else:
                trend = 'new'
            
            meta = get_item_metadata(slug)
            
            # Asegurar imagen local
            thumb_local = None
            if meta.get('thumb'):
                thumb_local = ensure_image_exists(meta['thumb'])
            
            trend_list.append({
                "rank": rank,
                "url_name": slug,
                "item_name": meta.get('item_name', slug),
                "thumb": thumb_local,
                "tags": meta.get('tags', []),
                "volume": volume,
                "trend": trend,
                "prev_rank": prev_rank
            })
        return trend_list

    new_trends = {
        "sell": build_trend_list(sell_results, prev_ranks_sell),
        "buy": build_trend_list(buy_results, prev_ranks_buy)
    }
        
    save_trends(new_trends)

def start_background_update():
    thread = threading.Thread(target=update_trends_logic)
    thread.daemon = True
    thread.start()

def get_trends():
    # Trigger update if needed
    if time.time() - LAST_UPDATE > UPDATE_INTERVAL and not UPDATING:
        start_background_update()
    
    return load_trends()
