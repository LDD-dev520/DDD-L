<script setup>
import { computed, ref } from 'vue'

// 使用props定义组件属性
const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  isUser: {
    type: Boolean,
    default: false
  }
})

// 显示/隐藏知识源
const showKnowledge = ref(false)

// 计算头像URL
const avatarSrc = computed(() => {
  return props.isUser 
    ? '/images/user-avatar.jpg' 
    : '/images/ai-avatar.jpg'
})

// 是否有知识源
const hasKnowledge = computed(() => {
  return props.message.usedKnowledge && 
         props.message.knowledgeItems && 
         props.message.knowledgeItems.length > 0
})

// 格式化时间戳
function formatTime(timestamp) {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  
  return `${hours}:${minutes}`
}

// 切换显示知识源
function toggleKnowledge() {
  if (hasKnowledge.value) {
    showKnowledge.value = !showKnowledge.value
  }
}
</script>

<template>
  <div class="chat-message" :class="{ 'user-message': isUser }">
    <div class="avatar">
      <div class="avatar-image" :class="{ 'user-avatar': isUser, 'ai-avatar': !isUser }"></div>
    </div>
    <div class="message-content">
      <div class="message-bubble" :class="{
        'user-bubble': isUser, 
        'ai-bubble': !isUser,
        'thinking': message.isThinking,
        'error': message.isError
      }">
        <p v-if="message.isThinking" class="thinking-animation">
          思考中<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
        </p>
        <template v-else>
          {{ message.content }}
        </template>
      </div>
      
      <div v-if="showKnowledge && hasKnowledge" class="knowledge-sources">
        <div class="knowledge-header">参考知识源:</div>
        <div v-for="(item, index) in message.knowledgeItems" :key="index" class="knowledge-item">
          {{ item }}
        </div>
      </div>
      
      <div class="message-meta">
        <span class="timestamp">{{ formatTime(message.timestamp) }}</span>
        <span 
          v-if="hasKnowledge" 
          class="knowledge-badge"
          @click="toggleKnowledge"
        >
          {{ showKnowledge ? '隐藏知识源' : '查看知识源' }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-message {
  display: flex;
  margin-bottom: 16px;
  align-items: flex-start;
}

.user-message {
  flex-direction: row-reverse;
}

.avatar {
  flex-shrink: 0;
  margin: 0 10px;
}

.avatar-image {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-size: cover;
  background-position: center;
}

.user-avatar {
  background-image: url('/images/user-avatar.jpg');
}

.ai-avatar {
  background-image: url('/images/ai-avatar.jpg');
}

.message-content {
  max-width: 70%;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 18px;
  word-break: break-word;
  white-space: pre-wrap;
  position: relative;
}

.user-bubble {
  background: linear-gradient(135deg, #3570EC, #5A7CFF);
  color: white;
  border-top-right-radius: 4px;
}

.ai-bubble {
  background-color: #f0f0f0;
  color: #333;
  border-top-left-radius: 4px;
}

.thinking {
  background-color: #e8e8e8;
  color: #666;
}

.error {
  background-color: #ffebee;
  color: #d32f2f;
}

.message-meta {
  font-size: 0.75rem;
  color: #888;
  margin-top: 4px;
  display: flex;
}

.timestamp {
  margin-right: 6px;
}

.knowledge-badge {
  color: #4080FF;
  cursor: pointer;
}

.knowledge-badge:hover {
  text-decoration: underline;
}

.knowledge-sources {
  margin-top: 8px;
  background-color: #f8f8f8;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 10px;
  font-size: 0.9em;
}

.knowledge-header {
  font-weight: bold;
  margin-bottom: 6px;
  color: #555;
}

.knowledge-item {
  padding: 4px 8px;
  background-color: #eef4ff;
  border-radius: 4px;
  margin-bottom: 4px;
}

/* 思考动画 */
.thinking-animation {
  display: flex;
  align-items: center;
}

.dot {
  animation: dotFade 1.4s infinite;
  opacity: 0;
  margin-left: 2px;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dotFade {
  0%, 60%, 100% { opacity: 0; }
  30% { opacity: 1; }
}
</style> 