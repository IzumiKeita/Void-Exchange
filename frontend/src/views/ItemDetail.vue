<template>
    <div class="item-detail-container">
        <!-- Loading State -->
        <div v-if="loading" class="loading-container">
            <div class="spinner"></div>
            <p>{{ t('itemDetail.loading') }}</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="error-container">
            <h3>{{ t('common.error') }}</h3>
            <p>{{ error }}</p>
            <button @click="retryLoad" class="retry-btn">{{ t('common.retry') }}</button>
        </div>

        <!-- Content -->
        <div v-else-if="item" class="content-wrapper">
            <!-- Header Section -->
            <div class="item-header">
                <div class="item-image">
                    <img :src="getFullImageUrl(item.thumb)" :alt="item.item_name" @error="handleImageError">
                </div>
                <div class="item-info">
                    <h1>{{ item.item_name }}</h1>
                    <div class="tags">
                        <span class="tag mastery" v-if="item.mastery_level">MR {{ item.mastery_level }}</span>
                        <span class="tag type">{{ item.item_type }}</span> <!-- Fixed: usage of item.item_type -->
                        <span class="tag vaulted" v-if="item.is_vaulted">{{ t('itemDetail.tags.vaulted') }}</span>
                        <span class="tag resurgence" v-if="item.is_resurgence">{{ t('itemDetail.tags.resurgence') }}</span>
                    </div>
                    <p class="description" v-html="formattedDescription"></p>
                    
                    <!-- Stats Grid -->
                    <div class="stats-grid">
                        <div class="stat-card">
                            <span class="label">{{ t('itemDetail.stats.minPrice') }}</span>
                            <span class="value">{{ marketStats.min_price }} <span class="plat-text">Pt</span></span>
                        </div>
                        <div class="stat-card">
                            <span class="label">{{ t('itemDetail.stats.avgPrice') }}</span>
                            <span class="value">{{ marketStats.avg_price }} <span class="plat-text">Pt</span></span>
                        </div>
                        <div class="stat-card" v-if="item.ducats">
                            <span class="label">{{ t('itemDetail.stats.ducats') }}</span>
                            <span class="value">{{ item.ducats }} <span class="ducat-text">Ducats</span></span>
                        </div>
                        <div class="stat-card">
                            <span class="label">{{ t('itemDetail.stats.volume') }}</span>
                            <span class="value">{{ marketStats.volume }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Historical Data Chart (TEMPORARILY DISABLED) -->
            <div class="chart-section">
                <div class="chart-controls">
                    <h3>{{ t('itemDetail.chart.title') }}</h3>
                    <div class="controls-group">
                        <div class="rank-filters" v-if="availableRanks.length > 0">
                            <button 
                                v-for="r in availableRanks" 
                                :key="r"
                                :class="{ active: selectedGraphRank === r }"
                                @click="selectedGraphRank = r"
                            >
                                {{ r === item.max_rank ? t('itemDetail.chart.maxRank', {rank: r}) : t('itemDetail.chart.rank', {rank: r}) }}
                            </button>
                        </div>
                        <div class="time-filters">
                            <button 
                                v-for="period in ['90d', '48h', '24h']" 
                                :key="period"
                                :class="{ active: selectedPeriod === period }"
                                @click="selectedPeriod = period"
                            >
                                {{ t('itemDetail.chart.periods.' + period) }}
                            </button>
                        </div>
                    </div>
                </div>
                <div class="chart-container">
                    <!-- Debug Info (Visible only if issues persist) -->
                    <div v-if="historyData['90d'] && historyData['90d'].length > 0" style="font-size: 10px; color: #666; display:none;">
                        Datos: {{ historyData['90d'].length }} puntos
                    </div>

                    <apexchart 
                        v-if="chartSeries.length > 0"
                        width="100%" 
                        height="350" 
                        :type="chartOptions.chart.type" 
                        :options="chartOptions" 
                        :series="chartSeries"
                    ></apexchart>
                    <div v-else class="no-data-chart">
                        {{ t('itemDetail.chart.noData') }} ({{ historyData['90d'] ? historyData['90d'].length : 0 }})
                    </div>
                </div>
            </div>

            <!-- Orders Table -->
            <div class="orders-section">
                <div class="orders-column">
                    <h3>{{ t('itemDetail.orders.sellers') }}</h3>
                    <div class="orders-list">
                        <div v-for="order in visibleSellOrders" :key="order.id" class="order-card sell">
                            <div class="user-info">
                                <span class="status-dot" :class="order.user.status"></span>
                                <span class="username">{{ order.user.ingame_name }}</span>
                                <span class="rep">{{ t('itemDetail.orders.reputation', {rep: order.user.reputation}) }}</span>
                            </div>
                            <div class="order-details">
                                <span class="quantity">{{ t('itemDetail.orders.quantity', {qty: order.quantity}) }}</span>
                                <span class="price">{{ order.platinum }} <span class="plat-text">Pt</span></span>
                            </div>
                            <button class="whisper-btn" @click="copyWhisper(order.whisper)">
                                <span>{{ t('itemDetail.orders.whisper') }}</span>
                            </button>
                        </div>
                    </div>
                </div>

                <div class="orders-column">
                    <h3>{{ t('itemDetail.orders.buyers') }}</h3>
                    <div class="orders-list">
                        <div v-for="order in visibleBuyOrders" :key="order.id" class="order-card buy">
                            <div class="user-info">
                                <span class="status-dot" :class="order.user.status"></span>
                                <span class="username">{{ order.user.ingame_name }}</span>
                                <span class="rep">{{ t('itemDetail.orders.reputation', {rep: order.user.reputation}) }}</span>
                            </div>
                            <div class="order-details">
                                <span class="quantity">{{ t('itemDetail.orders.quantity', {qty: order.quantity}) }}</span>
                                <span class="price">{{ order.platinum }} <span class="plat-text">Pt</span></span>
                            </div>
                            <button class="whisper-btn" @click="copyWhisper(order.whisper)">
                                <span>{{ t('itemDetail.orders.whisper') }}</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { get_item_detail, get_orders, get_warframe_market_history } from '../services/api';
import { useI18n } from '../i18n';
import axios from 'axios';

const { t } = useI18n();

const route = useRoute();
const loading = ref(true);
const error = ref(null);
const item = ref(null);
const orders = ref({ buy: [], sell: [] });
const historyData = ref({}); // Stores processed history data for chart
const rawHistory = ref(null); // Stores full raw history object
const availableRanks = ref([]); // Stores available ranks (e.g. [0, 10])
const selectedPeriod = ref('90d'); // '90d' or '48h'
const selectedGraphRank = ref(0); // For mod ranks

// Helper to process history data based on selected rank
const processHistoryData = () => {
    if (!rawHistory.value) return;
    
    // Helper to extract data from a period result
    const extractData = (periodResult) => {
        if (!periodResult) return [];
        if (periodResult.general) return periodResult.general;
        if (periodResult.ranks) {
            // Use selectedGraphRank
            const r = selectedGraphRank.value;
            // Check if rank exists in this period's ranks (loose comparison for key)
            if (periodResult[`rank_${r}`]) {
                 return periodResult[`rank_${r}`];
            }
            // Fallback: try to find any rank if selected is missing (shouldn't happen if availableRanks is correct)
            return [];
        }
        if (periodResult.refinements) {
             return periodResult[periodResult.refinements[0]] || []; 
        }
        return [];
    };

    const data90d = extractData(rawHistory.value['90d']);
    const data48h = extractData(rawHistory.value['48h']);

    historyData.value = {
        '90d': data90d.map(p => ({
            datetime: p.datetime,
            avg_price: p.avg_price,
            min_price: p.min_price,
            max_price: p.max_price,
            open_price: p.open_price,
            closed_price: p.closed_price,
            volume: p.volume
        })),
        '48h': data48h.map(p => ({
            datetime: p.datetime,
            avg_price: p.avg_price,
            min_price: p.min_price,
            max_price: p.max_price,
            open_price: p.open_price,
            closed_price: p.closed_price,
            volume: p.volume
        }))
    };
};

// Watch for rank changes
watch(selectedGraphRank, () => {
    processHistoryData();
});

// Stats computed from history
const marketStats = computed(() => {
    // Priority: item.value?.stats (48h cache from backend)
    if (item.value?.stats && !item.value.stats.is_ranked) {
        const s = item.value.stats;
        return {
            min_price: s.min_price?.toFixed(0) || 'N/A',
            avg_price: s.avg_price?.toFixed(0) || s.price?.toFixed(0) || 'N/A',
            volume: s.volume || '0'
        };
    } else if (item.value?.stats?.is_ranked) {
        // Dynamic rank selection for summary stats
        const r = selectedGraphRank.value;
        const s = item.value.stats[`rank_${r}`] || item.value.stats.rank_0 || item.value.stats;
        return {
            min_price: s.min_price?.toFixed(0) || 'N/A',
            avg_price: s.avg_price?.toFixed(0) || s.price?.toFixed(0) || 'N/A',
            volume: s.volume || '0'
        };
    }

    if (!historyData.value || !historyData.value['90d'] || historyData.value['90d'].length === 0) {
        return { min_price: 'N/A', avg_price: 'N/A', volume: 'N/A' };
    }
    const latest = historyData.value['90d'][historyData.value['90d'].length - 1];
    return {
        min_price: latest.min_price?.toFixed(0) || 'N/A',
        avg_price: latest.avg_price?.toFixed(0) || 'N/A',
        volume: latest.volume || '0'
    };
});

const chartOptions = computed(() => ({
    chart: {
        type: 'candlestick',
        height: 350,
        toolbar: { show: false },
        zoom: { enabled: false },
        background: 'transparent'
    },
    colors: ['#00e676', '#4ecdc4', '#ff9800'],
    stroke: { 
        width: [1, 0, 2],
        dashArray: [0, 0, 5] // Dashed line for trend
    },
    dataLabels: { enabled: false },
    theme: { mode: 'dark' },
    xaxis: {
        type: 'datetime',
        tooltip: { enabled: false },
        axisBorder: { show: false },
        axisTicks: { show: false }
    },
    yaxis: [
        {
            seriesName: 'Precio',
            labels: { 
                formatter: (val) => `${val.toFixed(0)} Pt`,
                style: { colors: '#00e676' }
            },
            tooltip: { enabled: true },
            forceNiceScale: true, // Asegura escalas limpias
            min: (min) => Math.floor(min * 0.95), // 5% de margen inferior
            max: (max) => Math.ceil(max * 1.05)   // 5% de margen superior
        },
        {
            seriesName: 'Volumen',
            opposite: true,
            labels: { 
                formatter: (val) => `${val.toFixed(0)}`,
                style: { colors: '#4ecdc4' }
            },
        },
        {
            seriesName: 'Tendencia',
            show: false, // Hide axis
            // Sincronizar escala con Precio manualmente (best effort)
            min: (min) => Math.floor(min * 0.95),
            max: (max) => Math.ceil(max * 1.05)
        }
    ],
    grid: {
        borderColor: '#444',
        strokeDashArray: 4
    },
    plotOptions: {
        candlestick: {
            colors: {
                upward: '#00e676',
                downward: '#ff1744'
            }
        },
        bar: {
            columnWidth: '50%',
            colors: {
                ranges: [{
                    from: 0,
                    to: 1000000,
                    color: 'rgba(78, 205, 196, 0.3)'
                }]
            }
        }
    }
}));

const chartSeries = computed(() => {
    let data = [];
    if (selectedPeriod.value === '24h') {
        const full48h = historyData.value['48h'] || [];
        // Slice last 24 hours if available, otherwise take all
        data = full48h.slice(-24);
    } else {
        data = historyData.value[selectedPeriod.value] || [];
    }
    
    if (data.length === 0) return [];

    // Calculate Trend (Linear Regression)
    let trendData = [];
    if (data.length > 1) {
        let subsetSize, startIndex;

        if (selectedPeriod.value === '90d') {
            // For 90d: Use only the last 40% of data points for trend calculation to reflect recent momentum
            // Or at least the last 14 points if available, to avoid long-term drag
            subsetSize = Math.max(14, Math.floor(data.length * 0.4));
            startIndex = Math.max(0, data.length - subsetSize);
        } else {
            // For 48h and 24h: Use the FULL dataset so the line spans the entire chart
            subsetSize = data.length;
            startIndex = 0;
        }
        
        const points = data.slice(startIndex).map((p, i) => ({ 
            x: i, // Relative index within the subset
            y: p.avg_price, 
            time: new Date(p.datetime).getTime(),
            originalIndex: startIndex + i
        }));

        let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
        const n = points.length;

        points.forEach(p => {
            sumX += p.x;
            sumY += p.y;
            sumXY += p.x * p.y;
            sumX2 += p.x * p.x;
        });

        const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        const intercept = (sumY - slope * sumX) / n;

        // Determine time step for projection
        const lastTime = points[n-1].time;
        // Estimate average time step from the subset
        const avgTimeStep = (lastTime - points[0].time) / (n - 1);
        
        // Generate trend points ONLY for the subset + projection
        const projectionSteps = 5; 
        
        for (let i = 0; i < n + projectionSteps; i++) {
            const y = slope * i + intercept;
            let time;
            if (i < n) {
                time = points[i].time;
            } else {
                time = lastTime + (avgTimeStep * (i - n + 1));
            }
            trendData.push({ x: time, y: parseFloat(y.toFixed(1)) });
        }
    }

    return [
        {
            name: 'Precio',
            type: 'candlestick',
            data: data.map(p => ({
                x: new Date(p.datetime).getTime(),
                y: [p.open_price, p.max_price, p.min_price, p.closed_price]
            }))
        },
        {
            name: 'Volumen',
            type: 'bar',
            data: data.map(p => ({
                x: new Date(p.datetime).getTime(),
                y: p.volume
            }))
        },
        {
            name: 'Tendencia',
            type: 'line',
            data: trendData
        }
    ];
});

// Description formatting
const formattedDescription = computed(() => {
    if (!item.value?.description) return 'Sin descripción disponible.';
    return item.value.description.replace(/\n/g, '<br>');
});

// Filter orders
const visibleSellOrders = computed(() => {
    return (orders.value?.sell || []).slice(0, 10);
});

const visibleBuyOrders = computed(() => {
    return (orders.value?.buy || []).slice(0, 10);
});

// Image helper
const getFullImageUrl = (thumb) => {
    if (!thumb) return '/placeholder.png';
    if (thumb.startsWith('http')) return thumb;
    return `https://warframe.market/static/assets/${thumb}`;
};

const handleImageError = (e) => {
    e.target.src = '/placeholder.png';
};

// Data Fetching
const loadData = async () => {
    const urlName = route.params.id;
    if (!urlName) return;

    loading.value = true;
    error.value = null;

    try {
        console.log("Cargando datos para:", urlName);
        
        // 1. Fetch Item Details
        const detailResponse = await get_item_detail(urlName);
        console.log("Detalle recibido:", detailResponse);
        
        // Manejar estructura de respuesta (API directa vs Backend propio)
        if (detailResponse?.payload?.item) {
            if (detailResponse.payload.item.items_in_set) {
                const actualItem = detailResponse.payload.item.items_in_set.find(i => i.url_name === urlName);
                item.value = actualItem || detailResponse.payload.item.items_in_set[0];
            } else {
                item.value = detailResponse.payload.item;
            }
        } else {
            // Estructura simplificada del backend
            item.value = detailResponse;
        }

        if (!item.value) throw new Error("No se pudo cargar la información del ítem");

        // 2. Fetch Orders
        const ordersResponse = await get_orders(urlName);
        if (ordersResponse?.payload?.orders) {
            const allOrders = ordersResponse.payload.orders;
            orders.value = {
                sell: allOrders.filter(o => o.order_type === 'sell' && o.user.status !== 'offline').sort((a,b) => a.platinum - b.platinum),
                buy: allOrders.filter(o => o.order_type === 'buy' && o.user.status !== 'offline').sort((a,b) => b.platinum - a.platinum)
            };
        } else if (ordersResponse?.sell || ordersResponse?.buy) {
            // Estructura simplificada del backend ({ sell: [], buy: [] })
            orders.value = ordersResponse;
        } else {
            orders.value = ordersResponse;
        }

        // 3. Process History (from Detail Response)
        if (item.value?.history) {
            rawHistory.value = item.value.history;
            
            // Detect ranks from 90d data
            if (rawHistory.value['90d']?.ranks) {
                // Get all available ranks keys (e.g. [0, 10])
                availableRanks.value = rawHistory.value['90d'].ranks.sort((a,b) => a - b);
                
                // Default to 0 if available, else first one
                if (availableRanks.value.includes(0)) selectedGraphRank.value = 0;
                else if (availableRanks.value.length > 0) selectedGraphRank.value = availableRanks.value[0];
            } else {
                availableRanks.value = [];
            }
            
            processHistoryData();
            
            console.log("Historial cargado:", { 
                '90d': historyData.value['90d'].length, 
                '48h': historyData.value['48h'].length 
            });
        }

        // Fallback: Fetch directly if still empty (though api.js is stubbed currently)
        if (!historyData.value['90d'] || historyData.value['90d'].length === 0) {
            try {
                const historyResponse = await get_warframe_market_history(urlName);
            if (historyResponse?.payload?.statistics_closed) {
                // Process 90days
                const stats90 = historyResponse.payload.statistics_closed['90days'] || [];
                historyData.value['90d'] = stats90.map(p => ({
                    datetime: p.datetime,
                    avg_price: p.avg_price,
                    min_price: p.min_price,
                    max_price: p.max_price,
                    open_price: p.open_price,
                    closed_price: p.closed_price,
                    volume: p.volume
                }));
            }
        } catch (hErr) {
            console.warn("Error cargando historial (no crítico):", hErr);
        }
        }

    } catch (e) {
        console.error("Error fatal cargando item:", e);
        error.value = `Error cargando datos: ${e.message}`;
    } finally {
        loading.value = false;
    }
};

const retryLoad = () => {
    loadData();
};

const copyWhisper = (text) => {
    navigator.clipboard.writeText(text);
    alert("Mensaje copiado al portapapeles");
};

// --- CHAT CONTEXT LOGIC ---
const updateChatContext = () => {
    if (!item.value) return;
    
    try {
        // Get recent trend snapshot (last 5 entries from 90d history)
        const trendSnapshot = (historyData.value['90d'] || []).slice(-5).map(p => ({
            date: new Date(p.datetime).toLocaleDateString(),
            avg: p.avg_price,
            vol: p.volume
        }));

        const context = {
            item: {
                name: item.value.item_name || item.value.en?.item_name || 'Unknown Item',
                id: item.value.id,
                url_name: item.value.url_name,
                description: item.value.description, // Added description
                is_vaulted: item.value.is_vaulted || false, // Added vaulted status
                is_resurgence: item.value.is_resurgence || false, // Added resurgence status
                stats: {
                    current_view: marketStats.value,
                    mod_ranks: item.value.stats?.is_ranked ? {
                        rank_0: item.value.stats.rank_0,
                        rank_max: item.value.stats.rank_max,
                        max_rank_level: item.value.stats.max_rank
                    } : null
                }
            },
            trend_history_90d_snapshot: trendSnapshot, // Added trend snapshot
            orders_summary: {
                sell_min: marketStats.value.min_price,
                sell_avg: marketStats.value.avg_price,
                volume: marketStats.value.volume,
                top_sellers: visibleSellOrders.value.slice(0, 3).map(o => ({
                    user: o.user.ingame_name,
                    price: o.platinum,
                    quantity: o.quantity,
                    rank: o.mod_rank // Include rank if available in order
                }))
            }
        };
        sessionStorage.setItem('activeItemContext', JSON.stringify(context));
        // console.log("Chat context updated:", context.item.name);
    } catch (e) {
        console.warn("Error updating chat context:", e);
    }
};

watch([item, orders, selectedGraphRank], () => {
    updateChatContext();
}, { deep: true });

// Lifecycle
onMounted(() => {
    loadData();
});

watch(() => route.params.id, (newId) => {
    if (newId) loadData();
});
</script>

<style scoped>
.item-detail-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    color: #e0e0e0;
}

