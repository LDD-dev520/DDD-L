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
export default {
  props: {
    disabled: {
      type: Boolean,
      default: false
    },
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
    uni.$on('reask', this.handleReask);
  },
  beforeDestroy() {
    // 移除事件监听
    uni.$off('reask', this.handleReask);
  },
  methods: {
    // 发送消息
    sendMessage() {
      if (!this.inputText.trim() || this.disabled) return;
      
      const message = this.inputText.trim();
      this.$emit('send', message);
      this.inputText = '';
    },
    
    // 处理再次提问
    handleReask(data) {
      if (data && data.question) {
        this.inputText = data.question;
      }
    },
    
    // 清空输入
    clearInput() {
      this.inputText = '';
    },
    
    // 设置输入内容
    setInput(text) {
      this.inputText = text;
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