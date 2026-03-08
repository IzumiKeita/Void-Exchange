<template> 
   <div class="dashboard"> 
     <div class="header-row">
        <h1>{{ t('dashboard.title') }}</h1>
        <div class="nav-links">
            <router-link to="/trends" class="trends-link">
                {{ t('dashboard.trends') }}
            </router-link>
            <router-link to="/void-trader" class="void-link">
                {{ t('dashboard.voidTrader') }}
            </router-link>
            <router-link to="/ducats" class="ducats-link">
                {{ t('dashboard.ducats') }}
            </router-link>
            <router-link to="/vault" class="vault-link">
                {{ t('dashboard.vault') }}
            </router-link>
            <router-link to="/trading" class="trading-link">
                {{ t('dashboard.trading') }}
            </router-link>
        </div>
     </div>
     
     <div class="controls">
        <input 
          type="text" 
          v-model="searchQuery" 
          :placeholder="t('dashboard.searchPlaceholder')" 
          @input="filterItems"
          class="search-input"
        />
        
        <div class="sort-controls" v-if="currentTab !== 'all'">
            <button 
                class="sort-btn" 
                :class="{ active: sortOrder === 'trend_asc' }"
                @click="handleSort('trend_asc')"
                :title="t('dashboard.sort.downTitle')"
                :disabled="loadingSort"
            >
                {{ t('dashboard.sort.down') }}
            </button>
            <button 
                class="sort-btn" 
                :class="{ active: sortOrder === 'trend_desc' }"
                @click="handleSort('trend_desc')"
                :title="t('dashboard.sort.upTitle')"
                :disabled="loadingSort"
            >
                {{ t('dashboard.sort.up') }}
            </button>
            <button 
                class="sort-btn" 
                :class="{ active: sortOrder === 'price_desc' }"
                @click="handleSort('price_desc')"
                :title="t('dashboard.sort.highPriceTitle')"
                :disabled="loadingSort"
            >
                {{ t('dashboard.sort.highPrice') }}
            </button>
            <div v-if="loadingSort" class="sort-loader">
                <span class="spinner"></span>
            </div>
        </div>
     </div>

     <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id" 
          :class="['tab-btn', { active: currentTab === tab.id }]"
          @click="changeTab(tab.id)"
        >
          {{ tab.label }}
        </button>
     </div>
     
     <!-- Sub-filtros para Warframe -->
     <div v-if="currentTab === 'warframe'" class="sub-tabs">
        <button 
          v-for="sub in warframeFilters" 
          :key="sub.id" 
          :class="['sub-tab-btn', { active: warframeSubFilter === sub.id }]"
          @click="changeWarframeFilter(sub.id)"
        >
          {{ sub.label }}
        </button>
     </div>
     
     <!-- Sub-filtros para Armas (Primarias/Secundarias) -->
     <div v-if="currentTab === 'primary' || currentTab === 'secondary'" class="sub-tabs">
        <button 
          v-for="sub in weaponFilters" 
          :key="sub.id" 
          :class="['sub-tab-btn', { active: weaponSubFilter === sub.id }]"
          @click="changeWeaponFilter(sub.id)"
        >
          {{ sub.label }}
        </button>
     </div>

     <!-- Sub-filtros para Melee -->
     <div v-if="currentTab === 'melee'" class="sub-tabs">
        <button 
          v-for="sub in meleeFilters" 
          :key="sub.id" 
          :class="['sub-tab-btn', { active: meleeSubFilter === sub.id }]"
          @click="changeMeleeFilter(sub.id)"
        >
          {{ sub.label }}
        </button>
     </div>
     
     <div v-if="currentTab === 'all' && recentItems.length > 0" class="history-controls">
        <button @click="clearHistory" class="clear-btn">{{ t('dashboard.history.clear') }}</button>
     </div>

     <div v-if="loading" class="loading">{{ t('common.loading') }}</div> 
     
     <transition-group name="list" tag="div" class="grid" v-else>
       <!-- Vista Historial (Todo) -->
       <template v-if="currentTab === 'all'">
            <div v-if="recentMarketData.length === 0" class="empty-state">
                <p>{{ t('dashboard.history.empty') }}</p>
                <p>{{ t('dashboard.history.emptySub') }}</p>
            </div>
            <div 
                v-else
                v-for="item in recentMarketData" 
                :key="item.url_name + (item.rank || '')" 
                class="card"
                @click="goToDetail(item)"
            > 
                <div class="card-header">
                   <img 
                       v-if="item.image" 
                       :src="`${API_URL}/images/${item.image}`" 
                       alt="Item icon" 
                       class="item-icon"
                       @error="$event.target.style.display='none'"
                   />
                   <h3>{{ item.name }}</h3> 
                   <span v-if="item.rank !== null" class="rank-badge">{{ t('dashboard.card.rank') }} {{ item.rank }}</span>
                </div>
                
                <div v-if="item.is_ranked" class="ranked-stats-container">
                    <div class="rank-row">
                       <span class="rank-badge-small">R{{ item.min_rank }}</span>
                       <div class="rank-prices-compact">
                           <span class="p-min" :title="t('dashboard.card.min')">{{ item.rank_min_stats?.min_price || '-' }}</span>
                           <span class="p-avg" :title="t('dashboard.card.avg')">{{ item.rank_min_stats?.price || '-' }}</span>
                           <span class="p-max" :title="t('dashboard.card.max')">{{ item.rank_min_stats?.max_price || '-' }}</span>
                       </div>
                    </div>
                    <div class="rank-row">
                       <span class="rank-badge-small">R{{ item.max_rank }}</span>
                       <div class="rank-prices-compact">
                           <span class="p-min" :title="t('dashboard.card.min')">{{ item.rank_max_stats?.min_price || '-' }}</span>
                           <span class="p-avg" :title="t('dashboard.card.avg')">{{ item.rank_max_stats?.price || '-' }}</span>
                           <span class="p-max" :title="t('dashboard.card.max')">{{ item.rank_max_stats?.max_price || '-' }}</span>
                       </div>
                    </div>
                </div>
                
                <div v-else class="price-range">
                    <div class="price-min">
                        <span class="label">{{ t('dashboard.card.min') }}</span>
                        <span class="value">{{ item.min_price || '-' }}</span>
                    </div>
                    <div class="price-avg">
                        <span class="label">{{ t('dashboard.card.avg') }}</span>
                        <span class="value">{{ item.price || '-' }}</span>
                    </div>
                    <div class="price-max">
                        <span class="label">{{ t('dashboard.card.max') }}</span>
                        <span class="value">{{ item.max_price || '-' }}</span>
                    </div>
                </div>
                
                <div class="stats">
                    <p :class="['trend', item.trend >= 0 ? 'up' : 'down']"> 
                      {{ item.trend >= 0 ? '▲' : '▼' }} {{ item.trend }}% 
                    </p>
                    <p class="volume">{{ t('dashboard.card.vol') }} {{ item.volume }}</p>
                </div>
            </div>
       </template>

       <!-- Vista Catálogo (Otras Pestañas) -->
       <template v-else>
            <div 
                v-for="item in paginatedCatalogItems" 
                :key="item.id" 
                class="card catalog-card"
                @click="goToDetailFromCatalog(item)"
            > 
                <div class="card-header">
                   <img 
                   v-if="item.thumb" 
                   :src="`${API_URL}/images/${item.thumb}`" 
                   alt="Item icon" 
                   class="item-icon"
               />
                   <h3>{{ item.item_name }}</h3> 
                </div>
                <template v-if="catalogMarketData[item.url_name]">
                    <div v-if="catalogMarketData[item.url_name].is_ranked" class="ranked-stats-container">
                        <div class="rank-row">
                           <span class="rank-badge-small">R{{ catalogMarketData[item.url_name].min_rank }}</span>
                           <div class="rank-prices-compact">
                               <span class="p-min" :title="t('dashboard.card.min')">{{ catalogMarketData[item.url_name].rank_min_stats?.min_price || '-' }}</span>
                           <span class="p-avg" :title="t('dashboard.card.avg')">{{ catalogMarketData[item.url_name].rank_min_stats?.price || '-' }}</span>
                           <span class="p-max" :title="t('dashboard.card.max')">{{ catalogMarketData[item.url_name].rank_min_stats?.max_price || '-' }}</span>
                       </div>
                    </div>
                    <div class="rank-row">
                       <span class="rank-badge-small">R{{ catalogMarketData[item.url_name].max_rank }}</span>
                       <div class="rank-prices-compact">
                           <span class="p-min" :title="t('dashboard.card.min')">{{ catalogMarketData[item.url_name].rank_max_stats?.min_price || '-' }}</span>
                           <span class="p-avg" :title="t('dashboard.card.avg')">{{ catalogMarketData[item.url_name].rank_max_stats?.price || '-' }}</span>
                           <span class="p-max" :title="t('dashboard.card.max')">{{ catalogMarketData[item.url_name].rank_max_stats?.max_price || '-' }}</span>
                       </div>
                    </div>
                </div>
                
                <div v-else class="price-range">
                    <div class="price-min">
                        <span class="label">{{ t('dashboard.card.min') }}</span>
                        <span class="value">{{ catalogMarketData[item.url_name].min_price || '-' }}</span>
                    </div>
                    <div class="price-avg">
                        <span class="label">{{ t('dashboard.card.avg') }}</span>
                        <span class="value">{{ catalogMarketData[item.url_name].price || '-' }}</span>
                    </div>
                    <div class="price-max">
                        <span class="label">{{ t('dashboard.card.max') }}</span>
                        <span class="value">{{ catalogMarketData[item.url_name].max_price || '-' }}</span>
                    </div>
                </div>
                
                <div class="stats">
                    <p :class="['trend', catalogMarketData[item.url_name].trend >= 0 ? 'up' : 'down']"> 
                      {{ catalogMarketData[item.url_name].trend >= 0 ? '▲' : '▼' }} {{ catalogMarketData[item.url_name].trend }}% 
                    </p>
                    <p class="volume">{{ t('dashboard.card.vol') }} {{ catalogMarketData[item.url_name].volume }}</p>
                </div>
                </template>
            </div>
       </template>
     </transition-group> 

     <!-- Paginación para Catálogo -->
     <div v-if="currentTab !== 'all' && totalPages > 1" class="pagination">
        <button :disabled="currentPage === 1" @click="currentPage--">{{ t('dashboard.pagination.prev') }}</button>
        <span>{{ t('dashboard.pagination.page', { current: currentPage, total: totalPages }) }}</span>
        <button :disabled="currentPage === totalPages" @click="currentPage++">{{ t('dashboard.pagination.next') }}</button>
     </div>
   </div> 
 </template> 

 <script setup> 
 import { ref, onMounted, computed, watch, reactive } from 'vue'; 
 import { useRouter } from 'vue-router';
 import { useI18n } from '../i18n';

 const { t } = useI18n();

 const router = useRouter();
 const recentMarketData = ref([]); 
 const allItems = ref([]);
 const searchQuery = ref('');
 const loading = ref(true); 
 const currentTab = ref('all');
 const recentItems = ref([]); // Lista de {url_name, rank}
 const currentPage = ref(1);
