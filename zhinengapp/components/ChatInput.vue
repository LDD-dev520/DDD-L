<template>
  <view class="chat-input-field">
    <input 
      class="input-field" 
      type="text" 
      v-model="inputText" 
      placeholder="有问题，尽管问" 
      confirm-type="send" 
      :disabled="disabled"
      @confirm="sendMessage"
    />
    <view class="send-btn" @click="sendMessage" v-if="inputText.trim().length > 0" :class="{ 'disabled': disabled }">
      <text class="iconfont icon-send"></text>
    </view>
  </view>
</template>

<script>
/**
 * 聊天输入组件
 * 负责用户文本输入并发送消息
 */
export default {
  props: {
    // 是否禁用输入
    disabled: {
      type: Boolean,
      default: false
    },
    // 输入框占位符文本
    placeholder: {
      type: String,
      default: '有问题，尽管问'
    }
  },
  
  data() {
    return {
      inputText: '',
    }
  },
  
  created() {
    // 监听再次提问事件
    this.registerEventListeners();
  },
  
  beforeDestroy() {
    // 移除事件监听
    this.unregisterEventListeners();
  },
  
  methods: {
    // 注册事件监听器
    registerEventListeners() {
      uni.$on('reask', this.handleReask);
    },
    
    // 取消注册事件监听器
    unregisterEventListeners() {
      uni.$off('reask', this.handleReask);
    },
    
    // 发送消息
    sendMessage() {
      // 验证输入是否有效
      if (!this.canSend()) return;
      
      const message = this.inputText.trim();
      this.$emit('send', message);
      this.clearInput();
    },
    
    // 检查是否可以发送消息
    canSend() {
      return !this.disabled && this.inputText.trim().length > 0;
    },
    
    // 处理再次提问
    handleReask(data) {
      if (data && data.question) {
        this.setInput(data.question);
      }
    },
    
    // 清空输入
    clearInput() {
      this.inputText = '';
    },
    
    // 设置输入内容
    setInput(text) {
      this.inputText = text || '';
    }
  }
}
</script>

<style>
.chat-input-field {
  flex: 1;
  display: flex;
  align-items: center;
  background-color: #f0f0f0;
  border-radius: 40rpx;
  padding: 0 20rpx;
}

.input-field {
  flex: 1;
  height: 80rpx;
  font-size: 30rpx;
  padding: 0 24rpx;
  background-color: transparent;
}

.send-btn {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 40rpx;
  background: linear-gradient(135deg, #3570EC, #5A7CFF);
  color: #FFFFFF;
  margin: 0 0 0 8rpx;
  box-shadow: 0 6rpx 16rpx rgba(53, 112, 236, 0.2);
  transition: all 0.3s;
}

.send-btn:active {
  transform: scale(0.95);
}

.send-btn.disabled {
  background: #cccccc;
  box-shadow: none;
}

.iconfont {
  font-family: "iconfont" !important;
  font-size: 32rpx;
  font-style: normal;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style> 