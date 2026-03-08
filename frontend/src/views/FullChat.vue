<template>
  <div class="full-chat-container">
    <div class="chat-main">
      <div class="chat-header">
        <h1>{{ t('chat.title') }}</h1>
        <p>{{ t('chat.subtitle') }}</p>
      </div>
      
      <div class="messages-area" ref="messagesContainer">
        <div v-for="(msg, index) in messages" :key="index" :class="['message-wrapper', msg.role]">
          <div class="avatar">
            {{ msg.role === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="message-content">
            {{ msg.text }}
          </div>
        </div>
        
        <div v-if="isLoading" class="message-wrapper model loading">
          <div class="avatar">🤖</div>
          <div class="message-content">{{ t('chat.typing') }}</div>
        </div>
      </div>

      <div class="input-area">
        <div class="input-wrapper">
          <input 
            v-model="newMessage" 
            @keyup.enter="sendMessage" 
            :placeholder="t('chat.placeholder')"
            :disabled="isLoading"
            ref="inputField"
          />
          <button @click="sendMessage" :disabled="isLoading || !newMessage.trim()">
            <span v-if="!isLoading">➤</span>
            <span v-else>...</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';
import { useI18n } from '../i18n';

const { t } = useI18n();
const route = useRoute();
const messages = ref([]);
const apiHistory = ref([]);
const newMessage = ref('');
const isLoading = ref(false);
const messagesContainer = ref(null);
const inputField = ref(null);

onMounted(async () => {
  // Recuperar historial pasado por el router o localStorage
  const storedMessages = sessionStorage.getItem('chatMessages');
  const storedApiHistory = sessionStorage.getItem('chatApiHistory');
  
  if (storedMessages && storedApiHistory) {
    messages.value = JSON.parse(storedMessages);
    apiHistory.value = JSON.parse(storedApiHistory);
  } else {
    // Mensaje inicial por defecto si no hay historial
    messages.value = [
      { role: 'model', text: t('chat.welcome') }
    ];
  }
  
  scrollToBottom();
  inputField.value?.focus();
});

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const saveState = () => {
  sessionStorage.setItem('chatMessages', JSON.stringify(messages.value));
  sessionStorage.setItem('chatApiHistory', JSON.stringify(apiHistory.value));
};

const sendMessage = async () => {
  if (!newMessage.value.trim() || isLoading.value) return;

  const userMsg = newMessage.value.trim();
  messages.value.push({ role: 'user', text: userMsg });
  newMessage.value = '';
  isLoading.value = true;
  scrollToBottom();
  saveState();

  try {
    const response = await axios.post('http://localhost:5001/api/ai/chat', {
      message: userMsg,
      history: apiHistory.value
    });

    const botResponse = response.data.response;
    messages.value.push({ role: 'model', text: botResponse });
    
    apiHistory.value.push({ role: 'user', parts: [userMsg] });
    apiHistory.value.push({ role: 'model', parts: [botResponse] });
    saveState();

  } catch (error) {
    console.error('Error en chat:', error);
    let errorMsg = 'Lo siento, hubo un error al procesar tu mensaje.';
    
    if (error.response) {
        if (error.response.data && error.response.data.error) {
            errorMsg = `Error del servidor: ${error.response.data.error}`;
        } else {
            errorMsg = `Error del servidor (${error.response.status})`;
        }
    } else if (error.request) {
        errorMsg = 'Error de conexión: No se pudo contactar con el servidor.';
    }
    
    messages.value.push({ role: 'model', text: errorMsg });
    saveState();
  } finally {
    isLoading.value = false;
    scrollToBottom();
  }
};
</script>

<style scoped>
.full-chat-container {
  height: calc(100vh - 60px); /* Ajustar según altura de navbar si existe */
  background-color: #121212;
  display: flex;
  justify-content: center;
  padding: 20px;
  box-sizing: border-box;
}

.chat-main {
  width: 100%;
  max-width: 900px;
  background-color: #1e1e1e;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  border: 1px solid #333;
  overflow: hidden;
}

.chat-header {
  padding: 20px;
  background-color: #252525;
  border-bottom: 1px solid #333;
  text-align: center;
}

.chat-header h1 {
  color: #00C0FF;
  margin: 0 0 5px 0;
  font-size: 1.5rem;
}

.chat-header p {
  color: #888;
  margin: 0;
  font-size: 0.9rem;
}

.messages-area {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-wrapper {
  display: flex;
  gap: 15px;
  max-width: 80%;
}

.message-wrapper.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-wrapper.model {
  align-self: flex-start;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #333;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.user .avatar {
  background-color: #0056b3;
}

.model .avatar {
  background-color: #00C0FF;
  color: #000;
}

.message-content {
  padding: 15px 20px;
  border-radius: 18px;
  font-size: 1rem;
  line-height: 1.5;
  white-space: pre-wrap;
  background-color: #2a2a2a;
  color: #ddd;
}

.user .message-content {
  background-color: #00C0FF;
  color: #000;
  border-top-right-radius: 4px;
}

.model .message-content {
  background-color: #333;
  border-top-left-radius: 4px;
}

.input-area {
  padding: 20px;
  background-color: #252525;
  border-top: 1px solid #333;
}

.input-wrapper {
  display: flex;
  gap: 10px;
  background-color: #1a1a1a;
  padding: 8px;
  border-radius: 30px;
  border: 1px solid #444;
}

.input-wrapper:focus-within {
  border-color: #00C0FF;
  box-shadow: 0 0 0 2px rgba(0, 192, 255, 0.2);
}

.input-wrapper input {
  flex: 1;
  background: none;
  border: none;
  padding: 12px 20px;
  color: white;
  font-size: 1rem;
  outline: none;
}

.input-wrapper button {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  border: none;
  background-color: #00C0FF;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.input-wrapper button:hover:not(:disabled) {
  transform: scale(1.05);
}

.input-wrapper button:disabled {
  background-color: #444;
  cursor: not-allowed;
}
</style>