const itemsPerPage = 50;
const catalogMarketData = reactive({});
const warframeSubFilter = ref('all');
const weaponSubFilter = ref('all');
const meleeSubFilter = ref('all');

// Sorting State
const sortOrder = ref('default');
const loadingSort = ref(false);
const marketCache = new Map(); // url_name -> { data, timestamp }
const CACHE_TTL = 5 * 60 * 1000; // 5 minutos

const API_URL = 'http://localhost:5001/api';

const tabs = computed(() => [
   { id: 'all', label: t('dashboard.tabs.recent') },
   { id: 'warframe', label: t('dashboard.tabs.warframes') },
   { id: 'primary', label: t('dashboard.tabs.primary') },
   { id: 'secondary', label: t('dashboard.tabs.secondary') },
   { id: 'melee', label: t('dashboard.tabs.melee') },
   { id: 'mod', label: t('dashboard.tabs.mods') },
   { id: 'arcane', label: t('dashboard.tabs.arcanes') },
   { id: 'relic', label: t('dashboard.tabs.relics') },
   { id: 'other', label: t('dashboard.tabs.others') }
]);

const warframeFilters = computed(() => [
    { id: 'all', label: t('dashboard.subfilters.all') },
    { id: 'set', label: t('dashboard.subfilters.sets') },
    { id: 'blueprint', label: t('dashboard.subfilters.blueprints') },
    { id: 'neuroptics', label: t('dashboard.subfilters.neuroptics') },
    { id: 'chassis', label: t('dashboard.subfilters.chassis') },
    { id: 'systems', label: t('dashboard.subfilters.systems') }
]);

