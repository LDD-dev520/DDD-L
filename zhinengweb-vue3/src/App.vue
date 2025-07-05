<script setup>
import { ref, onMounted } from 'vue'
import api from './utils/api.js'

// 应用状态
const apiConnected = ref(false)
const apiChecking = ref(true)

// 检查API连接状态
async function checkApiConnection() {
  apiChecking.value = true
  try {
    const status = await api.getStatus()
    apiConnected.value = status && status.status === 'running'
    console.log('API连接状态:', apiConnected.value ? '已连接' : '未连接')
  } catch (error) {
    console.error('API连接检查失败:', error)
    apiConnected.value = false
  } finally {
    apiChecking.value = false
  }
}

// 应用初始化
onMounted(async () => {
  console.log('App initialized')
  
  // 初始化聊天历史
  try {
    const history = localStorage.getItem('chat_history')
    if (!history) {
      localStorage.setItem('chat_history', JSON.stringify([]))
    }
  } catch (error) {
    console.error('初始化历史记录失败:', error)
    localStorage.setItem('chat_history', JSON.stringify([]))
  }
  
  // 检查API连接
  await checkApiConnection()
})
</script>

<template>
  <header class="header">
    <div class="container">
      <h1>智能问答助手</h1>
      <nav>
        <router-link to="/">首页</router-link>
        <router-link to="/history">历史记录</router-link>
      </nav>
    </div>
  </header>

  <main class="container">
    <div v-if="apiChecking" class="api-status checking">
      正在检查API连接...
    </div>
    <div v-else-if="!apiConnected" class="api-status error">
      警告: 无法连接到后端API服务，请检查服务是否已启动
    </div>
    
    <router-view />
  </main>
</template>

<style>
/* 全局样式 */
:root {
  --primary-color: #4080FF;
  --primary-hover: #3570EC;
  --text-color: #333333;
  --bg-light: #f8f8f8;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background-color: var(--bg-light);
  color: var(--text-color);
  line-height: 1.6;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.header {
  background-color: var(--primary-color);
  color: white;
  padding: 1rem 0;
  margin-bottom: 2rem;
}

.header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

nav a {
  color: white;
  margin-left: 1rem;
  text-decoration: none;
}

nav a:hover, nav a.router-link-active {
  text-decoration: underline;
}

.api-status {
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
  text-align: center;
}

.api-status.checking {
  background-color: var(--bg-light);
  border: 1px solid #ddd;
}

.api-status.error {
  background-color: #fef2f2;
  border: 1px solid var(--error-color);
  color: var(--error-color);
}
</style> 