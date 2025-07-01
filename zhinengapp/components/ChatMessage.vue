<template>
  <view class="message-container" :class="isUser ? 'user-message' : 'ai-message'">
    <view v-if="!isUser" class="ai-avatar">
      <image src="/static/images/ai-avatar.jpg" mode="aspectFill"></image>
    </view>
    <view v-else class="user-avatar">
      <image src="/static/images/user-avatar.jpg" mode="aspectFill"></image>
    </view>
    <view class="message-content" :class="isUser ? 'user-content' : 'ai-content'">
      <text selectable>{{ message }}</text>
      
      <!-- 消息时间 -->
      <view class="message-time" v-if="time">{{ time }}</view>
      
      <view class="message-tools" v-if="!isUser">
        <view class="tool-btn copy-btn" @click="copyText">
          <span class="iconfont icon-copy"></span>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  props: {
    message: {
      type: String,
      required: true
    },
    isUser: {
      type: Boolean,
      default: false
    },
    knowledge: {
      type: Array,
      default: () => []
    },
    time: {
      type: String,
      default: ''
    }
  },
  methods: {
    copyText() {
      uni.setClipboardData({
        data: this.message,
        success: () => {
          uni.showToast({
            title: '已复制到剪贴板',
            icon: 'success'
          });
        }
      });
    }
  }
}
</script>

<style>
.message-container {
  display: flex;
  margin-bottom: 40rpx;
}

.user-message {
  flex-direction: row-reverse;
}

.ai-message {
  flex-direction: row;
}

.ai-avatar, .user-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 40rpx;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.ai-avatar image, .user-avatar image {
  width: 100%;
  height: 100%;
}

.message-content {
  max-width: 75%;
  padding: 24rpx 30rpx;
  border-radius: 12rpx;
  word-break: break-all;
  font-size: 30rpx;
  line-height: 1.6;
}

.user-content {
  background-color: #e1edff;
  border-radius: 20rpx 4rpx 20rpx 20rpx;
  color: #333333;
  margin-right: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(53, 112, 236, 0.1);
}

.ai-content {
  background-color: #ffffff;
  border-radius: 4rpx 20rpx 20rpx 20rpx;
  color: #333333;
  margin-left: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.message-tools {
  display: flex;
  justify-content: flex-end;
  margin-top: 16rpx;
}

.tool-btn {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3570EC;
  margin-left: 16rpx;
}

/* 消息时间 */
.message-time {
  font-size: 22rpx;
  color: #999999;
  margin-top: 8rpx;
  text-align: right;
}

.iconfont {
  font-family: "iconfont" !important;
  font-size: 32rpx;
  font-style: normal;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style> 