const weaponFilters = computed(() => [
    { id: 'all', label: t('dashboard.subfilters.all') },
    { id: 'set', label: t('dashboard.subfilters.sets') },
    { id: 'blueprint', label: t('dashboard.subfilters.blueprints') },
    { id: 'receiver', label: t('dashboard.subfilters.receiver') },
    { id: 'barrel', label: t('dashboard.subfilters.barrel') },
    { id: 'stock', label: t('dashboard.subfilters.stock') }
]);

const meleeFilters = computed(() => [
    { id: 'all', label: t('dashboard.subfilters.all') },
    { id: 'set', label: t('dashboard.subfilters.sets') },
    { id: 'blueprint', label: t('dashboard.subfilters.blueprints') },
    { id: 'blade', label: t('dashboard.subfilters.blade') },
    { id: 'handle', label: t('dashboard.subfilters.handle') }
]);

const loadRecentItems = () => {
    const stored = localStorage.getItem('wf_recent_items');
    if (stored) {
        recentItems.value = JSON.parse(stored);
    }
 };

 const fetchRecentData = async () => { 
  if (recentItems.value.length === 0) {
      recentMarketData.value = [];
      loading.value = false;
      return;
  }

  loading.value = true;
  try { 
    // Usar endpoint batch para obtener datos solo de los recientes
    const response = await fetch(`${API_URL}/monitor/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items: recentItems.value })
    });
    const data = await response.json(); 
    // Ordenar por orden de recentItems (más reciente primero)
    // recentItems tiene {url_name, rank}
    // data tiene info de mercado
    // Mapear data para mantener orden
    const orderedData = [];
    // recentItems está ordenado del más reciente al más antiguo
    // pero queremos mostrarlos así.
    
    // Crear mapa para acceso rápido
    const dataMap = new Map();
    data.forEach(d => {
        // La clave debe ser url_name (monitor_controller devuelve datos combinados)
        // Ojo: process_item devuelve datos enriquecidos.
        dataMap.set(d.url_name, d);
    });

    recentItems.value.forEach(ri => {
        const itemData = dataMap.get(ri.url_name);
        if (itemData) {
            orderedData.push(itemData);
        }
    });

    recentMarketData.value = orderedData;
  } catch (error) { 
    console.error("Error conectando al backend:", error); 
  } finally { 
    loading.value = false; 
  } 
 }; 

 const fetchAllItems = async () => {
   try {
       const response = await fetch(`${API_URL}/items`);
       allItems.value = await response.json();
   } catch (error) {
       console.error("Error cargando lista de items:", error);
   }
 };

 const catalogItems = computed(() => {
    if (currentTab.value === 'all') return [];
    
    let filtered = allItems.value;
    
    // Filtrar por pestaña
     if (currentTab.value !== 'all') {
         filtered = filtered.filter(item => {
             const tags = item.tags || [];
             const equipmentTabs = ['warframe', 'primary', 'secondary', 'melee'];
             // Arcanos usan 'arcane_enhancement' en la API
             const upgradeTags = ['mod', 'arcane_enhancement', 'relic'];
      
             if (currentTab.value === 'other') {
                 const mainTags = [...equipmentTabs, ...upgradeTags];
                 return !tags.some(t => mainTags.includes(t));
             }
             
             if (equipmentTabs.includes(currentTab.value)) {
                 return tags.includes(currentTab.value) && !tags.some(t => upgradeTags.includes(t));
             }
             
             // Mapear tab 'arcane' a tag 'arcane_enhancement'
             let targetTag = currentTab.value;
             if (targetTag === 'arcane') targetTag = 'arcane_enhancement';
      
             return tags.includes(targetTag);
         });
         
         // Sub-filtrado para Warframe
         if (currentTab.value === 'warframe' && warframeSubFilter.value !== 'all') {
             filtered = filtered.filter(item => {
                 const url = item.url_name;
                 const sub = warframeSubFilter.value;
                 
                 if (sub === 'set') return url.endsWith('_set');
                 if (sub === 'neuroptics') return url.includes('_neuroptics');
                 if (sub === 'chassis') return url.includes('_chassis');
                 if (sub === 'systems') return url.includes('_systems');
                 if (sub === 'blueprint') {
                     // Solo blueprints principales
                     return url.endsWith('_blueprint') &&
                            !url.includes('_neuroptics') &&
                            !url.includes('_chassis') &&
                            !url.includes('_systems');
                 }
                 return true;
             });
         }
         
         // Sub-filtrado para Armas (Primary/Secondary)
         if ((currentTab.value === 'primary' || currentTab.value === 'secondary') && weaponSubFilter.value !== 'all') {
             filtered = filtered.filter(item => {
                 const url = item.url_name;
                 const sub = weaponSubFilter.value;
                 
                 if (sub === 'set') return url.endsWith('_set');
                 if (sub === 'barrel') return url.includes('_barrel');
                 if (sub === 'receiver') return url.includes('_receiver');
                 if (sub === 'stock') return url.includes('_stock');
                 if (sub === 'blueprint') {
                     return url.endsWith('_blueprint');
                 }
                 return true;
             });
         }

         // Sub-filtrado para Melee
         if (currentTab.value === 'melee' && meleeSubFilter.value !== 'all') {
             filtered = filtered.filter(item => {
                 const url = item.url_name;
                 const sub = meleeSubFilter.value;
                 
                 if (sub === 'set') return url.endsWith('_set');
                 if (sub === 'blade') return url.includes('_blade');
                 if (sub === 'handle') return url.includes('_handle');
                 if (sub === 'blueprint') {
                     return url.endsWith('_blueprint');
                 }
                 return true;
             });
         }
     }
    
    // Filtrar por búsqueda
    if (searchQuery.value.length >= 2) {
        const query = searchQuery.value.toLowerCase();
        filtered = filtered.filter(item => item.item_name.toLowerCase().includes(query));
    }
 
    return filtered;
  });

 const sortedCatalogItems = computed(() => {
    // Copiamos para no mutar el original
    let items = [...catalogItems.value];
    
    if (sortOrder.value === 'default') return items;
    
    return items.sort((a, b) => {
        const dataA = catalogMarketData[a.url_name];
        const dataB = catalogMarketData[b.url_name];

        // Helper para obtener precio comparable
        const getPrice = (d) => {
            if (!d) return -1;
            
            let val = 0;
            // Para items con rango, usar el precio de rango máximo
            if (d.is_ranked) {
               val = d.rank_max_stats?.price || d.rank_min_stats?.price || 0;
            } else {
               // Preferir avg_price, fallback a price
               val = d.avg_price || d.price || 0;
            }

            // Asegurar que sea número (manejo de strings y comas)
            if (typeof val === 'string') {
                val = parseFloat(val.replace(',', '.'));
            }
            return isNaN(val) ? 0 : val;
        };

        if (sortOrder.value === 'price_desc') {
            const priceA = getPrice(dataA);
            const priceB = getPrice(dataB);
            // console.log(`Comparing ${a.item_name} (${priceA}) vs ${b.item_name} (${priceB})`);
            return priceB - priceA;
        }

        // Obtenemos tendencias, por defecto 0 si no hay datos
        // Nota: Si los datos no están cargados, el ordenamiento será 0-0
        const trendA = dataA?.trend || 0;
        const trendB = dataB?.trend || 0;
        
        if (sortOrder.value === 'trend_asc') {
            // Ascendente: Menor a mayor (Ej: -10, -5, 0, 5, 10)
            // "Mostrar primero los ítems que han bajado de precio" -> Negativos primero
            return trendA - trendB;
        } else {
            // Descendente: Mayor a menor (Ej: 10, 5, 0, -5, -10)
            // "Mostrar primero los ítems que han subido de precio" -> Positivos primero
            return trendB - trendA;
        }
    });
 });

 const paginatedCatalogItems = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return sortedCatalogItems.value.slice(start, end);
 });

 const totalPages = computed(() => Math.ceil(sortedCatalogItems.value.length / itemsPerPage));

 // Helper para fetch con caché y batching
 const fetchMarketDataForItems = async (items) => {
    if (!items || items.length === 0) return;
    
    const now = Date.now();
    const itemsToFetch = [];
    
    // Identificar qué items necesitan fetch
    items.forEach(item => {
        const cached = marketCache.get(item.url_name);
        if (cached && (now - cached.timestamp < CACHE_TTL)) {
            // Usar caché si es fresco y no tenemos datos en el reactive
            if (!catalogMarketData[item.url_name]) {
                catalogMarketData[item.url_name] = cached.data;
            }
        } else {
            // Necesita fetch
            itemsToFetch.push({ url_name: item.url_name });
        }
    });
    
    if (itemsToFetch.length === 0) return;
    
    // Procesar en chunks de 50 para no saturar
    const chunkSize = 50;
    for (let i = 0; i < itemsToFetch.length; i += chunkSize) {
        const chunk = itemsToFetch.slice(i, i + chunkSize);
        
        try {
            const response = await fetch(`${API_URL}/monitor/batch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ items: chunk })
            });
            const data = await response.json();
            
            // Actualizar mapa y caché
            data.forEach(d => {
                catalogMarketData[d.url_name] = d;
                marketCache.set(d.url_name, {
                    data: d,
                    timestamp: Date.now()
                });
            });
        } catch (error) {
            console.error("Error cargando batch de stats:", error);
        }
    }
 };

 const fetchCatalogMarketData = async (items) => {
    await fetchMarketDataForItems(items);
};

