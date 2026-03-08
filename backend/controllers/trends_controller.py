from flask import Blueprint, jsonify
from backend.services.trends_service import get_trends

trends_bp = Blueprint('trends', __name__)

@trends_bp.route('/api/trends')
def trends_index():
    data = get_trends()
    return jsonify(data)
