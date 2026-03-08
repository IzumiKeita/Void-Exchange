from flask import Blueprint, jsonify, request
from backend.services.ai_service import chat_trading

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/api/ai/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        mensaje = data.get('message')
        historial = data.get('history', [])
        context = data.get('context')
        
        print(f"Chat request received: {mensaje}") # Debug log
        
        if not mensaje:
            return jsonify({'error': 'Mensaje requerido'}), 400
            
        respuesta = chat_trading(mensaje, historial, context)
        return jsonify({'response': respuesta})
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': f"Internal Server Error: {str(e)}"}), 500