// Debounce para el sort
let debounceTimer = null;
const handleSort = (order) => {
    if (sortOrder.value === order) {
        sortOrder.value = 'default';
        return;
    }
    
    loadingSort.value = true;
    
    if (debounceTimer) clearTimeout(debounceTimer);
    
    debounceTimer = setTimeout(async () => {
        try {
            // Si vamos a ordenar, necesitamos datos de TODOS los items filtrados actualmente
            // para poder ordenarlos globalmente.
            // Si la lista es muy grande, esto podría tardar, pero el usuario pidió sort.
            await fetchMarketDataForItems(catalogItems.value);
            sortOrder.value = order;
        } catch (e) {
            console.error("Error al preparar ordenamiento:", e);
        } finally {
            loadingSort.value = false;
        }
    }, 300); // 300ms debounce
};


const updateDashboardContext = (items) => {
    try {
        // Tomar los primeros 5 items visibles
        const topItems = items.slice(0, 5).map(item => {
            const market = catalogMarketData[item.url_name] || {};
            return {
                name: item.item_name,
                price: market.min_price || 'N/A',
                avg: market.avg_price || 'N/A',
                trend: market.trend !== undefined ? `${market.trend}%` : 'N/A',
                volume: market.volume || 0
            };
        });

        const context = {
            type: 'dashboard',
            filter: currentTab.value,
            sort: sortOrder.value,
            top_items: topItems
        };

        sessionStorage.setItem('activeDashboardContext', JSON.stringify(context));
        // console.log("Dashboard context updated for AI:", context);
    } catch (e) {
        console.error("Error updating dashboard context:", e);
    }
};

