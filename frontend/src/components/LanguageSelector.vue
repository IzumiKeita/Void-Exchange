<template>
  <div class="lang-selector">
    <span 
      @click="setLocale('en')"
      :class="{ active: locale === 'en' }"
      class="lang-option"
      title="Switch to English"
    >EN</span>
    <span class="divider">|</span>
    <span 
      @click="setLocale('es')"
      :class="{ active: locale === 'es' }"
      class="lang-option"
      title="Cambiar a Español"
    >ES</span>
  </div>
</template>

<script setup>
import { useI18n } from '../i18n';
const { locale } = useI18n();

const setLocale = (lang) => {
  locale.value = lang;
}
</script>

<style scoped>
/* Estilos fijos en la esquina superior derecha (Requirement 1) */
.lang-selector {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  background: rgba(18, 18, 18, 0.85);
  backdrop-filter: blur(10px);
  padding: 8px 16px;
  border-radius: 30px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #e0e0e0;
  font-family: 'Roboto', sans-serif; /* Usar fuente del sistema si es posible */
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
}

.lang-selector:hover {
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6);
}

.lang-option {
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  opacity: 0.6;
  transition: all 0.3s ease;
  padding: 4px 8px;
  border-radius: 6px;
  user-select: none;
}

.lang-option:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.1);
}

/* Indicador visual de idioma activo (Requirement 1) */
.lang-option.active {
  opacity: 1;
  color: #4fc3f7; /* Azul neón suave */
  text-shadow: 0 0 12px rgba(79, 195, 247, 0.6);
  background: rgba(79, 195, 247, 0.1);
}

.divider {
  opacity: 0.3;
  font-size: 0.8rem;
}

/* Ajustes para móviles (Requirement 5) */
@media (max-width: 768px) {
  .lang-selector {
    top: 10px;
    right: 10px;
    padding: 6px 12px;
  }
  
  .lang-option {
    font-size: 0.8rem;
  }
}
</style>
