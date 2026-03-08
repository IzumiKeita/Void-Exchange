from flask import Blueprint, jsonify
from backend.services.vault_service import get_vault_status, get_vault_weapons_status

vault_bp = Blueprint('vault', __name__)

@vault_bp.route('/api/vault', methods=['GET'])
def get_vault():
    """
    Devuelve el estado de la Bóveda de Warframes (Active, Resurgence, Vaulted).
    """
    try:
        data = get_vault_status()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vault_bp.route('/api/vault/weapons', methods=['GET'])
def get_vault_weapons():
    """
    Devuelve el estado de la Bóveda de Armas (Active, Resurgence, Vaulted).
    """
    try:
        data = get_vault_weapons_status()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
