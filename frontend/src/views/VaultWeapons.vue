<template>
  <div class="vault-container">
    <div class="header-section">
      <div class="title-group">
        <h1>{{ t('vault.titleWeapons') }}</h1>
        <div class="vault-nav">
          <router-link to="/vault" class="vault-nav-btn">{{ t('vault.nav.warframes') }}</router-link>
          <router-link to="/vault/weapons" class="vault-nav-btn active">{{ t('vault.nav.weapons') }}</router-link>
        </div>
      </div>
      <div class="controls">
        <button @click="$router.push('/')" class="btn-back">{{ t('vault.backDashboard') }}</button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>{{ t('vault.loadingWeapons') }}</p>
    </div>

    <div v-else class="vault-content">
      <!-- Sección: Activos (Farmables) -->
      <section class="vault-section active-section">
        <div class="section-header">
          <h2>{{ t('vault.sections.active.title') }}</h2>
          <span class="badge active-badge">{{ vaultData.active.length }} {{ t('vault.items') }}</span>
        </div>
        <p class="section-desc">{{ t('vault.sections.active.descWeapons') }}</p>
        
        <div class="cards-grid">
          <div v-for="item in vaultData.active" :key="item.slug" class="item-card active-card" :class="{ 'next-vault': item.next_to_vault }">
            <div class="card-image">
               <img :src="getImageUrl(item.thumb)" :alt="item.name" @error="handleImageError">
               <div v-if="item.next_to_vault" class="vault-warning">{{ t('vault.cards.warning') }}</div>
            </div>
            <div class="card-info">
              <h3>{{ item.name }}</h3>
              <button @click="goToDetail(item.slug)" class="btn-detail">{{ t('vault.cards.viewMarket') }}</button>
            </div>
          </div>
        </div>
      </section>

      <!-- Sección: Resurgimiento (Varzia) -->
      <section class="vault-section resurgence-section" v-if="vaultData.resurgence.length > 0">
        <div class="section-header">
          <h2>{{ t('vault.sections.resurgence.title') }}</h2>
          <span class="badge resurgence-badge">{{ vaultData.resurgence.length }} {{ t('vault.items') }}</span>
        </div>
        <p class="section-desc">{{ t('vault.sections.resurgence.descWeapons') }}</p>
        
        <div class="cards-grid">
          <div v-for="item in vaultData.resurgence" :key="item.slug" class="item-card resurgence-card">
            <div class="card-image">
               <img :src="getImageUrl(item.thumb)" :alt="item.name" @error="handleImageError">
            </div>
            <div class="card-info">
              <h3>{{ item.name }}</h3>
              <button @click="goToDetail(item.slug)" class="btn-detail">{{ t('vault.cards.viewMarket') }}</button>
            </div>
          </div>
        </div>
      </section>

      <!-- Sección: Bóveda (Vaulted) -->
      <section class="vault-section vaulted-section">
        <div class="section-header">
          <h2>{{ t('vault.sections.vaulted.title') }}</h2>
          <span class="badge vaulted-badge">{{ vaultData.vaulted.length }} {{ t('vault.items') }}</span>
        </div>
        <p class="section-desc">{{ t('vault.sections.vaulted.descWeapons') }}</p>
        
        <!-- Buscador para Vaulted -->
        <input v-model="searchVaulted" :placeholder="t('vault.searchPlaceholderWeapons')" class="search-input">

        <div class="cards-grid compact-grid">
          <div v-for="item in filteredVaulted" :key="item.slug" class="item-card vaulted-card">
            <div class="card-image small">
               <img :src="getImageUrl(item.thumb)" :alt="item.name" @error="handleImageError">
            </div>
            <div class="card-info">
              <h3>{{ item.name }}</h3>
              <button @click="goToDetail(item.slug)" class="btn-detail small-btn">{{ t('vault.cards.view') }}</button>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from '../i18n';

