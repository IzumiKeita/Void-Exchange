const API_URL = 'http://localhost:5001/api';

export const get_item_detail = async (url_name) => {
    try {
        console.log(`[API] Fetching item detail for: ${url_name}`);
        const response = await fetch(`${API_URL}/items/detail/${url_name}`);
        
        console.log(`[API] Response status: ${response.status}`);
        if (!response.ok) {
            const text = await response.text();
            console.error(`[API] Error response: ${text}`);
            throw new Error(`Server returned ${response.status}: ${text}`);
        }
        
        const data = await response.json();
        console.log("[API] Data received:", data);
        return data;
    } catch (error) {
        console.error('[API] Error fetching item detail:', error);
        return null;
    }
};

export const get_orders = async (url_name) => {
    try {
        const response = await fetch(`${API_URL}/items/orders/${url_name}`);
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error('[API] Error fetching orders:', error);
        return { payload: { orders: [] } };
    }
};

export const get_warframe_market_history = async (url_name) => {
    return { payload: { statistics_closed: { '90days': [] } } };
};
