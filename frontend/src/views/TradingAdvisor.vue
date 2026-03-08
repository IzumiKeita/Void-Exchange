<template>
  <div class="trading-container">
    <div class="header">
      <h1>{{ t('trading.title') }}</h1>
      <p class="subtitle">{{ t('trading.subtitle') }}</p>
    </div>

    <div class="tabs">
      <button 
        :class="['tab-btn', { active: activeTab === 'ducats' }]" 
        @click="activeTab = 'ducats'"
      >
        {{ t('trading.tabs.ducats') }}
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'investment' }]" 
        @click="activeTab = 'investment'"
      >
        {{ t('trading.tabs.investment') }}
      </button>
    </div>

    <!-- Pestaña de Ducados -->
    <div v-if="activeTab === 'ducats'" class="tab-content">
      <div class="filters">
        <label>
          <input type="radio" v-model="ducatStrategy" value="sell_trash" />
          {{ t('trading.strategies.sellTrash') }}
        </label>
        <label>
          <input type="radio" v-model="ducatStrategy" value="buy_baro" />
          {{ t('trading.strategies.buyBaro') }}
        </label>
      </div>

      <p class="strategy-desc" v-if="ducatStrategy === 'sell_trash'" v-html="t('trading.strategies.sellDesc')"></p>
      <p class="strategy-desc" v-else v-html="t('trading.strategies.buyDesc')"></p>

      <div v-if="loadingDucats" class="loading">{{ t('trading.loading') }}</div>
      
      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ t('trading.table.item') }}</th>
              <th>{{ t('trading.table.price') }}</th>
              <th>{{ t('trading.table.ducats') }}</th>
              <th>{{ t('trading.table.ratio') }}</th>
              <th>{{ t('trading.table.action') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredDucats" :key="item.id">
              <td class="item-cell">
                <img :src="getImageUrl(item.thumb)" v-if="item.thumb" class="item-thumb" />
                <span class="item-name">{{ item.item_name }}</span>
              </td>
              <td class="highlight">{{ item.plat_price.toFixed(1) }}</td>
              <td>{{ item.ducats }}</td>
              <td :class="getRatioClass(item.ducats_per_plat)">
                {{ item.ducats_per_plat.toFixed(1) }}
              </td>
              <td>
                <button @click="openOrders(item)" class="market-btn">
                  {{ t('trading.table.viewMarket') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pestaña de Inversiones -->
    <div v-if="activeTab === 'investment'" class="tab-content">
      <div class="investment-intro">
        <h3>{{ t('trading.investment.title') }}</h3>
        <p>{{ t('trading.investment.desc') }}</p>
      </div>

      <div v-if="loadingVault" class="loading">{{ t('trading.investment.loading') }}</div>

      <div v-else class="cards-grid">
        <div v-for="item in investmentItems" :key="item.slug" class="invest-card">
           <div class="card-badge">{{ t('trading.investment.badge') }}</div>
           <img :src="getImageUrl(item.thumb)" v-if="item.thumb" class="card-img" />
           <h4>{{ item.name }}</h4>
           <div class="card-actions">
             <button @click="openOrders(item)" class="market-btn full-width">
               {{ t('trading.investment.action') }}
             </button>
           </div>
        </div>
        <div v-if="investmentItems.length === 0" class="empty-msg">
          {{ t('trading.investment.empty') }}
        </div>
      </div>
    </div>

    <!-- Modal de Órdenes -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content large-modal">
        <div class="modal-header">
          <h2>{{ selectedItem?.item_name || selectedItem?.name }}</h2>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        
        <div v-if="loadingOrders" class="loading-orders">
          <div class="spinner"></div>
          {{ t('trading.modal.loading') }}
        </div>
        
        <div v-else class="modal-body-scroll">
            
            <!-- Details Grid -->
            <div class="details-top">
                <div class="main-info">
                    <img :src="getImageUrl(itemDetails?.info?.thumb || selectedItem?.thumb)" class="main-thumb" />
                    <div class="info-text">
                        <div class="tags">
                            <span v-for="tag in itemDetails?.info?.tags" :key="tag" class="tag">{{ tag }}</span>
                        </div>
                        <p class="desc">{{ itemDetails?.info?.description }}</p>
                        
                        <div class="ai-section">
                           <button @click="analyzeItem" class="ai-btn" :disabled="loadingAnalysis">
                              <span v-if="loadingAnalysis">{{ t('trading.modal.ai.analyzing') }}</span>
                              <span v-else>{{ t('trading.modal.ai.analyze') }}</span>
                           </button>
                           
                           <div v-if="analysisResult" class="ai-result" :style="{ borderColor: analysisResult.color }">
                              <div class="ai-header" :style="{ color: analysisResult.color }">
                                 <strong>{{ analysisResult.verdict }}</strong> (Score: {{ analysisResult.score }})
                              </div>
                              <ul class="ai-reasons">
                                 <li v-for="(reason, idx) in analysisResult.reasons" :key="idx">{{ reason }}</li>
                              </ul>
                           </div>
                        </div>
                    </div>
                </div>

                <div v-if="itemDetails?.components?.length" class="components-section">
                    <h4>{{ t('trading.modal.components') }}</h4>
                    <div class="components-list">
                        <div v-for="comp in itemDetails.components" :key="comp.url_name" class="comp-card" @click="openOrders({url_name: comp.url_name, item_name: comp.item_name})">
                            <img :src="getImageUrl(comp.thumb)" />
                            <div class="comp-meta">
                                <span class="comp-name">{{ comp.item_name }}</span>
                                <span class="comp-qty" v-if="comp.quantity > 1">x{{ comp.quantity }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Stats -->
            <div class="stats-row" v-if="displayStats">
                <div class="stat-card">
                    <label>{{ t('trading.modal.stats.volume') }}</label>
                    <div class="value">{{ displayStats.volume }}</div>
                </div>
                 <div class="stat-card">
                    <label>{{ t('trading.modal.stats.min') }}</label>
                    <div class="value text-green">{{ displayStats.min_price }} <small>Pt</small></div>
                </div>
                 <div class="stat-card">
                    <label>{{ t('trading.modal.stats.max') }}</label>
                    <div class="value">{{ displayStats.max_price }} <small>Pt</small></div>
                </div>
                 <div class="stat-card">
                    <label>{{ t('trading.modal.stats.avg') }}</label>
                    <div class="value text-blue">{{ displayStats.avg_price }} <small>Pt</small></div>
                </div>
            </div>

            <!-- Chart -->
            <div class="chart-row" v-if="chartSeries.length">
                <h4>{{ t('trading.modal.chartTitle') }}</h4>
                <apexchart type="line" height="250" :options="chartOptions" :series="chartSeries"></apexchart>
            </div>

            <!-- Orders -->
            <div class="orders-row">
                <div class="orders-col">
                    <h4>{{ t('trading.modal.sellers') }}</h4>
                    <table class="compact-table">
                        <thead><tr><th>User</th><th>Info</th><th>Qty</th><th>Pt</th></tr></thead>
                        <tbody>
                            <tr v-for="(o, idx) in selectedOrders.sell" :key="'s'+idx">
                                <td><span class="status-dot" :class="o.user.status"></span> {{ o.user.name }}</td>
                                <td>
                                    <span v-if="o.rank !== undefined && o.rank !== null" class="rank-badge">R{{ o.rank }}</span>
                                    <span v-if="o.subtype" class="subtype-badge">{{ o.subtype }}</span>
                                </td>
                                <td>{{ o.quantity }}</td>
                                <td class="text-green font-bold">{{ o.platinum }}</td>
                            </tr>
                             <tr v-if="!selectedOrders.sell.length"><td colspan="4" class="text-center">{{ t('ducats.empty') }}</td></tr>
                        </tbody>
                    </table>
                </div>
                <div class="orders-col">
                    <h4>{{ t('trading.modal.buyers') }}</h4>
                     <table class="compact-table">
                        <thead><tr><th>User</th><th>Info</th><th>Qty</th><th>Pt</th></tr></thead>
                        <tbody>
                            <tr v-for="(o, idx) in selectedOrders.buy" :key="'b'+idx">
                                <td><span class="status-dot" :class="o.user.status"></span> {{ o.user.name }}</td>
                                <td>
                                    <span v-if="o.rank !== undefined && o.rank !== null" class="rank-badge">R{{ o.rank }}</span>
                                    <span v-if="o.subtype" class="subtype-badge">{{ o.subtype }}</span>
                                </td>
                                <td>{{ o.quantity }}</td>
                                <td class="text-green font-bold">{{ o.platinum }}</td>
                            </tr>
                            <tr v-if="!selectedOrders.buy.length"><td colspan="4" class="text-center">{{ t('ducats.empty') }}</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
        
        <div class="modal-footer">
          <button @click="openMarket(selectedItem?.url_name || selectedItem?.slug)" class="market-link-btn">
            {{ t('trading.modal.viewMarket') }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios';
import { useI18n } from '../i18n';
import { watch, computed } from 'vue';

export default {
  name: 'TradingAdvisor',
  setup() {
    const { t, locale } = useI18n();
    return { t, locale };
  },
  data() {
    return {
      activeTab: 'ducats',
      ducatStrategy: 'buy_baro', // 'buy_baro' (high ratio) or 'sell_trash' (low ratio)
      ducatItems: [],
      vaultItems: [],
      loadingDucats: false,
      loadingVault: false,
      
      // Modal state
      showModal: false,
      loadingOrders: false,
      selectedItem: null,
      selectedOrders: { sell: [], buy: [] },
      itemDetails: null,
      
      // AI Analysis
      loadingAnalysis: false,
      analysisResult: null,
      
      // Chart
      chartSeries: [],
      
      API_URL: 'http://localhost:5001'
    };
  },
  computed: {
    chartOptions() {
      return {
        chart: {
          height: 300,
          toolbar: { show: false },
          background: 'transparent',
          stacked: false
        },
        theme: { mode: 'dark' },
        stroke: { width: [3, 0], curve: 'smooth' }, // Line for price, none for bar
        plotOptions: {
           bar: { columnWidth: '50%', borderRadius: 4 }
        },
        fill: {
          type: ['gradient', 'solid'],
          gradient: {
            shadeIntensity: 1,
            opacityFrom: 0.7,
            opacityTo: 0.3,
            stops: [0, 90, 100]
          },
          solid: { opacity: 0.3 }
        },
        dataLabels: { enabled: false },
        xaxis: {
          type: 'datetime',
          tooltip: { enabled: false },
          axisBorder: { show: false },
          axisTicks: { show: false }
        },
        yaxis: [
          {
            seriesName: this.t('trading.modal.chart.avgPrice'),
            labels: { formatter: (val) => val.toFixed(0) },
            title: { text: this.t('trading.modal.chart.plat'), style: { color: '#00e676' } },
            axisTicks: { show: true },
            axisBorder: { show: true, color: '#00e676' },
            labels: { style: { colors: '#00e676' } }
          },
          {
            seriesName: this.t('trading.modal.chart.volume'),
            opposite: true,
            labels: { formatter: (val) => val.toFixed(0) },
            title: { text: this.t('trading.modal.chart.volume'), style: { color: '#00b0ff' } },
            axisTicks: { show: true },
            axisBorder: { show: true, color: '#00b0ff' },
            labels: { style: { colors: '#00b0ff' } }
          }
        ],
        tooltip: {
          theme: 'dark',
          shared: true,
          intersect: false,
          x: { format: 'dd MMM yyyy' }
        },
        colors: ['#00e676', '#00b0ff'],
        legend: { show: true, position: 'top', horizontalAlign: 'left' }
      };
    },
    filteredDucats() {
      // Clone array to sort
      let items = [...this.ducatItems];
      
      if (this.ducatStrategy === 'buy_baro') {
        // High Ducats per Plat -> Good to buy for Ducats
        // Sort Descending by Ratio
        return items.sort((a, b) => b.ducats_per_plat - a.ducats_per_plat).slice(0, 50);
      } else {
        // Low Ducats per Plat -> Expensive items with low ducat value
        // Sort Ascending by Ratio (but filter out 0 price)
        return items
            .filter(i => i.plat_price > 5) // Ignore trash
            .sort((a, b) => a.ducats_per_plat - b.ducats_per_plat)
            .slice(0, 50);
      }
    },
    investmentItems() {
      // Filter active items that are "next_to_vault"
      if (!this.vaultItems.active) return [];
      return this.vaultItems.active.filter(i => i.next_to_vault);
    },
    displayStats() {
      if (!this.itemDetails || !this.itemDetails.stats) return null;
      const s = this.itemDetails.stats;
      if (s.is_ranked && s.rank_max) return s.rank_max;
      return s;
    }
  },
  mounted() {
    this.fetchDucats();
    this.fetchVault();
    
    // Watch for locale changes to re-render chart data with correct labels
    this.$watch('locale', () => {
       if (this.itemDetails) {
          this.prepareChartData();
       }
    });
  },
  methods: {
    async fetchDucats() {
      this.loadingDucats = true;
      try {
        const res = await axios.get(`${this.API_URL}/api/ducats`);
        if (Array.isArray(res.data)) {
          this.ducatItems = res.data;
        } else if (res.data && res.data.data) {
          this.ducatItems = res.data.data;
        }
      } catch (e) {
        console.error("Error fetching ducats", e);
      } finally {
        this.loadingDucats = false;
      }
    },
    async fetchVault() {
      this.loadingVault = true;
      try {
        const res = await axios.get(`${this.API_URL}/api/vault`);
        this.vaultItems = res.data;
      } catch (e) {
        console.error("Error fetching vault", e);
      } finally {
        this.loadingVault = false;
      }
    },
    async openOrders(item) {
      this.selectedItem = item;
      this.showModal = true;
      this.loadingOrders = true;
      this.selectedOrders = { sell: [], buy: [] };
      this.itemDetails = null;
      this.chartSeries = [];
      
      const slug = item.url_name || item.slug;
      
      try {
        const [ordersRes, detailsRes] = await Promise.all([
             axios.get(`${this.API_URL}/api/items/orders/${slug}`),
             axios.get(`${this.API_URL}/api/items/detail/${slug}`)
        ]);
        
        this.selectedOrders = ordersRes.data;
        this.itemDetails = detailsRes.data;
        
        this.prepareChartData();
        
      } catch (e) {
        console.error("Error fetching data", e);
      } finally {
        this.loadingOrders = false;
      }
    },
    prepareChartData() {
      if (!this.itemDetails || !this.itemDetails.history) return;
      
      const history = this.itemDetails.history;
      let dataPoints = [];
      let seriesName = this.t('trading.modal.chart.avgPrice');
      
      // Determine which history to use
      if (history.general) {
        dataPoints = history.general;
      } else if (history.rank_max) {
        dataPoints = history.rank_max;
        seriesName = this.t('trading.modal.chart.maxRank');
      } else if (history.intact) {
        dataPoints = history.intact; // For relics
        seriesName = this.t('trading.modal.chart.intact');
      } else {
        // Fallback: take first available key
        const keys = Object.keys(history).filter(k => k !== 'min_rank' && k !== 'max_rank' && k !== 'refinements');
        if (keys.length > 0) {
           dataPoints = history[keys[0]];
           seriesName = keys[0];
        }
      }
      
      if (!dataPoints || !Array.isArray(dataPoints)) return;
      
      // Sort by date just in case
      dataPoints.sort((a, b) => new Date(a.datetime) - new Date(b.datetime));
      
      const priceSeries = dataPoints.map(p => ({
        x: new Date(p.datetime).getTime(),
        y: p.avg_price
      }));

      const volumeSeries = dataPoints.map(p => ({
        x: new Date(p.datetime).getTime(),
        y: p.volume || 0
      }));
      
      this.chartSeries = [
        {
          name: seriesName,
          type: 'area',
          data: priceSeries
        },
        {
          name: this.t('trading.modal.chart.volume'),
          type: 'bar',
          data: volumeSeries
        }
      ];
    },
    closeModal() {
      this.showModal = false;
      this.selectedItem = null;
    },
    openMarket(slug) {
      window.open(`https://warframe.market/items/${slug}`, '_blank');
    },
    getRatioClass(ratio) {
      if (ratio > 15) return 'ratio-excellent'; // 15 ducats per plat (e.g. 15 duc item for 1p)
      if (ratio > 10) return 'ratio-good';
      if (ratio < 3) return 'ratio-bad'; // selling 100 duc item for 50p is 2.0 ratio (bad for ducats, good for plat)
      return '';
    },
    async analyzeItem() {
      if (!this.selectedItem) return;
      this.loadingAnalysis = true;
      this.analysisResult = null;
      
      const slug = this.selectedItem.url_name || this.selectedItem.slug;
      
      try {
        const res = await axios.get(`${this.API_URL}/api/analysis/${slug}`);
        if (res.data.status === 'success') {
            this.analysisResult = res.data.analysis;
        } else {
            alert(res.data.message);
        }
      } catch (e) {
        console.error("Error analyzing item", e);
        alert(this.t('trading.modal.errorAnalysis'));
      } finally {
        this.loadingAnalysis = false;
      }
    },
    getImageUrl(path) {
        if (!path) return '';
        if (typeof path !== 'string') return '';
        if (path.startsWith('http')) return path;
        return `${this.API_URL}/api/images/${path.split('/').pop()}`;
    }
  }
};
</script>

<style scoped>
.trading-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  color: #e0e0e0;
}

.ai-section {
    margin-top: 15px;
}

.ai-btn {
    background: linear-gradient(45deg, #7c4dff, #448aff);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    transition: transform 0.2s;
}

.ai-btn:hover {
    transform: scale(1.05);
}

.ai-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.ai-result {
    margin-top: 10px;
    padding: 10px;
    background: rgba(0, 0, 0, 0.3);
    border-left: 4px solid #7c4dff;
    border-radius: 0 4px 4px 0;
}

.ai-header {
    font-size: 1.1rem;
    margin-bottom: 5px;
}

.ai-reasons {
    margin: 0;
    padding-left: 20px;
    font-size: 0.9rem;
    color: #ccc;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: #1e1e24;
  border: 1px solid #444;
  border-radius: 12px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  color: #ffd700;
}

.close-btn {
  background: none;
  border: none;
  color: #aaa;
  font-size: 28px;
  cursor: pointer;
}

.close-btn:hover {
  color: #fff;
}

.loading-orders {
  padding: 50px;
  text-align: center;
  font-size: 1.2rem;
  color: #aaa;
}

.orders-container {
  display: flex;
  padding: 20px;
  gap: 20px;
  overflow-y: auto;
}

.orders-column {
  flex: 1;
  background: #25252b;
  border-radius: 8px;
  padding: 10px;
}

.orders-column h3 {
  text-align: center;
  margin-top: 0;
  color: #ddd;
  font-size: 1rem;
  border-bottom: 1px solid #333;
  padding-bottom: 10px;
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
}

.orders-table th {
  text-align: left;
  padding: 8px;
  color: #888;
  font-size: 0.85rem;
}

.orders-table td {
  padding: 8px;
  border-bottom: 1px solid #333;
  font-size: 0.9rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #555;
}

.status-dot.ingame { background: #a335ee; box-shadow: 0 0 5px #a335ee; } /* Purple for ingame */
.status-dot.online { background: #4caf50; box-shadow: 0 0 5px #4caf50; }

.price-cell {
  color: #ffd700;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 4px;
}

.no-data {
  text-align: center;
  color: #666;
  padding: 20px;
}

.modal-footer {
  padding: 15px;
  border-top: 1px solid #333;
  text-align: right;
}

.market-link-btn {
  background: none;
  border: 1px solid #555;
  color: #aaa;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.market-link-btn:hover {
  border-color: #ffd700;
  color: #ffd700;
}


.subtitle {
  color: #aaa;
}

.tabs {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
}

.tab-btn {
  background: #333;
  color: #aaa;
  border: none;
  padding: 10px 20px;
  font-size: 1.1rem;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s;
}

.tab-btn.active {
  background: #6200ea;
  color: white;
  box-shadow: 0 4px 10px rgba(98, 0, 234, 0.3);
}

.filters {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 15px;
  background: #252525;
  padding: 15px;
  border-radius: 8px;
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
}

.filters label {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.strategy-desc {
  text-align: center;
  color: #bbb;
  margin-bottom: 20px;
  font-style: italic;
}

.table-container {
  background: #1e1e1e;
  border-radius: 8px;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th, .data-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #333;
}

.data-table th {
  background: #252525;
  color: #fff;
  font-weight: 600;
}

.item-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-thumb {
  width: 32px;
  height: 32px;
  border-radius: 4px;
}

.highlight {
  color: #00e676;
  font-weight: bold;
}

.ratio-excellent { color: #00e676; font-weight: bold; } /* Green */
.ratio-good { color: #76ff03; } /* Light Green */
.ratio-bad { color: #ff5252; } /* Red */

.market-btn {
  background: #444;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.market-btn:hover {
  background: #6200ea;
}

/* Investment Cards */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.invest-card {
  background: #252525;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  position: relative;
  border: 1px solid #333;
  transition: transform 0.2s;
}

.invest-card:hover {
  transform: translateY(-5px);
  border-color: #ffd700;
}

.card-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #ff9800;
  color: #000;
  font-size: 0.7rem;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 4px;
}

.card-img {
  width: 80px;
  height: 80px;
  margin-bottom: 10px;
}

.full-width {
  width: 100%;
  margin-top: 10px;
}

.loading {
  text-align: center;
  padding: 40px;
  font-size: 1.2rem;
  color: #aaa;
}

.plat-icon {
  color: #a0b3c5;
  font-weight: bold;
  font-size: 0.8em;
  margin-left: 2px;
  vertical-align: middle;
}

/* New Modal Styles */
.large-modal {
  max-width: 900px;
  width: 95%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-body-scroll {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.details-top {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .details-top {
    grid-template-columns: 1fr;
  }
}

.main-info {
  display: flex;
  gap: 15px;
  background: #252525;
  padding: 15px;
  border-radius: 8px;
}

.main-thumb {
  width: 80px;
  height: 80px;
  object-fit: contain;
}

.info-text {
  flex: 1;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 10px;
}

.tag {
  background: #333;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #aaa;
}

.desc {
  font-size: 0.9rem;
  color: #ccc;
  line-height: 1.4;
}

.components-section {
  background: #252525;
  padding: 15px;
  border-radius: 8px;
}

.components-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.comp-card {
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.comp-card:hover {
  transform: scale(1.05);
}

.comp-card img {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.comp-meta {
  font-size: 0.7rem;
  color: #aaa;
  line-height: 1.2;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: #252525;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.stat-card label {
  display: block;
  font-size: 0.8rem;
  color: #aaa;
  margin-bottom: 5px;
}

.stat-card .value {
  font-size: 1.2rem;
  font-weight: bold;
}

.chart-row {
  background: #252525;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.orders-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.compact-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.compact-table th {
  text-align: left;
  padding: 8px;
  color: #aaa;
  border-bottom: 1px solid #333;
}

.compact-table td {
  padding: 8px;
  border-bottom: 1px solid #333;
}

.rank-badge {
    background: #444;
    color: #fff;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.75rem;
    margin-right: 4px;
}

.subtype-badge {
    background: #3d5afe;
    color: #fff;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.75rem;
    text-transform: capitalize;
}

.text-green { color: #00e676; }
.text-blue { color: #00b0ff; }
.text-center { text-align: center; }
.font-bold { font-weight: bold; }

.spinner {
  border: 4px solid #333;
  border-top: 4px solid #6200ea;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
