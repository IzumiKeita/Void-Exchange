import { reactive, computed, watch } from 'vue';
import en from './locales/en';
import es from './locales/es';

const messages = {
  en,
  es
};

const state = reactive({
  locale: 'en' // Idioma por defecto (Requirement 2)
});

// Recuperar preferencia guardada (Requirement 2)
const savedLocale = localStorage.getItem('user-locale');
if (savedLocale && messages[savedLocale]) {
  state.locale = savedLocale;
}

// Persistencia y actualización del atributo lang (Requirement 2)
watch(
  () => state.locale,
  (newLocale) => {
    localStorage.setItem('user-locale', newLocale);
    document.documentElement.lang = newLocale;
  }
);

// Función de traducción (Requirement 3)
function t(key, args = {}) {
  const keys = key.split('.');
  let value = messages[state.locale];
  
  // Navegar por el objeto de traducciones
  for (const k of keys) {
    if (value && value[k]) {
      value = value[k];
    } else {
      // Fallback a EN si falta la clave (Requirement 5 - Retrocompatibilidad/Validación)
      if (state.locale !== 'en') {
         let fallback = messages['en'];
         for (const fbK of keys) {
            if (fallback && fallback[fbK]) {
               fallback = fallback[fbK];
            } else {
               console.warn(`[i18n] Missing key: ${key}`);
               return key;
            }
         }
         value = fallback;
      } else {
        console.warn(`[i18n] Missing key: ${key}`);
        return key;
      }
    }
  }

  // Interpolación simple de variables {name}
  if (typeof value === 'string') {
      for (const [argKey, argValue] of Object.entries(args)) {
          value = value.replace(`{${argKey}}`, argValue);
      }
  }
  
  return value;
}

export function useI18n() {
  return {
    locale: computed({
      get: () => state.locale,
      set: (value) => {
        if (messages[value]) {
          state.locale = value;
        }
      }
    }),
    t,
    availableLocales: Object.keys(messages)
  };
}
