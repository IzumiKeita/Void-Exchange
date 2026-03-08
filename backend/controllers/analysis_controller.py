from flask import Blueprint, jsonify, request
from backend.services.analysis_service import analyze_item_profitability

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/api/analysis/<url_name>')
def get_analysis(url_name):
    variant = request.args.get('variant', 'default')
    result = analyze_item_profitability(url_name, variant)
    return jsonify(result)
