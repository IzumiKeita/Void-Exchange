import pytest

def test_live_feed_endpoint(client):
    """
    Prueba que el endpoint /api/live/feed responde correctamente (200 OK) y devuelve una lista.
    Valida también que la respuesta tenga la estructura esperada.
    """
    response = client.get('/api/live/feed')
    
    # Verificar estado 200
    assert response.status_code == 200, f"Falló con status: {response.status_code}"
    
    data = response.json
    
    # Verificar que devuelve una lista
    assert isinstance(data, list), "El endpoint debería devolver una lista JSON"
    
    # Nota: Puede estar vacía si falla la API externa o no hay trends, 
    # pero no debería dar error 500.
    
    # Si devuelve datos, verificamos la estructura del primer elemento
    if len(data) > 0:
        item = data[0]
        required_fields = ['id', 'item_name', 'platinum', 'order_type', 'user']
        for field in required_fields:
            assert field in item, f"Falta el campo '{field}' en la respuesta"
