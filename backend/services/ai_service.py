import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la API Key
# Se asume que la variable de entorno GEMINI_API_KEY está configurada
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def analizar_tendencias(datos):
    """
    Analiza los datos de mercado de Warframe y devuelve una recomendación.
    
    Args:
        datos (dict): Un diccionario con los datos del mercado. 
                      Se espera que contenga claves como 'precio_minimo', 
                      'precio_promedio', 'volumen', 'tendencia', etc.
                      
    Returns:
        str: Recomendación (COMPRAR, VENDER, ESPERAR) o un mensaje de error.
    """
    if not API_KEY:
        return "Error: API Key de Google Generative AI no configurada. Asegúrate de configurar la variable de entorno GEMINI_API_KEY."

    try:
        # Configuración del modelo
        # Usamos gemini-flash-latest para asegurar acceso al modelo rápido más reciente y estable.
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""
        Actúa como un experto trader en el mercado de Warframe (Warframe Market).
        Analiza los siguientes datos de un objeto:
        {json.dumps(datos, indent=2)}
        
        Basándote en estos datos (precio mínimo actual, promedio, volumen, tendencia),
        dame una recomendación CORTA y DIRECTA.
        
        Las posibles recomendaciones son:
        - COMPRAR: Si el precio actual está significativamente por debajo del promedio y hay volumen.
        - VENDER: Si el precio está alto respecto al promedio.
        - ESPERAR: Si el mercado es incierto o el volumen es muy bajo.
        
        Tu respuesta debe ser solo la recomendación seguida de una explicación muy breve (una frase).
        Ejemplo: "COMPRAR: Precio muy por debajo del promedio."
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        return f"Error al analizar tendencias: {str(e)}"

def chat_trading(mensaje, historial=None, context=None):
    """
    Procesa un mensaje de chat actuando como experto en trading de Warframe.
    """
    if not API_KEY:
        print("DEBUG: API Key no encontrada en variables de entorno")
        return "Error de configuración: API Key no encontrada. Revisa el archivo .env."

    try:
        # Asegurar que el historial es una lista válida
        history_data = historial if isinstance(historial, list) else []
        
        # Filtrar historial para asegurar formato correcto si es necesario
        # Gemini espera: [{'role': 'user'|'model', 'parts': [...]}, ...]
        valid_history = []
        for entry in history_data:
            if isinstance(entry, dict) and 'role' in entry and 'parts' in entry:
                valid_history.append(entry)

        # Construir instrucciones del sistema
        base_instruction = """Eres un experto comerciante (trader) de Warframe. 
        Tu objetivo es ayudar a los jugadores a ganar platino, identificar estafas, 
        entender el mercado y optimizar sus intercambios.
        
        Reglas:
        1. SOLO responde preguntas relacionadas con Warframe, trading, precios, farmeo de reliquias y economía del juego.
        2. Si te preguntan de otro tema, responde amablemente que solo puedes hablar de Warframe Market.
        3. Sé conciso, directo y usa terminología del juego (Platino, Ducados, Vault, Sets).
        4. No inventes precios. Si no sabes un precio específico, sugiere buscarlo en warframe.market.
        """

        if context:
            context_type = context.get('type', 'item') # Default to item for backward compatibility
            
            if context_type == 'dashboard':
                base_instruction += f"""
                
                CONTEXTO ACTUAL DEL USUARIO (DASHBOARD):
                El usuario está viendo el panel principal (Dashboard).
                Filtro actual: {context.get('filter', 'Todos')}
                Ordenamiento: {context.get('sort', 'Ninguno')}
                
                Ítems destacados visibles en pantalla (Top 5):
                {json.dumps(context.get('top_items', []), indent=2)}
                
                Si el usuario pregunta "¿qué compro?" o "¿qué está bajando?", usa la lista de ítems destacados visibles para sugerir opciones.
                Si el ordenamiento es por "Bajada" (trend_asc), los ítems mostrados son los que más han bajado de precio.
                Si el ordenamiento es por "Subida" (trend_desc), son los que más han subido.
                """
            else:
                # Asumimos contexto de ítem individual
                base_instruction += f"""
                
                CONTEXTO ACTUAL DEL USUARIO (ITEM):
                El usuario está viendo actualmente la página de un ítem específico. Usa estos datos para responder:
                Nombre: {context.get('item', {}).get('name') or context.get('name')}
                Descripción: {context.get('item', {}).get('description') or context.get('description')}
                Estado: {'Vaulted (No obtenible en juego)' if context.get('item', {}).get('is_vaulted') else 'Disponible'} {'(Prime Resurgence Activo)' if context.get('item', {}).get('is_resurgence') else ''}
                Estadísticas (48h): {json.dumps(context.get('item', {}).get('stats') or context.get('stats'), indent=2)}
                Tendencia Reciente (Últimos días): {json.dumps(context.get('trend_history_90d_snapshot'), indent=2)}
                Resumen de Órdenes: {json.dumps(context.get('orders_summary'), indent=2)}
                
                Si el usuario pregunta "¿está buen precio?" o "¿debo comprar?", usa las estadísticas provistas y la TENDENCIA RECIENTE para dar una opinión fundamentada.
                Analiza si el precio está subiendo o bajando en los últimos días según el historial proporcionado. Considera si es Vaulted (suele subir de precio) o si está en Resurgence (suele bajar).
                """

        # Configuración del modelo
        model = genai.GenerativeModel('gemini-flash-latest', system_instruction=base_instruction)
        
        chat = model.start_chat(history=valid_history)
        response = chat.send_message(mensaje)
        return response.text.strip()
        
    except Exception as e:
        print(f"DEBUG: Error en chat_trading: {str(e)}")
        return f"Error interno de IA: {str(e)}"
