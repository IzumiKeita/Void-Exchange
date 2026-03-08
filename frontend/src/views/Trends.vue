<template>
  <div class="trends-view">
    <div class="header">
      <button @click="goBack" class="back-btn">← {{ t('dashboard.title') }}</button>
      <h1 class="page-title">{{ t('trends.title') }}</h1>
      <p class="subtitle">{{ t('trends.subtitle') }}</p>
    </div>

    <div class="trend-type-toggle">
        <button 
            :class="['type-btn', { active: trendType === 'sell' }]"
            @click="trendType = 'sell'"
        >
            {{ t('trends.sell') }}
        </button>
        <button 
            :class="['type-btn', { active: trendType === 'buy' }]"
            @click="trendType = 'buy'"
        >
            {{ t('trends.buy') }}
        </button>
    </div>

    <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id" 
          :class="['tab-btn', { active: currentTab === tab.id }]"
          @click="currentTab = tab.id"
        >
          {{ tab.label }}
        </button>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>{{ t('trends.loading') }}</p>
    </div>

    <div v-else-if="error" class="error-container">
      <p class="error-msg">{{ error }}</p>
      <button @click="fetchTrends" class="retry-btn">{{ t('common.retry') }}</button>
    </div>

    <div v-else class="trends-list">
      <div v-if="filteredTrends.length === 0" class="empty-state">
        <p>{{ t('trends.empty') }}</p>
      </div>

      <div v-else class="ranking-table">
        <div class="table-header">
          <span class="col-rank">{{ t('trends.table.rank') }}</span>
          <span class="col-item">{{ t('trends.table.item') }}</span>
          <span class="col-trend">{{ t('trends.table.trend') }}</span>
          <span class="col-volume">{{ t('trends.table.volume') }}</span>
        </div>
        
        <div 
            v-for="(item, index) in filteredTrends" 
            :key="item.url_name" 
            class="ranking-row"
            @click="goToItem(item.url_name)"
        >
          <div class="col-rank">
            <span class="rank-number">{{ currentTab === 'all' ? item.rank : index + 1 }}</span>
          </div>
          
          <div class="col-item">
            <img :src="getImageUrl(item.thumb)" :alt="item.item_name" class="item-thumb"/>
            <span class="item-name">{{ item.item_name }}</span>
          </div>
          
          <div class="col-trend">
            <span v-if="item.trend === 'up'" class="trend-indicator up">{{ t('trends.indicators.up') }}</span>
            <span v-else-if="item.trend === 'down'" class="trend-indicator down">{{ t('trends.indicators.down') }}</span>
            <span v-else-if="item.trend === 'new'" class="trend-indicator new">{{ t('trends.indicators.new') }}</span>
            <span v-else class="trend-indicator same">{{ t('trends.indicators.same') }}</span>
          </div>
          
          <div class="col-volume">
            {{ item.volume }} u.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from '../i18n';

const { t } = useI18n();
const router = useRouter();
const allTrends = ref({ sell: [], buy: [] });
const trendType = ref('sell'); // 'sell' or 'buy'
const loading = ref(true);
const error = ref(null);
const currentTab = ref('all');
const API_URL = 'http://localhost:5001/api';

const tabs = computed(() => [
  { id: 'all', label: t('dashboard.tabs.recent') }, // Reusing 'recent' or 'all' concept
  { id: 'warframe', label: t('dashboard.tabs.warframes') },
  { id: 'primary', label: t('dashboard.tabs.primary') },
  { id: 'secondary', label: t('dashboard.tabs.secondary') },
  { id: 'melee', label: t('dashboard.tabs.melee') },
  { id: 'mod', label: t('dashboard.tabs.mods') },
  { id: 'arcane_enhancement', label: t('dashboard.tabs.arcanes') },
  { id: 'relic', label: t('dashboard.tabs.relics') }
]);

 const filteredTrends = computed(() => {
    const currentList = allTrends.value[trendType.value] || [];
    if (currentTab.value === 'all') return currentList;
    
    return currentList.filter(item => {
        const tags = item.tags || [];
        // Lógica de filtrado igual al Dashboard
        const equipmentTabs = ['warframe', 'primary', 'secondary', 'melee'];
        // Modificamos para usar el tag correcto de arcanos
        const upgradeTags = ['mod', 'arcane_enhancement', 'relic'];

        if (equipmentTabs.includes(currentTab.value)) {
            // Asegurarse de no mostrar mods/arcanos si comparten tag (aunque en sets es raro)
            return tags.includes(currentTab.value) && !tags.some(t => upgradeTags.includes(t));
        }

        return tags.includes(currentTab.value);
    });
 });

