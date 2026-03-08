from flask import Blueprint, jsonify, request, send_from_directory
from backend.services.market_service import get_all_items, get_image_path, get_full_item_details, ensure_image_exists, get_item_orders
from backend.utils.storage import add_item, remove_item
import os

items_bp = Blueprint('items', __name__)

@items_bp.route('/api/items')
def list_items():
    items = get_all_items()
    return jsonify(items)

@items_bp.route('/api/items/orders/<url_name>')
def get_orders(url_name):
    orders = get_item_orders(url_name)
    return jsonify(orders)

@items_bp.route('/api/items/detail/<url_name>')
def get_item_detail(url_name):
    details = get_full_item_details(url_name)
    if details:
        return jsonify(details)
    return jsonify({"error": "Item not found"}), 404

@items_bp.route('/api/images/<path:filename>')
def serve_image(filename):
    # Asegurar que la imagen existe (descargar si es necesario)
    # ensure_image_exists descarga la imagen en la carpeta raíz de images (aplanada)
    # y devuelve solo el nombre del archivo (basename)
    local_filename = ensure_image_exists(filename)
    
    if not local_filename:
        return "Image not found", 404
    
    # Obtenemos el directorio base donde están las imágenes
    # Usamos get_image_path con el nombre de archivo local (aplanado)
    full_path = get_image_path(local_filename)
    directory = os.path.dirname(full_path)
    return send_from_directory(directory, local_filename)

@items_bp.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist():
    data = request.json
    item_url_name = data.get('url_name')
    rank = data.get('rank')
    if item_url_name:
        add_item(item_url_name, rank)
        return jsonify({"success": True, "message": "Item added"})
    return jsonify({"success": False, "message": "Invalid item"}), 400

@items_bp.route('/api/watchlist/remove', methods=['POST'])
def remove_from_watchlist():
    data = request.json
    item_url_name = data.get('url_name')
    rank = data.get('rank')
    if item_url_name:
        remove_item(item_url_name, rank)
        return jsonify({"success": True, "message": "Item removed"})
    return jsonify({"success": False, "message": "Invalid item"}), 400
