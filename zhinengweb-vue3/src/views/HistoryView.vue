<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api.js'

const router = useRouter()
const history = ref([])
const isLoading = ref(true)
const isDeleting = ref(false) // 删除操作状态

// 格式化时间戳为可读日期
function formatDate(timestamp) {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hour}:${minute}`
}

// 再次提问功能
function reaskQuestion(question) {
  // 全局事件总线模式在Vue 3中不再建议使用
  // 这里使用一个简单的localStorage解决方案
  localStorage.setItem('reask_question', question)
  router.push('/')
}

// 加载历史记录
async function loadHistory() {
  isLoading.value = true
  
  try {
    // 从本地存储加载历史记录
    const savedHistory = localStorage.getItem('chat_history')
    console.log('正在加载历史记录...')
    
    if (savedHistory) {
      try {
        const parsedHistory = JSON.parse(savedHistory)
        console.log('成功解析历史记录，数量:', parsedHistory.length)
        
        // 按时间倒序排列
        history.value = parsedHistory.sort((a, b) => b.timestamp - a.timestamp)
        console.log('历史记录已排序并加载到视图')
      } catch (parseError) {
        console.error('历史记录解析失败:', parseError)
        console.log('原始历史记录数据:', savedHistory.substring(0, 100) + '...')
        history.value = []
      }
    } else {
      console.log('未找到历史记录')
      history.value = []
    }
    
    // 检查API状态
    try {
      await api.getStatus()
    } catch (error) {
      console.error('API连接失败:', error)
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
    history.value = []
  } finally {
    isLoading.value = false
  }
}

// 清空全部历史记录
async function clearAllHistory() {
  if (isDeleting.value) return
  
  if (confirm('确定要清空全部历史记录吗？此操作无法撤销。')) {
    isDeleting.value = true
    
    try {
      // 清空历史记录
      localStorage.removeItem('chat_history')
      history.value = []
    } catch (error) {
      console.error('清空历史记录失败:', error)
      alert('清空历史记录失败，请稍后再试。')
    } finally {
      isDeleting.value = false
    }
  }
}

// 删除单个历史记录
function deleteHistoryItem(index) {
  if (isDeleting.value) return
  
  isDeleting.value = true
  
  try {
    // 获取当前历史记录
    const currentHistory = [...history.value]
    
    // 删除指定项
    currentHistory.splice(index, 1)
    
    // 更新本地存储
    localStorage.setItem('chat_history', JSON.stringify(currentHistory))
    
    // 更新视图
    history.value = currentHistory
  } catch (error) {
    console.error('删除历史记录失败:', error)
    alert('删除历史记录失败，请稍后再试。')
  } finally {
    isDeleting.value = false
  }
}

// 组件加载时获取历史记录
onMounted(() => {
  loadHistory()
})
</script>

<template>
      <div class="history-page">
    <div class="header">
      <h2>历史记录</h2>
    </div>
    
    <div class="clear-all-container">
      <button 
        @click="clearAllHistory" 
        class="clear-all-btn"
        :disabled="isDeleting || history.length === 0"
      >
        清空全部
      </button>
    </div>
    
    <div v-if="isLoading" class="loading">
      加载中...
    </div>
    
    <div v-else-if="history.length === 0" class="empty-history">
      <p>暂无历史记录</p>
    </div>
    
    <div v-else class="history-list">
      <div 
        v-for="(item, index) in history" 
        :key="index" 
        class="history-item"
      >
        <div class="item-header">
          <h3 class="question-label">问题:</h3>
          <span class="timestamp">{{ formatDate(item.timestamp) }}</span>
        </div>
        
        <p class="question-content">{{ item.question }}</p>
        
        <h3 class="answer-label">回答:</h3>
        <p class="answer-content">{{ item.answer }}</p>
        
        <div class="item-actions">
          <button 
            @click="reaskQuestion(item.question)"
            class="reask-btn"
          >
            再次提问
          </button>
          <button 
            @click="deleteHistoryItem(index)"
            class="delete-btn"
            :disabled="isDeleting"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.history-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
  color: var(--primary-color);
}

.loading,
.empty-history {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  color: #888;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.history-item {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.question-label {
  color: var(--primary-color);
  margin: 0;
}

.timestamp {
  font-size: 0.9rem;
  color: #888;
}

.question-content {
  padding-left: 10px;
  margin-bottom: 15px;
}

.answer-label {
  color: #059669;
  margin: 0 0 10px 0;
}

.answer-content {
  padding-left: 10px;
}

.item-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 15px;
}

.reask-btn {
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 0.9rem;
}

.reask-btn:hover {
  background-color: var(--primary-hover);
}

.delete-btn {
  border: none;
  background-color: #f44336;
  color: white;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-left: 10px;
}

.delete-btn:hover {
  background-color: #d32f2f;
}

.delete-btn:disabled {
  background-color: #ffcdd2;
  cursor: not-allowed;
}

.header {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 10px;
}

.clear-all-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.clear-all-btn {
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
  width: 120px;
}

.clear-all-btn:hover:not(:disabled) {
  background-color: #d32f2f;
}

.clear-all-btn:disabled {
  background-color: #ffcdd2;
  cursor: not-allowed;
}
</style> 