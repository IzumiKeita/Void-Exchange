from flask import Blueprint, jsonify
from backend.services.void_trader_service import fetch_void_trader_data, get_baro_history

void_trader_bp = Blueprint('void_trader', __name__)

@void_trader_bp.route('/api/void-trader/current', methods=['GET'])
def get_current_inventory():
    """
    Obtiene el inventario actual de Baro Ki'Teer.
    Devuelve estado activo/inactivo, ubicación e items con precios de mercado.
    """
    try:
        data = fetch_void_trader_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@void_trader_bp.route('/api/void-trader/history', methods=['GET'])
def get_inventory_history():
    """
    Obtiene el historial de visitas e inventarios anteriores.
    """
    try:
        history = get_baro_history()
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
