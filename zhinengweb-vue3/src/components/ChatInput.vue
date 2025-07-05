<script setup>
import { ref, onMounted } from 'vue'

// 使用defineProps和defineEmits宏定义组件属性和事件
const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: '有问题，尽管问'
  }
})

const emit = defineEmits(['send'])

// 响应式数据
const inputText = ref('')

// 发送消息
function sendMessage() {
  if (!inputText.value.trim() || props.disabled) return
  
  emit('send', inputText.value.trim())
  inputText.value = ''
}

// 检查是否有需要再次提问的问题
onMounted(() => {
  // 检查localStorage中是否有待提问的问题
  const reaskQuestion = localStorage.getItem('reask_question')
  if (reaskQuestion) {
    inputText.value = reaskQuestion
    localStorage.removeItem('reask_question') // 清除
  }
})

// 清空输入
function clearInput() {
  inputText.value = ''
}

// 设置输入内容
function setInput(text) {
  inputText.value = text
}

// 暴露方法给父组件
defineExpose({
  clearInput,
  setInput
})
</script>

<template>
  <div class="chat-input">
    <input 
      type="text" 
      v-model="inputText" 
      :placeholder="placeholder" 
      :disabled="disabled"
      @keyup.enter="sendMessage"
      class="input-field"
    />
    <button 
      class="send-btn"
      :class="{ 'disabled': disabled || !inputText.trim() }"
      @click="sendMessage"
      :disabled="disabled || !inputText.trim()"
    >
      发送
    </button>
  </div>
</template>

<style scoped>
.chat-input {
  display: flex;
  width: 100%;
  border-radius: 24px;
  background-color: #f0f0f0;
  padding: 6px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.input-field {
  flex: 1;
  border: none;
  outline: none;
  background-color: transparent;
  padding: 12px 16px;
  font-size: 16px;
  color: #333;
}

.input-field::placeholder {
  color: #999;
}

.input-field:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.send-btn {
  border: none;
  background: linear-gradient(135deg, #3570EC, #5A7CFF);
  color: white;
  border-radius: 20px;
  padding: 0 20px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}

.send-btn:hover:not(.disabled) {
  background: linear-gradient(135deg, #2560DC, #4A6DEF);
}

.send-btn:active:not(.disabled) {
  transform: scale(0.98);
}

.send-btn.disabled {
  background: #cccccc;
  cursor: not-allowed;
}
</style> 