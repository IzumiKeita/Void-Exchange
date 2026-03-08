import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import ItemDetail from '../views/ItemDetail.vue'
import Trends from '../views/Trends.vue'
import Ducats from '../views/Ducats.vue'
import Vault from '../views/Vault.vue'
import VaultWeapons from '../views/VaultWeapons.vue'
import TradingAdvisor from '../views/TradingAdvisor.vue'
import FullChat from '../views/FullChat.vue'
import VoidTrader from '../views/VoidTrader.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/item/:id',
    name: 'ItemDetail',
    component: ItemDetail
  },
  {
    path: '/trends',
    name: 'Trends',
    component: Trends
  },
  {
    path: '/void-trader',
    name: 'VoidTrader',
    component: VoidTrader
  },
  {
    path: '/ducats',
    name: 'Ducats',
    component: Ducats
  },
  {
    path: '/vault',
    name: 'Vault',
    component: Vault
  },
  {
    path: '/vault/weapons',
    name: 'VaultWeapons',
    component: VaultWeapons
  },
  {
    path: '/trading',
    name: 'TradingAdvisor',
    component: TradingAdvisor
  },
  {
    path: '/chat',
    name: 'FullChat',
    component: FullChat
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