const getImageUrl = (path) => {
    if (!path) return '';
    if (path.startsWith('http')) return path;
    return `${API_URL}/images/${path}`;
};

const goBack = () => {
    router.push('/');
};

const goToItem = (urlName) => {
    router.push(`/item/${urlName}`);
};

const fetchTrends = async () => {
    loading.value = true;
    error.value = null;
    try {
        const response = await fetch(`${API_URL}/trends`);
        if (!response.ok) throw new Error('Error al cargar tendencias');
        const data = await response.json();
        
        if (Array.isArray(data)) {
            // Backward compatibility
            allTrends.value = { sell: data, buy: [] };
        } else {
            allTrends.value = data;
        }
    } catch (err) {
        console.error(err);
        error.value = "No se pudieron cargar las tendencias.";
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    fetchTrends();
    // Auto-refresh every 60s check
    setInterval(fetchTrends, 60000);
});
</script>

<style scoped>
.trends-view {
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px;
    color: #fff;
}

.header {
    margin-bottom: 30px;
    text-align: center;
}

.trend-type-toggle {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 20px;
}

.type-btn {
    background: #222;
    border: 1px solid #444;
    color: #888;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1.1em;
    font-weight: bold;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    gap: 10px;
}

.type-btn:hover {
    background: #333;
    color: #ccc;
    border-color: #666;
}

.type-btn.active {
    background: #ff9800;
    color: white;
    border-color: #ff9800;
    box-shadow: 0 0 15px rgba(255, 152, 0, 0.3);
}

.page-title {
    font-size: 2.5em;
    color: #ff9800; /* Orange for trends */
    margin: 10px 0;
}

.subtitle {
    color: #aaa;
}

.back-btn {
    background: transparent;
    border: 1px solid #444;
    color: #aaa;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    position: absolute;
    left: 20px;
    top: 20px;
}

.back-btn:hover {
    border-color: #ff9800;
    color: #ff9800;
}

.loading, .error-container, .empty-state {
    text-align: center;
    padding: 50px;
    color: #888;
}

.retry-btn {
    background: #ff9800;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 10px;
}

.tabs {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.tab-btn {
    background: #2a2a2a;
    border: none;
    color: #888;
    padding: 10px 20px;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.3s;
}

.tab-btn:hover {
    background: #3a3a3a;
    color: #fff;
}

.tab-btn.active {
    background: #ff9800; /* Matching trends theme */
    color: white;
}

.ranking-table {
    background: #2a2a2a;
    border-radius: 10px;
    overflow: hidden;
}

.table-header {
    display: flex;
    padding: 15px;
    background: #333;
    font-weight: bold;
    color: #ccc;
    border-bottom: 2px solid #444;
}

.ranking-row {
    display: flex;
    padding: 15px;
    border-bottom: 1px solid #333;
    align-items: center;
    cursor: pointer;
    transition: background 0.2s;
}

.ranking-row:hover {
    background: #3a3a3a;
}

.col-rank {
    width: 60px;
    font-size: 1.2em;
    font-weight: bold;
    text-align: center;
    color: #ff9800;
}

.col-item {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 15px;
}

.item-thumb {
    width: 40px;
    height: 40px;
    object-fit: contain;
}

.item-name {
    font-size: 1.1em;
}

.col-trend {
    width: 150px;
    text-align: center;
}

.col-volume {
    width: 150px;
    text-align: right;
    font-family: monospace;
    font-size: 1.1em;
    color: #ccc;
}

.trend-indicator {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.9em;
    font-weight: bold;
}

.trend-indicator.up { color: #4caf50; background: rgba(76, 175, 80, 0.1); }
.trend-indicator.down { color: #f44336; background: rgba(244, 67, 54, 0.1); }
.trend-indicator.same { color: #999; background: rgba(153, 153, 153, 0.1); }
.trend-indicator.new { color: #2196f3; background: rgba(33, 150, 243, 0.1); }

@media (max-width: 600px) {
    .col-trend { display: none; }
    .col-volume { width: auto; }
    .page-title { font-size: 1.8em; }
    .back-btn { position: static; display: block; margin-bottom: 20px; }
}
</style>
