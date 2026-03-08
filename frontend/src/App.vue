<template>
  <LanguageSelector />
  <router-view></router-view>
  <ChatAssistant />
</template>

<script setup>
import ChatAssistant from './components/ChatAssistant.vue';
import LanguageSelector from './components/LanguageSelector.vue';
</script>

<style>
body { 
  font-family: 'Segoe UI', sans-serif; 
  background-color: #1a1a1a; 
  color: #ffffff; 
  margin: 0; 
} 
</style>