// Observar cambios en la paginación o pestaña para cargar datos y actualizar contexto de IA
watch(paginatedCatalogItems, (newItems) => {
    if (currentTab.value !== 'all' && newItems.length > 0) {
        // Cargar datos de mercado
        fetchCatalogMarketData(newItems).then(() => {
            // Una vez cargados (o si ya estaban en caché), actualizar contexto del chat
            updateDashboardContext(newItems);
        });
    } else {
        // Si estamos en "Recientes" o vacío, también actualizar contexto
        updateDashboardContext(newItems);
    }
}, { immediate: true });

const changeTab = (tabId) => {
   currentTab.value = tabId;
   currentPage.value = 1;
   searchQuery.value = '';
   warframeSubFilter.value = 'all'; // Resetear subfiltro al cambiar de pestaña
   weaponSubFilter.value = 'all';
   meleeSubFilter.value = 'all';
   sortOrder.value = 'default'; // Resetear ordenamiento
   
   if (tabId === 'all') {
       loadRecentItems();
       fetchRecentData();
   } else {
       // Opcional: Limpiar caché de catálogo al cambiar de tab principal
       for (const key in catalogMarketData) delete catalogMarketData[key];
   }
};

const changeWarframeFilter = (filterId) => {
    warframeSubFilter.value = filterId;
    currentPage.value = 1;
};

