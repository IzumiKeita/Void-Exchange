<template>
  <div class="void-trader-page">
    <div class="header">
      <h1>{{ t('voidTrader.title') }}</h1>
      <div class="status-badge" :class="{ active: isActive }">
        {{ isActive ? t('voidTrader.status.active') : t('voidTrader.status.away') }}
      </div>
    </div>

    <!-- Loading / Error States -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>{{ t('voidTrader.loading') }}</p>
    </div>
    <div v-else-if="error" class="error-msg">
      ⚠️ {{ error }}
    </div>

    <div v-else class="content">
      <!-- Warning Message -->
      <div v-if="warning" class="warning-msg">
        ⚠️ {{ warning }}
      </div>

      <!-- Info Panel -->
      <div class="info-panel">
        <div class="info-card location">
          <h3>📍 {{ t('voidTrader.location') }}</h3>
          <p>{{ location || t('voidTrader.unknown') }}</p>
        </div>
        <div class="info-card time">
          <h3>⏳ {{ isActive ? t('voidTrader.departingIn') : t('voidTrader.arrivingIn') }}</h3>
          <p class="timer">{{ timeDisplay }}</p>
          <small>{{ dateDisplay }}</small>
        </div>
      </div>

      <!-- Inventory Section (Active or Last Visit) -->
      <div v-if="displayInventory.length > 0" class="inventory-section">
        <div class="inventory-header">
            <h2>
                {{ isActive ? t('voidTrader.inventory.current') : `${t('voidTrader.inventory.last')} (${formatDate(lastVisitDate)})` }}
            </h2>
            <div class="header-controls">
                <button v-if="isActive" @click="fetchData" class="refresh-btn" :title="t('voidTrader.actions.refresh')">🔄</button>
                <div class="category-filters">
                    <button 
                        v-for="cat in categories" 
                        :key="cat.id"
                        :class="{ active: selectedCategory === cat.id }"
                        @click="selectedCategory = cat.id"
                    >
                        {{ cat.label }}
                    </button>
                </div>
            </div>
        </div>

        <div v-if="!isActive" class="inactive-notice">
            <p>ℹ️ {{ t('voidTrader.inventory.inactiveNotice') }}</p>
        </div>

        <div class="inventory-grid">
          <div 
            v-for="(item, index) in filteredInventory" 
            :key="index" 
            class="item-card"
            @click="goToItem(item.url_name)"
            :class="{ 'clickable': !!item.url_name }"
          >
            <div class="card-header">
              <span class="category-tag">{{ item.category || 'Item' }}</span>
              <h3>{{ item.item_name }}</h3>
            </div>
            
            <div class="costs">
              <div class="cost ducats">
                <span>🦆</span> {{ item.ducats }}
              </div>
              <div class="cost credits">
                <span>💳</span> {{ formatCredits(item.credits) }}
              </div>
            </div>

            <!-- Market Data Integration -->
            <div v-if="item.market_stats" class="market-stats">
              <div class="stat-row">
                <span class="label">{{ t('voidTrader.market.minPrice') }}</span>
                <span class="value">{{ getPriceStats(item).min }} pl</span>
              </div>
              <div class="stat-row">
                <span class="label">{{ t('voidTrader.market.avg') }}</span>
                <span class="value">{{ getPriceStats(item).avg }} pl</span>
              </div>
            </div>
            <div v-else-if="item.tradeable" class="market-stats no-data">
              <small>{{ t('voidTrader.market.noData') }}</small>
            </div>
          </div>
        </div>
      </div>

      <div v-if="!isActive && displayInventory.length === 0 && !loading" class="void-message">
        <p>{{ t('voidTrader.inventory.empty') }}</p>
      </div>

      <!-- History Section -->
      <div class="history-section">
        <h2>📜 {{ t('voidTrader.history.title') }}</h2>
        <button @click="toggleHistory" class="toggle-btn">
          {{ showHistory ? t('voidTrader.history.toggleHide') : t('voidTrader.history.toggleShow') }}
        </button>

        <div v-if="showHistory" class="history-list">
            <div v-if="loadingHistory" class="loading-small">{{ t('voidTrader.history.loading') }}</div>
            <div v-else-if="processedHistory.length === 0">{{ t('voidTrader.history.empty') }}</div>
            <div v-else class="history-container">
                <div v-for="(visit, idx) in processedHistory" :key="idx" class="history-visit-card">
                    <div class="visit-header" @click="toggleVisit(visit.date)">
                        <span class="visit-date">📅 {{ formatDate(visit.date) }}</span>
                        <span class="visit-count">{{ visit.items.length }} {{ t('voidTrader.history.tradeableItems') }}</span>
                        <span class="arrow">{{ visit.expanded ? '▼' : '▶' }}</span>
                    </div>
                    
                    <div v-if="visit.expanded" class="visit-items">
                        <div v-if="visit.items.length === 0" class="no-items-msg">
                            {{ t('voidTrader.history.noItemsCategory') }}
                        </div>
                        <table v-else class="history-table">
                            <thead>
                                <tr>
                                    <th>{{ t('voidTrader.table.item') }}</th>
                                    <th>{{ t('voidTrader.table.ducats') }}</th>
                                    <th>{{ t('voidTrader.table.credits') }}</th>
                                    <th>{{ t('voidTrader.table.plat') }}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr 
                                    v-for="(item, i) in visit.items" 
                                    :key="i"
                                    @click="goToItem(item.url_name)"
                                    :class="{ 'clickable-row': !!item.url_name }"
                                >
                                    <td>{{ item.item_name }}</td>
                                    <td>{{ item.ducats }}</td>
                                    <td>{{ formatCredits(item.credits) }}</td>
                                    <td>{{ item.market_price ? item.market_price + ' pl' : '-' }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from '../i18n';

const { t } = useI18n();

const router = useRouter();
const loading = ref(true);
const error = ref(null);
const warning = ref(null);
const isActive = ref(false);
const location = ref('');
const activationTime = ref('');
const expiryTime = ref('');
const inventory = ref([]); // Inventario actual o último conocido
const lastVisitDate = ref(null);
const timeDisplay = ref('');
const dateDisplay = ref('');
let timerInterval = null;

// Categories
const selectedCategory = ref('all');
const categories = computed(() => [
    { id: 'all', label: t('voidTrader.filters.all') },
    { id: 'mods', label: t('voidTrader.filters.mods') },
    { id: 'weapons', label: t('voidTrader.filters.weapons') },
    { id: 'relics', label: t('voidTrader.filters.relics') },
    { id: 'others', label: t('voidTrader.filters.others') }
]);

const displayInventory = computed(() => inventory.value);

const itemMatchesCategory = (item, filterCat) => {
    if (filterCat === 'all') return true;
    
    const cat = item.category || _guessCategory(item.item_name, true);
    
    if (filterCat === 'others') {
        // Todo lo que no sea Mods, Armas o Reliquias cae en Otros
        return cat !== 'Mods' && cat !== 'Armas' && cat !== 'Reliquias';
    }
    
    if (filterCat === 'mods') return cat === 'Mods';
    if (filterCat === 'weapons') return cat === 'Armas';
    if (filterCat === 'relics') return cat === 'Reliquias';

    return false;
};

const filteredInventory = computed(() => {
    return displayInventory.value.filter(item => itemMatchesCategory(item, selectedCategory.value));
});

// History
const showHistory = ref(false);
const loadingHistory = ref(false);
const history = ref([]);

const processedHistory = computed(() => {
    return history.value.map(visit => {
        // 1. Limpiar basura (cosméticos) usando el filtro estricto
        let items = getVisibleHistoryItems(visit.items);
        
        // 2. Aplicar filtro de categoría seleccionado
        if (selectedCategory.value !== 'all') {
            items = items.filter(item => itemMatchesCategory(item, selectedCategory.value));
        }
        
        return {
            ...visit,
            items: items
        };
    });
});

const API_URL = 'http://localhost:5001/api';

const formatCredits = (val) => {
    return new Intl.NumberFormat('en-US').format(val);
};

const formatDate = (isoStr) => {
    if (!isoStr) return '-';
    return new Date(isoStr).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
};

const fetchHistory = async () => {
    loadingHistory.value = true;
    try {
        const res = await fetch(`${API_URL}/void-trader/history`);
        if (!res.ok) throw new Error("Error cargando historial");
        const data = await res.json();
        // Agregar estado 'expanded' a cada visita
        history.value = data.map(visit => ({ ...visit, expanded: false }));
        return history.value;
    } catch (e) {
        console.error(e);
        return [];
    } finally {
        loadingHistory.value = false;
    }
};

const fetchData = async () => {
  loading.value = true;
  error.value = null;
  try {
    const res = await fetch(`${API_URL}/void-trader/current`);
    if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
    const data = await res.json();
    
    if (data.error) throw new Error(data.error);

    isActive.value = data.active;
    location.value = data.location;
    
    // Set timing
    if (data.active) {
        expiryTime.value = data.expiry;
        dateDisplay.value = `Hasta: ${new Date(data.expiry).toLocaleString()}`;
        inventory.value = data.inventory || [];
    } else {
        activationTime.value = data.activation; 
        dateDisplay.value = `Llega: ${new Date(data.activation).toLocaleString()}`;
        
        // Si no está activo, cargar el historial y mostrar la última visita
        const hist = await fetchHistory();
        if (hist && hist.length > 0) {
            // La API devuelve orden descendente, así que el primero es el último
            const lastVisit = hist[0];
            inventory.value = lastVisit.items.map(i => ({
                ...i,
                // Mapear campos de historial a formato de inventario si difieren
                category: i.category || _guessCategory(i.item_name, true),
                market_stats: i.market_stats || (i.market_price ? { avg_price: i.market_price, min_price: '?' } : null),
                tradeable: true // Asumimos tradeable si está guardado en historial filtrado
            }));
            lastVisitDate.value = lastVisit.date;
        } else {
            inventory.value = [];
        }
    }

    startTimer();

  } catch (e) {
    error.value = e.message;
    console.error("Error fetching Void Trader:", e);
  } finally {
    loading.value = false;
  }
};

const _guessCategory = (name, isTradeable) => {
    const n = name.toLowerCase();
    if (n.includes('mod') || n.includes('primed')) return 'Mods';
    if (n.includes('reliquia') || n.includes('axi')) return 'Reliquias';
    if (isTradeable && (n.includes('vandal') || n.includes('wraith') || n.includes('prisma'))) return 'Armas';
    return 'Otros';
};

const getVisibleHistoryItems = (items) => {
    return items.filter(item => {
        // 1. Si tiene flag tradeable explícita, confiamos en ella (prioridad máxima)
        // Esto soluciona el problema de items válidos ocultos por heurísticas fallidas
        if (item.tradeable === true) return true;

        // Filtro estricto visual para limpiar historial antiguo sucio (si no tiene flag tradeable)
        const n = item.item_name.toLowerCase();
        
        // Blacklist de cosméticos
        const blacklist = [
            'skin', 'diseño', 'aspecto', 'helmet', 'casco', 'glifo', 'glyph', 
            'sigil', 'sello', 'emblema', 'armadura', 'armor', 'syandana', 'sugatra',
            'decoración', 'decoration', 'noggle', 'estatua', 'pedestal',
            'color', 'palette', 'paleta', 'escena', 'scene', 'gesto', 'emote',
            'máscara', 'mask', 'diadema', 'auricular', 'kavat', 'kubrow',
            'peluche', 'efímero', 'ephemera', 'canción', 'song', 'drone', 'domestik',
            'transmutador', 'fuegos', 'fireworks', 'espectro', 'floof', 'prez'
        ];
        
        // Whitelist de excepciones (cosas que pueden sonar a blacklist pero son tradeables)
        if (n.includes('prisma') || n.includes('vandal') || n.includes('wraith')) return true;
        
        if (blacklist.some(term => n.includes(term))) return false;
        
        // Debe ser Mod, Reliquia o Arma/Tradeable
        // AHORA INCLUIMOS "PRIME" (Español) ADEMÁS DE "PRIMED"
        if (n.includes('mod') || n.includes('primed') || n.includes('prime')) return true;
        if (n.includes('reliquia') || n.includes('axi') || n.includes('neo') || n.includes('meso') || n.includes('lith')) return true;
        
        // Chequeo de stats de mercado (compatible con estructura vieja y nueva)
        if ((item.market_price && item.market_price > 0) || item.market_stats) return true;
        
        // Si no cumple nada explícito, lo ocultamos por seguridad si el usuario quiere "solo tradeable"
        return false;
    });
};

const getPriceStats = (item) => {
    const stats = item.market_stats;
    if (!stats) return { min: 'N/A', avg: 'N/A' };

    // 1. Mods / Items con Rango (Baro vende Rank 0)
    if (stats.rank_0) {
        return {
            min: stats.rank_0.min_price || stats.rank_0.price || 'N/A',
            avg: stats.rank_0.avg_price || stats.rank_0.price || 'N/A'
        };
    }

    // 2. Reliquias (Baro vende Intact)
    if (stats.intact) {
        return {
            min: stats.intact.min_price || stats.intact.price || 'N/A',
            avg: stats.intact.avg_price || stats.intact.price || 'N/A'
        };
    }

    // 3. Estructura plana (Armas, Otros)
    return {
        min: stats.min_price || stats.price || 'N/A',
        avg: stats.avg_price || stats.price || 'N/A'
    };
};

const goToItem = (urlName) => {
    if (urlName) {
        router.push(`/item/${urlName}`);
    }
};

const toggleHistory = () => {
    showHistory.value = !showHistory.value;
    if (showHistory.value && history.value.length === 0) {
        fetchHistory();
    }
};

const toggleVisit = (date) => {
    const visit = history.value.find(v => v.date === date);
    if (visit) {
        visit.expanded = !visit.expanded;
    }
};

// --- CHAT CONTEXT LOGIC ---
const updateChatContext = () => {
    try {
        const context = {
            type: 'void_trader',
            status: {
                active: isActive.value,
                location: location.value,
                arrival_or_departure: isActive.value ? expiryTime.value : activationTime.value
            },
            inventory_count: inventory.value.length,
            inventory: inventory.value.map(i => ({
                name: i.item_name,
                ducats: i.ducats,
                credits: i.credits,
                category: i.category,
                market_stats: i.market_stats ? {
                    min: getPriceStats(i).min,
                    avg: getPriceStats(i).avg
                } : null
            })),
            current_filter: selectedCategory.value
        };
        sessionStorage.setItem('activeVoidTraderContext', JSON.stringify(context));
    } catch (e) {
        console.warn("Error updating Void Trader chat context:", e);
    }
};

watch([inventory, isActive, location, selectedCategory], () => {
    updateChatContext();
}, { deep: true });

const startTimer = () => {
    if (timerInterval) clearInterval(timerInterval);
    
    const updateTimer = () => {
        const target = isActive.value ? new Date(expiryTime.value) : new Date(activationTime.value);
        const now = new Date();
        const diff = target - now;

        if (diff <= 0) {
            timeDisplay.value = "Calculando...";
            return;
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);

        timeDisplay.value = `${days}d ${hours}h ${minutes}m ${seconds}s`;
    };

    updateTimer();
    timerInterval = setInterval(updateTimer, 1000);
};

onMounted(() => {
    fetchData();
});

onUnmounted(() => {
    if (timerInterval) clearInterval(timerInterval);
});
</script>

<style scoped>
.clickable {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.clickable:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.clickable-row {
    cursor: pointer;
}
.clickable-row:hover {
    background-color: #444;
}

.void-trader-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  color: #eee;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  border-bottom: 2px solid #333;
  padding-bottom: 15px;
}

.status-badge {
  padding: 8px 16px;
  border-radius: 20px;
  background: #444;
  font-weight: bold;
  color: #aaa;
}
.status-badge.active {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
  border: 1px solid #4caf50;
}

.loading, .error-msg {
  text-align: center;
  padding: 40px;
  font-size: 1.2em;
}
.error-msg {
    color: #f44336;
}
.warning-msg {
    background: rgba(255, 152, 0, 0.1);
    border: 1px solid #ff9800;
    color: #ff9800;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 20px;
    text-align: center;
}
.spinner {
    border: 4px solid rgba(255, 255, 255, 0.1);
    border-left-color: #4caf50;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
}
@keyframes spin { to { transform: rotate(360deg); } }

.info-panel {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 30px;
}
.info-card {
    background: #2a2a2a;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
}
.info-card h3 { color: #aaa; margin-bottom: 10px; font-size: 0.9em; text-transform: uppercase; }
.info-card p { font-size: 1.2em; font-weight: bold; }
.timer { font-family: monospace; font-size: 1.5em !important; color: #ffd700; }

/* Inventory */
.inventory-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.header-controls {
    display: flex;
    gap: 15px;
    align-items: center;
}
.refresh-btn {
    background: none;
    border: 1px solid #444;
    cursor: pointer;
    padding: 5px 10px;
    border-radius: 4px;
    color: #fff;
}
.category-filters {
    display: flex;
    gap: 5px;
}
.category-filters button {
    background: #333;
    border: none;
    padding: 5px 12px;
    border-radius: 15px;
    color: #888;
    cursor: pointer;
    transition: all 0.2s;
}
.category-filters button.active {
    background: #4caf50;
    color: #fff;
}

.inventory-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}
.item-card {
    background: #252525;
    border-radius: 8px;
    padding: 15px;
    border: 1px solid #333;
    transition: transform 0.2s;
}
.item-card:hover {
    transform: translateY(-2px);
    border-color: #4caf50;
}
.clickable {
    cursor: pointer;
}
.card-header {
    margin-bottom: 15px;
}
.category-tag {
    font-size: 0.7em;
    color: #4caf50;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.tradeable-badge {
    font-size: 0.7em;
    background: #1a3a1a;
    color: #4caf50;
    padding: 2px 6px;
    border-radius: 4px;
    margin-left: 5px;
}
.item-card h3 {
    margin: 5px 0;
    font-size: 1.1em;
}

.costs {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
    background: #1e1e1e;
    padding: 8px;
    border-radius: 4px;
}
.cost { display: flex; align-items: center; gap: 5px; font-weight: bold; }
.cost.ducats { color: #ffd700; }
.cost.credits { color: #aaa; }

.market-stats {
    border-top: 1px solid #333;
    padding-top: 10px;
    font-size: 0.9em;
}
.stat-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;
}
.stat-row .label { color: #888; }
.stat-row .value { color: #fff; font-weight: bold; }
.no-data { color: #666; font-style: italic; text-align: center; }

.inactive-notice {
    background: rgba(255, 193, 7, 0.1);
    border: 1px solid rgba(255, 193, 7, 0.3);
    color: #ffc107;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 20px;
    text-align: center;
}

/* History */
.history-section {
    border-top: 2px solid #333;
    padding-top: 30px;
}
.toggle-btn {
    background: #333;
    color: #fff;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    margin-bottom: 20px;
}

.history-container {
    display: flex;
    flex-direction: column;
    gap: 15px;
}
.history-visit-card {
    background: #252525;
    border-radius: 8px;
    overflow: hidden;
}
.visit-header {
    padding: 15px;
    background: #2e2e2e;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    transition: background 0.2s;
}
.visit-header:hover {
    background: #353535;
}
.visit-date { font-weight: bold; color: #4caf50; }
.visit-count { color: #aaa; }
.no-items-msg { padding: 15px; color: #888; font-style: italic; text-align: center; }

.visit-items {
    padding: 15px;
    background: #222;
}

.history-table {
    width: 100%;
    border-collapse: collapse;
}
.history-table th, .history-table td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid #333;
}
.history-table th { color: #888; font-weight: normal; }
.history-table td { color: #ddd; }
</style>