export default {
  name: 'VaultWeapons',
  setup() {
    const { t } = useI18n();
    const router = useRouter();
    const vaultData = ref({ active: [], resurgence: [], vaulted: [] });
    const loading = ref(true);
    const searchVaulted = ref('');

    const API_URL = 'http://localhost:5001/api'; 

    const loadVaultData = async () => {
      try {
        loading.value = true;
        const response = await fetch(`${API_URL}/vault/weapons`);
        if (!response.ok) throw new Error('Error cargando datos de bóveda de armas');
        const data = await response.json();
        vaultData.value = data;
      } catch (error) {
        console.error(error);
      } finally {
        loading.value = false;
      }
    };

    const getImageUrl = (thumb) => {
      if (!thumb) return '';
      if (thumb.startsWith('http')) return thumb;
      return `${API_URL}/images/${thumb}`;
    };

    const handleImageError = (e) => {
      e.target.src = 'https://via.placeholder.com/128x128.png?text=No+Image';
    };

    const goToDetail = (slug) => {
      router.push({ name: 'ItemDetail', params: { id: slug } });
    };

    const filteredVaulted = computed(() => {
      if (!searchVaulted.value) return vaultData.value.vaulted;
      const term = searchVaulted.value.toLowerCase();
      return vaultData.value.vaulted.filter(i => i.name.toLowerCase().includes(term));
    });

    onMounted(() => {
      loadVaultData();
    });

    return {
      t,
      vaultData,
      loading,
      searchVaulted,
      filteredVaulted,
      getImageUrl,
      handleImageError,
      goToDetail
    };
  }
}
</script>

<style scoped>
.vault-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  color: #e0e0e0;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  background: #1e1e1e;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}

.title-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.header-section h1 {
  margin: 0;
  color: #ffd700; /* Gold */
}

.vault-nav {
  display: flex;
  gap: 10px;
  margin-top: 5px;
}

.vault-nav-btn {
  background: #333;
  color: #aaa;
  text-decoration: none;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 0.9em;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.vault-nav-btn:hover {
  background: #444;
  color: white;
}

.vault-nav-btn.active {
  background: #ffd700;
  color: #1e1e1e;
  font-weight: bold;
}

.btn-back {
  background: #444;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-back:hover {
  background: #555;
}

.vault-section {
  background: #1e1e1e;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  border: 1px solid #333;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.section-desc {
  color: #aaa;
  margin-bottom: 20px;
}

.badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.9em;
  font-weight: bold;
}

.active-badge { background: #2e7d32; color: white; }
.resurgence-badge { background: #d84315; color: white; }
.vaulted-badge { background: #424242; color: #bdbdbd; }

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.compact-grid {
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
}

.item-card {
  background: #2a2a2a;
  border-radius: 10px;
  overflow: hidden;
  transition: transform 0.2s;
  border: 1px solid #333;
}

.item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.5);
}

.active-card { border-top: 3px solid #4caf50; }
.resurgence-card { border-top: 3px solid #ff5722; }
.vaulted-card { border-top: 3px solid #757575; }

.card-image {
  height: 140px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #222;
  position: relative;
}

.card-image.small {
  height: 100px;
}

.card-image img {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.vault-warning {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 0, 0, 0.8);
  color: white;
  text-align: center;
  font-size: 0.8em;
  padding: 2px;
}

.card-info {
  padding: 15px;
  text-align: center;
}

.card-info h3 {
  margin: 0 0 10px 0;
  font-size: 1em;
  color: #fff;
}

.btn-detail {
  background: #00bcd4;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
}

.btn-detail:hover {
  background: #00acc1;
}

.small-btn {
  padding: 4px 8px;
  font-size: 0.9em;
}

.search-input {
  width: 100%;
  max-width: 300px;
  padding: 10px;
  margin-bottom: 20px;
  background: #333;
  border: 1px solid #555;
  color: white;
  border-radius: 4px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #ffd700;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