const changeWeaponFilter = (filterId) => {
    weaponSubFilter.value = filterId;
    currentPage.value = 1;
};

const changeMeleeFilter = (filterId) => {
    meleeSubFilter.value = filterId;
    currentPage.value = 1;
};

 const filterItems = () => {
   currentPage.value = 1; // Resetear a pag 1 al buscar
 };

 const addToHistory = (item) => {
    // item es { url_name, item_name, ... }
    let history = JSON.parse(localStorage.getItem('wf_recent_items') || '[]');
    // Eliminar si ya existe para ponerlo al principio
    history = history.filter(h => h.url_name !== item.url_name);
    
    // Agregar al inicio
    history.unshift({
        url_name: item.url_name,
        rank: null // Por defecto sin rango en historial simple
    });
    
    // Mantener solo 15
    if (history.length > 15) {
        history = history.slice(0, 15);
    }
    
    localStorage.setItem('wf_recent_items', JSON.stringify(history));
 };

 const goToDetailFromCatalog = (item) => {
    addToHistory(item);
    router.push(`/item/${item.url_name}`);
 };

 const goToDetail = (item) => {
    // Ya está en historial, pero lo movemos al top? Sí.
    addToHistory(item);
    router.push(`/item/${item.url_name}`);
 };
 
 const clearHistory = () => {
   if(confirm('¿Borrar historial reciente?')) {
       localStorage.removeItem('wf_recent_items');
       recentItems.value = [];
       recentMarketData.value = [];
   }
};