.loading-container, .error-container {
    text-align: center;
    padding: 50px;
}

.item-header {
    display: flex;
    gap: 30px;
    margin-bottom: 40px;
    background: #1e1e1e;
    padding: 20px;
    border-radius: 12px;
}

.item-image img {
    max-width: 200px;
    border-radius: 8px;
    border: 2px solid #333;
}

.item-info h1 {
    font-size: 2.5rem;
    margin: 0 0 10px 0;
    color: #fff;
}

.tags {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.tag {
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 0.9rem;
    font-weight: bold;
}

.tag.mastery { background: #d32f2f; color: white; }
.tag.type { background: #1976d2; color: white; }
.tag.vaulted { background: #3e2723; color: #ffab91; border: 1px solid #ff5722; }
.tag.resurgence { background: #311b92; color: #e1bee7; border: 1px solid #d500f9; }

.description {
    line-height: 1.6;
    color: #aaa;
    margin-bottom: 20px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.stat-card {
    background: #2a2a2a;
    padding: 15px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stat-card .label {
    font-size: 0.9rem;
    color: #888;
    margin-bottom: 5px;
}

.stat-card .value {
    font-size: 1.2rem;
    font-weight: bold;
    display: flex;
    align-items: center;
    gap: 5px;
}

.ducat-text {
    color: #ffd700;
    font-size: 0.9rem;
    font-weight: normal;
}

.plat-icon {
    width: 20px;
    height: 20px;
}

.orders-section {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    margin-top: 30px;
}

.orders-column h3 {
    border-bottom: 2px solid #333;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

.order-card {
    background: #1e1e1e;
    padding: 15px;
    margin-bottom: 10px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.order-card.sell { border-left: 4px solid #4caf50; }
.order-card.buy { border-left: 4px solid #2196f3; }

.user-info {
    display: flex;
    flex-direction: column;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 5px;
}
.status-dot.ingame { background: #4caf50; }
.status-dot.online { background: #8bc34a; }
.status-dot.offline { background: #9e9e9e; }

.username { font-weight: bold; }
.rep { font-size: 0.8rem; color: #888; }

.order-details {
    text-align: right;
}

.whisper-btn {
    background: #333;
    border: none;
    color: white;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s;
}

.whisper-btn:hover { background: #444; }

@media (max-width: 768px) {
    .item-header { flex-direction: column; align-items: center; text-align: center; }
    .orders-section { grid-template-columns: 1fr; }
}

.no-data-chart {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 350px;
    color: #888;
    font-style: italic;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
}

.chart-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.controls-group {
    display: flex;
    gap: 20px;
    align-items: center;
    flex-wrap: wrap;
}

.time-filters, .rank-filters {
    display: flex;
    gap: 10px;
}

.time-filters button, .rank-filters button {
    background: #333;
    border: none;
    color: #888;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9em;
}

.time-filters button:hover, .rank-filters button:hover {
    background: #444;
}

.time-filters button.active, .rank-filters button.active {
    background: #4caf50;
    color: white;
}
</style>