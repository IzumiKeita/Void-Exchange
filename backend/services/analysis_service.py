import statistics
from backend.services.database_service import get_local_history
from datetime import datetime, timedelta

def calculate_slope(prices):
    """Calcula la pendiente de una regresión lineal simple (y = mx + b)"""
    n = len(prices)
    if n < 2:
        return 0
    x = list(range(n))
    y = prices
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)
    
    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    denominator = sum((xi - mean_x) ** 2 for xi in x)
    
    if denominator == 0:
        return 0
    return numerator / denominator

def analyze_item_profitability(url_name, variant='default'):
    """
    Realiza un análisis técnico sobre el historial de precios local.
    Retorna un diccionario con veredicto, score e indicadores.
    """
    # 1. Obtener datos (90 días para tener contexto suficiente para SMA30)
    history = get_local_history(url_name, variant, days=90)
    
    if not history or len(history) < 7:
        return {
            "status": "error",
            "message": "Insuficientes datos históricos (mínimo 7 días) para análisis. Visita el item más veces o espera a acumular historial."
        }

    # Extraer precios y volúmenes
    # Aseguramos que estén ordenados por fecha (get_local_history ya hace ORDER BY date ASC)
    prices = [h['avg_price'] for h in history]
    volumes = [h['volume'] for h in history]
    
    current_price = prices[-1]
    
    # 2. Calcular Indicadores
    # SMA (Simple Moving Average)
    sma_7 = statistics.mean(prices[-7:])
    sma_30 = statistics.mean(prices[-30:]) if len(prices) >= 30 else statistics.mean(prices)
    
    # Volatilidad (Desviación Estándar de los últimos 14 días)
    volatility = 0
    if len(prices) >= 2:
        subset = prices[-14:] if len(prices) >= 14 else prices
        volatility = statistics.stdev(subset)
    
    # Pendiente (Regresión Lineal de los últimos 7 días)
    slope = calculate_slope(prices[-7:])

    # 3. Lógica de Decisión (Score -100 a +100)
    # +100 = Compra Fuerte, -100 = Venta Fuerte
    score = 0
    reasons = []

    # A. Comparación con SMA 30 (Precio Histórico)
    diff_sma30 = 0
    if sma_30 > 0:
        diff_sma30 = (current_price - sma_30) / sma_30 * 100 
    
    if diff_sma30 < -15:
        score += 30
        reasons.append(f"Precio muy bajo ({current_price:.1f}) vs promedio mensual ({sma_30:.1f}).")
    elif diff_sma30 > 15:
        score -= 30
        reasons.append(f"Precio muy alto ({current_price:.1f}) vs promedio mensual ({sma_30:.1f}).")
    
    # B. Comparación con SMA 7 (Momentum Corto)
    diff_sma7 = 0
    if sma_7 > 0:
        diff_sma7 = (current_price - sma_7) / sma_7 * 100
    
    if diff_sma7 < -5:
        score += 10
        reasons.append("Caída reciente (potencial rebote).")
    elif diff_sma7 > 5:
        score -= 10
        reasons.append("Subida reciente (cuidado con corrección).")

    # C. Tendencia (Slope)
    if slope > 0.5:
        score -= 15 
        reasons.append(f"Tendencia alcista fuerte (+{slope:.2f}/día).")
    elif slope < -0.5:
        score += 15 
        reasons.append(f"Tendencia bajista fuerte ({slope:.2f}/día).")

    # D. Volumen
    avg_vol = statistics.mean(volumes[-7:])
    if avg_vol > 50:
        score += 10
        reasons.append("Alta liquidez.")
    elif avg_vol < 5:
        score -= 20
        reasons.append("Baja liquidez (difícil venta).")

    # 4. Generar Veredicto
    verdict = "NEUTRAL"
    color = "grey"
    
    if score >= 35:
        verdict = "COMPRA"
        color = "green"
    elif score <= -35:
        verdict = "VENTA"
        color = "red" # En frontend usaré clases de color, enviar string simple

    return {
        "status": "success",
        "analysis": {
            "verdict": verdict,
            "score": score,
            "color": color,
            "reasons": reasons,
            "metrics": {
                "current_price": round(current_price, 1),
                "sma_7": round(sma_7, 1),
                "sma_30": round(sma_30, 1),
                "volatility": round(volatility, 2),
                "slope": round(slope, 2)
            }
        }
    }