const restoreDashboardState = () => {
   try {
       const saved = sessionStorage.getItem('dashboard_state');
       if (saved) {
           const state = JSON.parse(saved);
           if (state.currentTab) currentTab.value = state.currentTab;
           if (state.searchQuery) searchQuery.value = state.searchQuery;
           if (state.currentPage) currentPage.value = state.currentPage;
           if (state.warframeSubFilter) warframeSubFilter.value = state.warframeSubFilter;
           if (state.weaponSubFilter) weaponSubFilter.value = state.weaponSubFilter;
           if (state.meleeSubFilter) meleeSubFilter.value = state.meleeSubFilter;
           if (state.sortOrder) sortOrder.value = state.sortOrder;
       }
   } catch (e) {
       console.error("Error restoring dashboard state", e);
   }
};

const saveDashboardState = () => {
    try {
        const state = {
            currentTab: currentTab.value,
            searchQuery: searchQuery.value,
            currentPage: currentPage.value,
            warframeSubFilter: warframeSubFilter.value,
            weaponSubFilter: weaponSubFilter.value,
            meleeSubFilter: meleeSubFilter.value,
            sortOrder: sortOrder.value
        };
        sessionStorage.setItem('dashboard_state', JSON.stringify(state));
    } catch (e) {
        console.error("Error saving dashboard state", e);
    }
};

// Guardar estado automáticamente al cambiar cualquier filtro
watch([currentTab, searchQuery, currentPage, warframeSubFilter, weaponSubFilter, meleeSubFilter, sortOrder], () => {
    saveDashboardState();
});

