<template>
  <div class="ducats-view">
    <div class="header">
      <button @click="goBack" class="back-btn">← {{ t('dashboard.title') }}</button>
      <h1 class="page-title">{{ t('ducats.title') }}</h1>
      <p class="subtitle">{{ t('ducats.subtitle') }}</p>
    </div>

    <div class="controls">
        <div class="search-box">
            <input 
              type="text" 
              v-model="searchQuery" 
              :placeholder="t('ducats.searchPlaceholder')" 
              class="search-input"
            />
        </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>{{ t('ducats.loading') }}</p>
    </div>

    <div v-else-if="error" class="error-container">
      <p class="error-msg">{{ error }}</p>
      <button @click="fetchDucatsData" class="retry-btn">{{ t('common.retry') }}</button>
    </div>

    <div v-else class="ducats-list">
      <div class="ranking-table">
        <div class="table-header">
          <span class="col-item">{{ t('ducats.table.item') }}</span>
          <span class="col-ducats" @click="sortBy('ducats')">{{ t('ducats.table.ducats') }}</span>
          <span class="col-plat" @click="sortBy('plat_price')">{{ t('ducats.table.plat') }}</span>
          <span class="col-ratio" @click="sortBy('ducats_per_plat')">{{ t('ducats.table.ratio') }}</span>
          <span class="col-volume" @click="sortBy('volume')">{{ t('ducats.table.volume') }}</span>
        </div>
        
        <div 
            v-for="item in sortedAndFilteredItems" 
            :key="item.id" 
            class="ranking-row"
            @click="goToItem(item.url_name)"
        >
          <div class="col-item">
            <img :src="getImageUrl(item.thumb)" :alt="item.item_name" class="item-thumb" @error="handleImageError"/>
            <div class="item-info">
                <span class="item-name">{{ item.item_name }}</span>
            </div>
          </div>
          
          <div class="col-ducats">
            <span class="value">{{ item.ducats }}</span>
            <span class="unit">duc</span>
          </div>
          
          <div class="col-plat">
            <span class="value">{{ item.plat_price }}</span>
            <span class="unit">pl</span>
          </div>
          
          <div class="col-ratio">
            <span :class="['ratio-badge', getRatioClass(item.ducats_per_plat)]">
                {{ item.ducats_per_plat.toFixed(1) }}
            </span>
          </div>
          
          <div class="col-volume">
            {{ item.volume }}
          </div>
        </div>
        
        <div v-if="sortedAndFilteredItems.length === 0" class="empty-state">
            <p>{{ t('ducats.empty') }}</p>
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
const ducatsData = ref([]);
const loading = ref(true);
const error = ref(null);
const searchQuery = ref('');
const sortKey = ref('ducats_per_plat');
const sortDesc = ref(true);

const API_URL = 'http://localhost:5001/api';

const goBack = () => {
  router.push('/');
};

const goToItem = (urlName) => {
  router.push(`/item/${urlName}`);
};

const getImageUrl = (thumbPath) => {
  if (!thumbPath) return '';
  if (thumbPath.startsWith('http')) return thumbPath;
  return `${API_URL}/images/${thumbPath}`;
};

const handleImageError = (e) => {
    e.target.style.display = 'none';
};

const getRatioClass = (ratio) => {
    if (ratio >= 10) return 'excellent'; // Muy eficiente (muchos ducados por poco platino)
    if (ratio >= 5) return 'good';
    if (ratio >= 2) return 'normal';
    return 'bad'; // Poco eficiente
};

const fetchDucatsData = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await fetch(`${API_URL}/ducats`);
    
    if (!response.ok) {
      throw new Error(`Error HTTP: ${response.status}`);
    }
    
    const data = await response.json();
    ducatsData.value = data;
  } catch (err) {
    console.error('Error fetching ducats data:', err);
    error.value = 'No se pudo cargar la información de Ducanator. Inténtalo de nuevo más tarde.';
  } finally {
    loading.value = false;
  }
};

const sortBy = (key) => {
  if (sortKey.value === key) {
    sortDesc.value = !sortDesc.value;
  } else {
    sortKey.value = key;
    sortDesc.value = true; // Default descendente para nuevos sorts
  }
};

