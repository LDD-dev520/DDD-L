<script setup>
import { ref, onMounted, nextTick, computed, onBeforeUnmount, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import ChatMessage from '../components/ChatMessage.vue'
import ChatInput from '../components/ChatInput.vue'
import api from '../utils/api.js'

// 路由相关
const router = useRouter()

// 反应性状态
const messages = ref([])
const isProcessing = ref(false)
const userId = ref('user_' + Math.random().toString(36).substring(2, 9)) // 生成随机用户ID
const messagesContainer = ref(null) // 添加对消息容器的引用

// 历史记录配置
const MAX_HISTORY_ITEMS = 50 // 最大保留历史记录数量
const AUTO_CLEANUP_ENABLED = true // 是否启用自动清理

// 虚拟滚动相关状态
const visibleMessages = ref(new Set()) // 存储可见消息的ID
const observedElements = ref(new Map()) // 存储被观察的元素

// 滚动到底部的函数
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 获取API状态
async function checkApiStatus() {
  try {
    const status = await api.getStatus()
    console.log('API状态:', status)
    
    // 增强检查逻辑，只要成功返回响应就认为API在线
    if (status) {
      // 如果返回了任何响应，就认为服务器在线
      console.log('检测到API服务在线')
      return true
    }
    
    // 如果特别返回了status字段，检查其值
    if (status && status.status === 'running') {
      console.log('API服务状态正常')
      return true
    }
    
    return false
  } catch (error) {
    console.error('API状态检查失败:', error)
    return false
  }
}

  // 处理发送消息
async function handleSendMessage(text) {
  if (!text || isProcessing.value) return
  
  // 添加用户消息
  messages.value.push({
    content: text,
    isUser: true,
    timestamp: Date.now()
  })
  
  // 保存消息
  saveMessages()
  
  // 滚动到底部
  scrollToBottom()
  
  // 更新观察的元素
  nextTick(() => {
    observeMessageElements()
  })
  
  // 开始处理
  isProcessing.value = true
  
  try {
    // 添加思考中消息
    const thinkingIndex = messages.value.length
    messages.value.push({
      content: '思考中...',
      isUser: false,
      isThinking: true,
      timestamp: Date.now()
    })
    
    // 滚动到底部显示思考中状态
    scrollToBottom()
    
    // 调用后端API
    const response = await api.sendChat(userId.value, text)
    
    // 替换思考消息为实际回答
    if (response && response.success) {
      messages.value[thinkingIndex] = {
        content: response.answer,
        isUser: false,
        timestamp: Date.now(),
        usedKnowledge: response.used_knowledge,
        knowledgeItems: response.knowledge_items
      }
    } else {
      throw new Error('获取回答失败')
    }
    
    // 滚动到底部显示回答
    scrollToBottom()
  } catch (error) {
    console.error('处理消息失败:', error)
    
    // 添加错误消息
    messages.value.push({
      content: '抱歉，处理您的问题时出错。请稍后再试。',
      isUser: false,
      isError: true,
      timestamp: Date.now()
    })
    
    // 滚动到底部显示错误消息
    scrollToBottom()
  } finally {
    isProcessing.value = false
    saveMessages()
    // 更新观察的元素
    nextTick(() => {
      observeMessageElements()
    })
  }
}

// 清理历史记录
function cleanupHistory() {
  try {
    if (!AUTO_CLEANUP_ENABLED) return
    
    const savedHistory = localStorage.getItem('chat_history')
    if (savedHistory) {
      let history = JSON.parse(savedHistory)
      
      // 如果历史记录超过最大数量，只保留最近的记录
      if (history.length > MAX_HISTORY_ITEMS) {
        // 按时间排序，保留最近的记录
        history.sort((a, b) => b.timestamp - a.timestamp)
        history = history.slice(0, MAX_HISTORY_ITEMS)
        localStorage.setItem('chat_history', JSON.stringify(history))
        console.log(`历史记录已自动清理至 ${MAX_HISTORY_ITEMS} 条`)
      }
    }
  } catch (error) {
    console.error('清理历史记录失败:', error)
  }
}

// 创建新对话，清空当前消息
function createNewChat() {
  // 将当前对话保存到历史记录
  saveToHistory()
  
  // 重置消息和状态
  messages.value = []
  localStorage.removeItem('chat_messages') // 清空当前聊天缓存
  userId.value = 'user_' + Math.random().toString(36).substring(2, 9) // 生成新的用户ID
}

// 将当前对话保存到历史记录
function saveToHistory() {
  // 只有当有对话时才保存
  if (messages.value.length > 1) {
    try {
      console.log('尝试保存对话到历史记录，当前消息数量:', messages.value.length)
      
      // 从消息中提取问答对
      const pairs = []
      for (let i = 0; i < messages.value.length - 1; i++) {
        if (messages.value[i].isUser && !messages.value[i+1]?.isUser && !messages.value[i+1]?.isThinking) {
          console.log('找到有效的问答对:', 
                     {question: messages.value[i].content, 
                      answer: messages.value[i+1].content.substring(0, 20) + '...'})
          
          pairs.push({
            question: messages.value[i].content,
            answer: messages.value[i+1].content,
            timestamp: messages.value[i].timestamp
          })
          i++ // 跳过已处理的回答
        }
      }
      
      console.log('提取到的问答对数量:', pairs.length)
      
      if (pairs.length > 0) {
        // 读取现有历史记录
        let history = []
        const savedHistory = localStorage.getItem('chat_history')
        if (savedHistory) {
          history = JSON.parse(savedHistory)
          console.log('现有历史记录数量:', history.length)
        }
        
        // 添加新的对话记录
        history = [...pairs, ...history]
        
        // 保存更新后的历史记录
        localStorage.setItem('chat_history', JSON.stringify(history))
        console.log('历史记录已更新，新的历史记录数量:', history.length)
        
        // 清理过多的历史记录
        cleanupHistory()
      } else {
        console.log('没有找到有效的问答对，跳过保存')
      }
    } catch (error) {
      console.error('保存历史记录失败:', error)
    }
  } else {
    console.log('消息数量不足，跳过保存历史记录')
  }
}

// 保存当前消息到本地存储（临时缓存）
function saveMessages() {
  try {
    localStorage.setItem('chat_messages', JSON.stringify(messages.value))
  } catch (error) {
    console.error('保存消息失败:', error)
  }
}

// 组件加载时从本地存储获取消息
// 计算哪些消息需要渲染
const messagesToRender = computed(() => {
  // 如果消息不多，全部渲染
  if (messages.value.length < 30) {
    return messages.value
  }
  
  // 否则只渲染可见的消息和周围的几条
  const visibleIndices = Array.from(visibleMessages.value)
  if (visibleIndices.length === 0) {
    // 如果没有可见消息，默认显示最近的消息
    const end = messages.value.length
    const start = Math.max(0, end - 10)
    return messages.value.slice(start, end)
  }
  
  // 确定可见消息的范围
  const minIndex = Math.min(...visibleIndices)
  const maxIndex = Math.max(...visibleIndices)
  
  // 添加缓冲区域
  const bufferSize = 5
  const start = Math.max(0, minIndex - bufferSize)
  const end = Math.min(messages.value.length, maxIndex + bufferSize + 1)
  
  return messages.value.slice(start, end)
})

// 设置 Intersection Observer
function setupIntersectionObserver() {
  if (!messagesContainer.value) return
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      const messageId = entry.target.dataset.messageId
      
      if (entry.isIntersecting) {
        visibleMessages.value.add(parseInt(messageId))
      } else {
        visibleMessages.value.delete(parseInt(messageId))
      }
    })
  }, {
    root: messagesContainer.value,
    threshold: 0.1 // 10% 可见即算可见
  })
  
  return observer
}