onMounted(async () => { 
  restoreDashboardState();
  loadRecentItems();
  
  if (currentTab.value === 'all') {
      fetchRecentData();
      fetchAllItems();
  } else {
      // Si estamos restaurando una pestaña de catálogo, necesitamos esperar a que se carguen los items
      loading.value = true;
      await fetchAllItems();
      loading.value = false;
  }
}); 
 </script> 
 
 <style scoped>
 /* Estilos previos mantenidos y adaptados */
 .dashboard { 
   max-width: 1200px; 
   margin: 0 auto; 
   padding: 20px; 
 } 
 h1 { 
   text-align: center; 
   color: #00bcd4; 
 } 
 .header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
 }
 .trends-link, .ducats-link, .vault-link, .scanner-link, .void-link {
    text-decoration: none;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: bold;
    transition: transform 0.2s, box-shadow 0.2s;
 }

 .trends-link {
    background: linear-gradient(45deg, #ff5722, #ff9800);
    color: white;
 }

 .void-link {
    background: linear-gradient(45deg, #009688, #4db6ac);
    color: white;
 }

 .ducats-link {
    background: linear-gradient(45deg, #2196f3, #00bcd4);
    color: white;
 }

 .vault-link {
    background: linear-gradient(45deg, #7b1fa2, #e040fb);
    color: white;
 }

 .scanner-link {
    background: linear-gradient(45deg, #6200ea, #b388ff);
    color: white;
 }

 .trends-link:hover, .ducats-link:hover, .vault-link:hover, .scanner-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
 }
 .nav-links {
    display: flex;
    gap: 15px;
    align-items: center;
 }
 .controls {
    margin-bottom: 20px;
    position: relative;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
    z-index: 1000;
 }
 .search-input {
    width: 100%;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #333;
    background: #2a2a2a;
    color: white;
    font-size: 16px;
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
 .tab-btn.active {
    background: #00bcd4;
    color: white;
 }
 .sub-tabs {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-bottom: 20px;
    flex-wrap: wrap;
 }
 .sub-tab-btn {
    background: transparent;
    border: 1px solid #444;
    color: #888;
    padding: 5px 15px;
    border-radius: 15px;
    cursor: pointer;
    font-size: 0.9em;
    transition: all 0.2s;
 }
 .sub-tab-btn:hover {
    border-color: #666;
    color: #aaa;
 }
 .sub-tab-btn.active {
    background: #00bcd4;
    border-color: #00bcd4;
    color: white;
 }
 .grid { 
   display: grid; 
   grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); 
   gap: 20px; 
 } 
 .card { 
   background-color: #2a2a2a; 
   border-radius: 10px; 
   padding: 15px; 
   text-align: center; 
   position: relative;
   transition: transform 0.2s;
   cursor: pointer;
 } 
 .card:hover {
    transform: translateY(-5px);
 }
 .card-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 10px;
 }
 .item-icon {
    width: 64px;
    height: 64px;
    object-fit: contain;
    margin-bottom: 5px;
 }
 .history-controls {
    text-align: center;
    margin-bottom: 20px;
 }
 .clear-btn {
    background: #f44336;
    color: white;
    border: none;
    padding: 5px 15px;
    border-radius: 5px;
    cursor: pointer;
 }
 .empty-state {
    grid-column: 1 / -1;
    text-align: center;
    color: #888;
    padding: 40px;
 }
 .pagination {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 30px;
    align-items: center;
    color: #888;
 }
 .pagination button {
    background: #2a2a2a;
    border: 1px solid #333;
    color: white;
    padding: 8px 16px;
    border-radius: 5px;
    cursor: pointer;
 }
 .pagination button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
 }
 /* Estilos de stats para vista Recientes */
 .price-range {
    display: flex;
    justify-content: center;
    gap: 15px;
    margin: 10px 0;
    background: rgba(0,0,0,0.2);
    padding: 8px;
    border-radius: 8px;
 }
 .price-min, .price-max, .price-avg {
    display: flex;
    flex-direction: column;
    align-items: center;
 }
 .price-min .label, .price-max .label, .price-avg .label {
    font-size: 0.7em;
    color: #888;
    text-transform: uppercase;
    margin-bottom: 2px;
 }
 .price-min .value { color: #4caf50; font-weight: bold; font-size: 1.1em; }
 .price-max .value { color: #f44336; font-weight: bold; font-size: 1.1em; }
 .price-avg .value { color: #ffd700; font-weight: bold; font-size: 1.2em; }
 
 .stats {
    display: flex;
    justify-content: space-between;
    font-size: 0.9em;
    color: #aaa;
 }
 .trend.up { color: #4caf50; } 
 .trend.down { color: #f44336; } 
 .loading { text-align: center; color: #888; }

.rank-badge {
    background: #00bcd4;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.8em;
    margin-top: 5px;
}
.ranked-stats-container {
    background: rgba(0,0,0,0.2);
    border-radius: 8px;
    padding: 8px;
    margin: 10px 0;
}
.rank-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
    padding: 2px 0;
}
.rank-row:last-child {
    margin-bottom: 0;
}
.rank-badge-small {
    background: #333;
    border: 1px solid #00bcd4;
    color: #00bcd4;
    font-size: 0.75em;
    padding: 1px 5px;
    border-radius: 4px;
    min-width: 30px;
    text-align: center;
}
.rank-prices-compact {
    display: flex;
    gap: 8px;
    font-size: 0.9em;
}
.rank-prices-compact span {
    font-weight: bold;
}
.rank-prices-compact .p-min { color: #4caf50; }
.rank-prices-compact .p-avg { color: #ffd700; }
.rank-prices-compact .p-max { color: #f44336; }

/* Estilos de controles de ordenamiento */
.sort-controls {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 10px;
    align-items: center;
}
.sort-btn {
    background: #333;
    border: 1px solid #555;
    color: #888;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9em;
    display: flex;
    align-items: center;
    gap: 5px;
    transition: all 0.2s;
}
.sort-btn:hover:not(:disabled) {
    background: #444;
    color: #fff;
    border-color: #666;
}
.sort-btn.active {
    background: #00bcd4;
    color: #fff;
    border-color: #00bcd4;
}
.sort-btn:disabled {
    opacity: 0.5;
    cursor: wait;
}
.sort-loader {
    display: inline-block;
    width: 20px;
    height: 20px;
}
.spinner {
    display: block;
    width: 16px;
    height: 16px;
    border: 2px solid rgba(0, 188, 212, 0.3);
    border-radius: 50%;
    border-top-color: #00bcd4;
    animation: spin 1s ease-in-out infinite;
}
@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Transiciones de lista */
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}
.list-leave-active {
  position: absolute; 
}
 </style>