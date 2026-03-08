<template>
  <div class="chat-widget" v-if="!isFullChatRoute">
    <!-- Botón flotante -->
    <button v-if="!isOpen" @click="toggleChat" class="chat-toggle-btn">
      {{ t('chat.toggle') }}
    </button>

    <!-- Ventana de Chat -->
    <div v-else class="chat-window">
      <div class="chat-header">
        <h3 @click="expandToFullChat" class="clickable-header">{{ t('chat.windowTitle') }}</h3>
        <button @click="toggleChat" class="close-btn">×</button>
      </div>
      
      <div class="chat-messages" ref="messagesContainer">
        <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
          <div class="message-content">{{ msg.text }}</div>
        </div>
        <div v-if="isLoading" class="message model loading">
          {{ t('chat.typing') }}
        </div>
      </div>

      <div class="chat-input">
        <input 
          v-model="newMessage" 
          @keyup.enter="sendMessage" 
          :placeholder="t('chat.placeholder')"
          :disabled="isLoading"
        />
        <button @click="sendMessage" :disabled="isLoading || !newMessage.trim()">➤</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from '../i18n';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();

const isOpen = ref(false);
const isLoading = ref(false);
const newMessage = ref('');
const messages = ref([
  { role: 'model', text: t('chat.welcome') }
]);

const apiHistory = ref([]);

// Ocultar widget en la vista de chat completo
const isFullChatRoute = computed(() => route.path === '/chat');

// Sincronizar estado con sessionStorage al montar
onMounted(() => {
  try {
    const storedMessages = sessionStorage.getItem('chatMessages');
    const storedApiHistory = sessionStorage.getItem('chatApiHistory');
    
    if (storedMessages) {
      messages.value = JSON.parse(storedMessages);
    }
    if (storedApiHistory) {
      apiHistory.value = JSON.parse(storedApiHistory);
    }
  } catch (e) {
    console.error("Error loading chat history from storage:", e);
    // Clear potentially corrupted storage
    sessionStorage.removeItem('chatMessages');
    sessionStorage.removeItem('chatApiHistory');
  }
});

// Guardar estado cada vez que cambia
watch([messages, apiHistory], () => {
  sessionStorage.setItem('chatMessages', JSON.stringify(messages.value));
  sessionStorage.setItem('chatApiHistory', JSON.stringify(apiHistory.value));
}, { deep: true });

const toggleChat = () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value) scrollToBottom();
};

const expandToFullChat = () => {
  // El estado ya se guarda automáticamente por el watcher
  isOpen.value = false; // Cerrar widget
  router.push('/chat');
};

const scrollToBottom = async () => {
  await nextTick();
  const container = document.querySelector('.chat-messages');
  if (container) container.scrollTop = container.scrollHeight;
};

const sendMessage = async () => {
  if (!newMessage.value.trim() || isLoading.value) return;

  const userMsg = newMessage.value.trim();
  messages.value.push({ role: 'user', text: userMsg });
  newMessage.value = '';
  isLoading.value = true;
  scrollToBottom();

  try {
    // Preparar payload base
    const payload = {
      message: userMsg,
      history: apiHistory.value
    };

    // Si estamos en una página de detalle de ítem, adjuntar contexto
    let contextStr = null;
    
    if (route.path.startsWith('/item/')) {
        contextStr = sessionStorage.getItem('activeItemContext');
    } else if (route.path === '/void-trader') {
        contextStr = sessionStorage.getItem('activeVoidTraderContext');
    } else {
        // Si no es un ítem específico, intentar cargar contexto del dashboard
        contextStr = sessionStorage.getItem('activeDashboardContext');
    }

    if (contextStr) {
        try {
            payload.context = JSON.parse(contextStr);
        } catch (e) {
            console.warn("Error parsing context", e);
        }
    }

    const response = await axios.post('http://localhost:5001/api/ai/chat', payload);

    const botResponse = response.data.response;
    messages.value.push({ role: 'model', text: botResponse });
    
    apiHistory.value.push({ role: 'user', parts: [userMsg] });
    apiHistory.value.push({ role: 'model', parts: [botResponse] });

  } catch (error) {
    console.error('Error en chat:', error);
    let errorMsg = t('chat.errorGeneric');
    
    if (error.response) {
        if (error.response.data && error.response.data.error) {
            errorMsg = t('chat.errorServer', { error: error.response.data.error });
        } else {
            errorMsg = t('chat.errorServer', { error: error.response.status });
        }
    } else if (error.request) {
        errorMsg = t('chat.errorConnection');
    }
    
    messages.value.push({ role: 'model', text: errorMsg });
  } finally {
    isLoading.value = false;
    scrollToBottom();
  }
};
</script>

<style scoped>
/* Estilos anteriores se mantienen igual */
.chat-widget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  font-family: 'Segoe UI', sans-serif;
}

.clickable-header {
  cursor: pointer;
  transition: color 0.2s;
}

.clickable-header:hover {
  color: white !important;
  text-decoration: underline;
}

/* ... resto de estilos igual ... */
.chat-toggle-btn {
  background-color: #00C0FF;
  color: white;
  border: none;
  border-radius: 50px;
  padding: 15px 25px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s;
}

.chat-toggle-btn:hover {
  transform: scale(1.05);
}

.chat-window {
  width: 350px;
  height: 500px;
  background-color: #1e1e1e;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.5);
  border: 1px solid #333;
  overflow: hidden;
}

.chat-header {
  background-color: #2a2a2a;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #333;
}

.chat-header h3 {
  margin: 0;
  font-size: 16px;
  color: #00C0FF;
}

.close-btn {
  background: none;
  border: none;
  color: #aaa;
  font-size: 24px;
  cursor: pointer;
}

.chat-messages {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message {
  max-width: 80%;
  padding: 10px 15px;
  border-radius: 15px;
  font-size: 14px;
  line-height: 1.4;
  white-space: pre-wrap;
}

.message.user {
  align-self: flex-end;
  background-color: #00C0FF;
  color: white;
  border-bottom-right-radius: 2px;
}

.message.model {
  align-self: flex-start;
  background-color: #333;
  color: #ddd;
  border-bottom-left-radius: 2px;
}

.message.loading {
  font-style: italic;
  color: #888;
}

.chat-input {
  padding: 15px;
  background-color: #2a2a2a;
  display: flex;
  gap: 10px;
  border-top: 1px solid #333;
}

.chat-input input {
  flex: 1;
  padding: 10px;
  border-radius: 20px;
  border: 1px solid #444;
  background-color: #1a1a1a;
  color: white;
  outline: none;
}

.chat-input input:focus {
  border-color: #00C0FF;
}

.chat-input button {
  background-color: #00C0FF;
  color: white;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-input button:disabled {
  background-color: #444;
  cursor: not-allowed;
}
</style>