// 观察消息元素
function observeMessageElements() {
  nextTick(() => {
    const observer = setupIntersectionObserver()
    if (!observer) return
    
    // 清理旧的观察
    observedElements.value.forEach((oldObserver, element) => {
      oldObserver.unobserve(element)
    })
    observedElements.value.clear()
    
    // 开始新的观察
    const messageElements = document.querySelectorAll('.message-item')
    messageElements.forEach(element => {
      observer.observe(element)
      observedElements.value.set(element, observer)
    })
  })
}

// 在组件加载时
onMounted(async () => {
  try {
    // 检查是否有需要再次提问的问题
    const reaskQuestion = localStorage.getItem('reask_question')
    
    // 每次加载组件时创建新聊天
    createNewChat()
    
    // 如果有需要再次提问的问题，发送它
    if (reaskQuestion) {
      localStorage.removeItem('reask_question')
      await handleSendMessage(reaskQuestion)
    }
    
    // 检查API状态
    const apiRunning = await checkApiStatus()
    console.log('API运行状态检查结果:', apiRunning)
    
    if (!apiRunning) {
      // 添加警告消息
      messages.value.push({
        content: '警告: API服务似乎未运行。请确保后端服务已启动。如果您确定后端服务已启动。',
        isUser: false,
        isError: true,
        timestamp: Date.now()
      })
      scrollToBottom()
      observeMessageElements()
    } else {
      console.log('API连接正常，可以开始聊天')
    }
  } catch (error) {
    console.error('初始化聊天失败:', error)
  }
})

// 组件即将卸载前保存历史
onBeforeUnmount(() => {
  saveToHistory()
})

// 每次激活组件时创建新聊天
onActivated(() => {
  createNewChat()
})
</script>

<template>
  <div class="home">
    <div class="chat-container">
      <div class="messages-area" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty-state">
          <p>欢迎使用智能问答助手</p>
          <p class="hint">有问题，尽管问!</p>
        </div>
        
        <!--要是用虚拟滚动就该把这里改一下  -->
        <div
          v-for="(message, index) in messages"
          :key="index"
          :data-message-id="index"
          class="message-item"
        >
          <ChatMessage
            v-if="messages.length < 30 || messagesToRender.includes(message)"
            :message="message"
            :is-user="message.isUser"
          />
          <div
            v-else
            class="message-placeholder"
            :class="{ 'user-placeholder': message.isUser }"
          ></div>
        </div>
      </div>
      
      <ChatInput
        @send="handleSendMessage"
        :disabled="isProcessing"
      />
      
      <div class="action-buttons">
        <button @click="createNewChat" class="new-chat-btn" :disabled="isProcessing || messages.length === 0">
          新对话
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.chat-container {
  width: 100%;
  max-width: 800px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.messages-area {
  height: 500px;
  overflow-y: auto;
  margin-bottom: 20px;
  padding: 10px;
}

.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #888;
}

.empty-state p {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.empty-state .hint {
  font-size: 1rem;
  color: #aaa;
}

.message-item {
  width: 100%;
}

.message-placeholder {
  height: 40px;
  margin: 8px 0;
  background-color: #f0f0f0;
  border-radius: 18px;
  opacity: 0.4;
}

.user-placeholder {
  margin-left: auto;
  width: 70%;
  background-color: rgba(53, 112, 236, 0.2);
}

.action-buttons {
  display: flex;
  justify-content: center;
  margin-top: 15px;
}

.new-chat-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #3570EC, #5A7CFF);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.new-chat-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #2560DC, #4A6DEF);
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(53, 112, 236, 0.3);
}

.new-chat-btn:disabled {
  background: #cccccc;
  cursor: not-allowed;
}
</style> 