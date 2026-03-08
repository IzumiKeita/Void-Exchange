from flask import Blueprint, jsonify
from backend.services.ducats_service import get_ducats_data

ducats_bp = Blueprint('ducats', __name__)

@ducats_bp.route('/api/ducats', methods=['GET'])
def get_ducats():
    try:
        data = get_ducats_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