const sortedAndFilteredItems = computed(() => {
  let items = ducatsData.value;
  
  // Filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    items = items.filter(item => 
      item.item_name.toLowerCase().includes(query)
    );
  }
  
  // Sort
  return items.sort((a, b) => {
    let valA = a[sortKey.value];
    let valB = b[sortKey.value];
    
    // Handle specific types if needed, but numbers work fine
    if (valA === valB) return 0;
    
    const result = valA > valB ? 1 : -1;
    return sortDesc.value ? -result : result;
  });
});

onMounted(() => {
  fetchDucatsData();
});
</script>

<style scoped>
.ducats-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  margin-bottom: 30px;
}

.back-btn {
  background: none;
  border: none;
  color: #aaa;
  cursor: pointer;
  font-size: 1rem;
  padding: 0;
  margin-bottom: 10px;
}

.back-btn:hover {
  color: #fff;
  text-decoration: underline;
}

.page-title {
  font-size: 2rem;
  margin: 0 0 10px 0;
  background: linear-gradient(45deg, #ffd700, #daa520);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: #aaa;
  margin: 0;
}

.controls {
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.search-input {
    padding: 10px 15px;
    border-radius: 8px;
    border: 1px solid #444;
    background-color: #2a2a2a;
    color: #fff;
    width: 300px;
    font-size: 1rem;
}

.loading, .error-container, .empty-state {
  text-align: center;
  padding: 50px;
  background-color: #2a2a2a;
  border-radius: 12px;
  margin-top: 20px;
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-left-color: #ffd700;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.ranking-table {
  background-color: #2a2a2a;
  border-radius: 12px;
  overflow: hidden;
}

.table-header {
  display: flex;
  padding: 15px 20px;
  background-color: #333;
  font-weight: bold;
  color: #aaa;
  border-bottom: 1px solid #444;
}

.table-header span {
    cursor: pointer;
    user-select: none;
}

.table-header span:hover {
    color: #fff;
}

.ranking-row {
  display: flex;
  padding: 15px 20px;
  border-bottom: 1px solid #333;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.ranking-row:hover {
  background-color: #3a3a3a;
}

.ranking-row:last-child {
  border-bottom: none;
}

.col-item { flex: 2; display: flex; align-items: center; gap: 15px; }
.col-ducats { flex: 1; text-align: right; }
.col-plat { flex: 1; text-align: right; }
.col-ratio { flex: 1; text-align: center; }
.col-volume { flex: 1; text-align: right; }

.item-thumb {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.item-name {
  font-weight: 500;
  color: #fff;
}

.unit {
    font-size: 0.8rem;
    color: #888;
    margin-left: 4px;
}

.value {
    font-weight: bold;
    color: #e0e0e0;
}

.ratio-badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-weight: bold;
    display: inline-block;
    min-width: 40px;
}

.excellent { background-color: rgba(76, 175, 80, 0.2); color: #81c784; border: 1px solid rgba(76, 175, 80, 0.5); }
.good { background-color: rgba(33, 150, 243, 0.2); color: #64b5f6; border: 1px solid rgba(33, 150, 243, 0.5); }
.normal { background-color: rgba(255, 193, 7, 0.2); color: #ffd54f; border: 1px solid rgba(255, 193, 7, 0.5); }
.bad { background-color: rgba(244, 67, 54, 0.2); color: #e57373; border: 1px solid rgba(244, 67, 54, 0.5); }

@media (max-width: 768px) {
  .table-header { display: none; }
  
  .ranking-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    padding: 15px;
  }
  
  .col-item, .col-ducats, .col-plat, .col-ratio, .col-volume {
    width: 100%;
    text-align: left;
    display: flex;
    justify-content: space-between;
  }
  
  .col-item { margin-bottom: 5px; }
  
  .col-ducats::before { content: "Ducados:"; color: #aaa; }
  .col-plat::before { content: "Platino:"; color: #aaa; }
  .col-ratio::before { content: "Ducados/Plat:"; color: #aaa; }
  .col-volume::before { content: "Volumen:"; color: #aaa; }
}
</style>
