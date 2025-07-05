<template>
  <view class="container">
    <!-- 状态栏占位符 - 用于适配手机顶部状态栏 -->
    <view class="status-bar-placeholder" :style="{ height: statusBarHeight + 'px' }"></view>
    
    <!-- 顶部栏 -->
    <view class="status-bar">
      <!-- 历史图标 -->
      <view class="history-button" @tap="openHistory">
        <text class="iconfont icon-history"></text>
      </view>
      
      <!-- 标题 -->
      <view class="app-title">
        <text>智能问答助手</text>
      </view>
      
      <!-- 清空按钮 -->
      <view class="clear-button" @tap="clearChat">
        <text class="iconfont icon-delete"></text>
      </view>
    </view>
    
    <!-- 聊天区域 -->
    <scroll-view class="chat-container" scroll-y="true" :scroll-top="scrollTop" @scrolltoupper="loadMoreHistory">
      <view class="chat-list">
        <!-- 使用 ChatMessage 组件显示消息 -->
        <ChatMessage
          v-for="(msg, index) in chatMessages"
          :key="index"
          :message="msg.content"
          :isUser="msg.isUser"
          :knowledge="msg.knowledge || []"
          :time="msg.time"
        />
      </view>
      <view v-if="isThinking" class="thinking-indicator">
        <text>正在思考</text>
        <view class="thinking-dots">
          <text class="dot">.</text>
          <text class="dot">.</text>
          <text class="dot">.</text>
        </view>
      </view>
    </scroll-view>
    
    <!-- 底部输入区域，使用 ChatInput 组件 -->
    <view class="input-container">
      <!-- 语音输入按钮 -->
      <view class="voice-input-wrapper">
        <button 
          class="action-button voice-button" 
          :class="{'recording': isRecording}" 
          @touchstart.prevent="startRecord" 
          @touchend.prevent="stopRecord"
          @touchcancel.prevent="cancelRecord"
          @touchmove.prevent="moveRecord"
          :disabled="isThinking"
        >
          <text class="iconfont" :class="isRecording ? 'icon-mic' : 'icon-voice'"></text>
        </button>
      </view>
      
      <!-- 使用 ChatInput 组件 -->
      <ChatInput 
        @send="handleSendMessage" 
        :disabled="isThinking || isRecording"
        placeholder="有问题，尽管问"
        ref="chatInput"
      />
    </view>
    
    <!-- 录音提示 -->
    <view class="recording-tip" v-if="isRecording">
      <view class="recording-tip-inner">
        <view class="recording-icon" :class="{'cancel': isCancelRecording}">
          <text class="iconfont" :class="isCancelRecording ? 'icon-delete' : 'icon-mic'"></text>
        </view>
        <text class="recording-text">{{ isCancelRecording ? '松开手指，取消发送' : '松开手指，发送语音' }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import * as api from '@/utils/api.js';
import * as speech from '@/utils/speech.js';
import { formatTime } from '@/utils/utils.js';
import * as Storage from '@/utils/storage.js';
import ChatInput from '@/components/ChatInput.vue';
import ChatMessage from '@/components/ChatMessage.vue';

export default {
  components: {
    ChatInput,
    ChatMessage
  },
  
  data() {
    return {
      userInput: '',
      chatMessages: [],
      isRecording: false,
      isThinking: false,
      scrollTop: 0,
      config: {
        useKnowledge: true,
        temperature: 0.7,
        maxTokens: 2000
      },
      isCancelRecording: false,
      touchStartY: 0,
      statusBarHeight: 0
    };
  },
  
  computed: {
    canSend() {
      return !this.isThinking && !this.isRecording && this.userInput && this.userInput.trim().length > 0;
    }
  },
  
  created() {
    // 获取状态栏高度
    this.getStatusBarHeight();
    
    // 初始化配置
    this.loadConfig();
    
    // 加载聊天历史
    this.loadChatHistory();
    
    // 确保chatMessages是一个数组
    if (!Array.isArray(this.chatMessages)) {
      console.warn('chatMessages不是数组，初始化为空数组');
      this.chatMessages = [];
    }
    
    // 添加欢迎消息（如果没有消息）
    if (this.chatMessages.length === 0) {
      this.addAIMessage('您好，我是智能助手小吕，有什么问题都可以问我哦');
    }
    
    // 监听重新提问事件
    uni.$on('reask', (data) => {
      if (data && data.question) {
        this.userInput = data.question;
      }
    });
  },
  
  onLoad() {
    // 初始化页面
    this.initPage();
  },
  
  onUnload() {
    console.log('页面卸载，清理资源');
    // 页面卸载时清理事件监听器
    uni.$off('reask');
    
    // 取消所有正在进行的操作
    if (this.isRecording) {
      this.cancelRecord();
    }
    
    if (this.isThinking) {
      this.isThinking = false;
    }
    
    // 保存聊天历史
    this.saveChatHistory();
  },
  
  methods: {
    // 获取状态栏高度
    getStatusBarHeight() {
      try {
        const app = getApp();
        if (app.globalData && app.globalData.statusBarHeight) {
          this.statusBarHeight = app.globalData.statusBarHeight;
        } else {
          // 如果全局变量中没有，尝试获取
          uni.getSystemInfo({
            success: (res) => {
              this.statusBarHeight = res.statusBarHeight || 0;
            }
          });
        }
      } catch (e) {
        console.error('获取状态栏高度失败:', e);
        this.statusBarHeight = 0;
      }
    },
    
    // 初始化页面
    async initPage() {
      try {
        // 确保chatMessages是一个数组
        if (!Array.isArray(this.chatMessages)) {
          console.log('初始化页面: chatMessages不是数组，重新初始化为空数组');
          this.chatMessages = [];
        }
        
        // 初始化录音管理器
        speech.initRecorder();
      } catch (error) {
        console.error('初始化页面失败:', error);
      }
    },
    
    // 开始录音
    async startRecord(e) {
      console.log('开始录音按钮被点击');
      if (this.isRecording || this.isThinking) {
        console.log('当前正在录音或思考中，无法开始新录音');
        return;
      }
      
      try {
        // 记录触摸起始位置并初始化录音状态
        this.initRecordingState(e);
        
        // 开始录音
        console.log('设置录音状态为true');
        this.isRecording = true;
        
        // 尝试开始录音
        await speech.startRecording();
        
        // 提供触觉反馈
        this.provideTactileFeedback();
      } catch (error) {
        this.handleRecordingError(error);
      }
    },
    
    // 初始化录音状态
    initRecordingState(e) {
      if (e && e.touches && e.touches[0]) {
        this.touchStartY = e.touches[0].clientY;
      } else {
        this.touchStartY = 0;
        console.warn('无法获取触摸位置信息');
      }
      this.isCancelRecording = false;
    },
    
    // 提供触觉反馈
    provideTactileFeedback() {
      try {
        uni.vibrateShort();
      } catch (vibError) {
        console.log('震动反馈失败，但不影响录音', vibError);
      }
    },
    
    // 处理录音错误
    handleRecordingError(error) {
      console.error('开始录音失败:', error);
      this.isRecording = false;
      
      // 显示错误提示
      uni.showToast({
        title: '录音启动失败，请检查权限',
        icon: 'none',
        duration: 2000
      });
    },
    
    // 手指移动
    moveRecord(e) {
      if (!this.isRecording) return;
      
      try {
        // 计算手指移动距离，向上移动超过50像素则取消录音
        if (e && e.touches && e.touches[0]) {
          const touchMoveY = e.touches[0].clientY;
          const moveDistance = this.touchStartY - touchMoveY;
          
          // 如果向上移动超过50像素，显示取消提示
          this.isCancelRecording = moveDistance > 50;
        }
      } catch (error) {
        console.error('处理手指移动事件失败:', error);
      }
    },
    
    // 取消录音
    cancelRecord() {
      if (!this.isRecording) return;
      
      // 停止录音但不处理
      speech.stopRecording().then(() => {
        console.log('录音已取消');
        this.isRecording = false;
        this.isCancelRecording = false;
        
        uni.showToast({
          title: '已取消录音',
          icon: 'none'
        });
      }).catch(error => {
        console.error('取消录音失败:', error);
        this.isRecording = false;
        this.isCancelRecording = false;
      });
    },
    
    // 停止录音并识别
    async stopRecord() {
      console.log('停止录音按钮被松开');
      if (!this.isRecording) {
        console.log('当前不在录音状态，无需停止');
        return;
      }
      
      try {
        // 如果是取消状态，则取消录音
        if (this.isCancelRecording) {
          console.log('检测到上滑取消手势，取消录音');
          this.cancelRecord();
          return;
        }
        
        this.provideTactileFeedback();
        
        // 停止录音并获取文件路径
        const filePath = await this.stopAndGetRecordingFile();
        if (!filePath) return;
        
        // 处理语音识别
        await this.processVoiceRecognition(filePath);
      } catch (error) {
        console.error('停止录音失败:', error);
        this.isRecording = false;
        
        uni.showToast({
          title: '录音处理失败',
          icon: 'none'
        });
      }
    },
    
    // 停止录音并获取文件路径
    async stopAndGetRecordingFile() {
      console.log('停止录音并获取文件路径');
      const filePath = await speech.stopRecording();
      this.isRecording = false;
      
      if (!filePath) {
        console.error('未获取到录音文件路径');
        throw new Error('未获取到录音文件');
      }
      
      console.log('获取到录音文件路径:', filePath);
      return filePath;
    },
    
    // 处理语音识别
    async processVoiceRecognition(filePath) {
      // 显示思考状态
      this.isThinking = true;
      
      try {
        uni.showLoading({
          title: '正在处理语音...',
          mask: true
        });
        
        // 调用语音识别API
        const recognitionResult = await speech.recognizeVoice(filePath);
        console.log('语音识别结果:', recognitionResult);
        
        // 隐藏加载提示
        uni.hideLoading();
        
        if (recognitionResult && recognitionResult.text) {
          this.handleRecognitionSuccess(recognitionResult.text);
        } else {
          uni.showToast({
            title: '未能识别语音内容',
            icon: 'none'
          });
        }
      } catch (error) {
        this.handleRecognitionError(error);
      } finally {
        this.isThinking = false;
      }
    },
    
    // 处理语音识别成功
    handleRecognitionSuccess(text) {
      // 将识别结果设置到输入框
      if (this.$refs.chatInput) {
        this.$refs.chatInput.setInput(text);
      } else {
        this.userInput = text;
      }
      
      // 自动发送识别结果
      setTimeout(() => {
        this.handleSendMessage(text);
      }, 300);
    },
    
    // 处理语音识别错误
    handleRecognitionError(error) {
      console.error('语音识别失败:', error);
      uni.hideLoading();
      
      uni.showToast({
        title: '语音识别失败，请重试',
        icon: 'none'
      });
    },
    
    // 发送文本消息
    async sendMessage() {
      console.log('尝试发送消息，canSend:', this.canSend, '输入内容:', this.userInput);
      
      if (this.isThinking || this.isRecording) {
        console.log('当前正在思考或录音中，无法发送');
        return;
      }
      
      const question = this.userInput.trim();
      if (!question) {
        console.log('输入内容为空，无法发送');
        return;
      }
      
      // 添加用户消息
      this.addUserMessage(question);
      
      // 清空输入框
      this.userInput = '';
      
      // 显示思考状态
      this.isThinking = true;
      
      try {
        // 调用API获取回答
        const result = await api.getAnswer(question, {
          temperature: this.config.temperature,
          max_tokens: this.config.maxTokens,
          use_knowledge: this.config.useKnowledge
        });
        
        // 添加AI回答
        this.addAIMessage(result.answer, result.knowledge_items);
      } catch (error) {
        console.error('获取回答失败:', error);
        uni.showToast({
          title: error.message || '获取回答失败',
          icon: 'none'
        });
        // 如果发生错误，添加一个默认回答
        this.addAIMessage('抱歉，我遇到了一些问题，无法回答您的问题。');
      } finally {
        this.isThinking = false;
      }
    },
    
    // 添加用户消息
    addUserMessage(content) {
      this.ensureChatMessagesIsArray();
      
      const message = this.createMessage(content, true);
      this.addMessageToChat(message);
    },
    
    // 添加AI消息
    addAIMessage(content, knowledgeItems = []) {
      this.ensureChatMessagesIsArray();
      
      // 确保content不为空
      if (!content || content.trim() === '') {
        content = '抱歉，我暂时无法回答这个问题。';
      }
      
      const message = this.createMessage(content, false, knowledgeItems);
      this.addMessageToChat(message);
      
      // 调试输出
      console.log('AI回答内容:', content);
    },
    
    // 创建消息对象
    createMessage(content, isUser, knowledgeItems = []) {
      return {
        isUser: isUser,
        content: content,
        time: formatTime(new Date()),
        knowledge: isUser ? [] : (knowledgeItems || [])
      };
    },
    
    // 添加消息到聊天列表
    addMessageToChat(message) {
      this.chatMessages.push(message);
      this.saveChatHistory();
      this.scrollToBottom();
    },
    
    // 滚动到底部
    scrollToBottom() {
      this.$nextTick(() => {
        const query = uni.createSelectorQuery().in(this);
        query.select('.chat-list').boundingClientRect(data => {
          if (data) {
            this.scrollTop = data.height + 1000; // 确保滚动到底部
          }
        }).exec();
      });
    },
    
    // 加载更多历史消息
    loadMoreHistory() {
      // 可以实现加载更多历史消息的逻辑
      console.log('加载更多历史消息');
    },
    
    // 保存聊天历史
    saveChatHistory() {
      try {
        this.ensureChatMessagesIsArray();
        
        // 只保留最近的20条消息
        const recentMessages = this.chatMessages.slice(-20);
        console.log('保存聊天历史，条数:', recentMessages.length);
        
        // 使用Storage工具类保存
        Storage.setStorage('chat_history', recentMessages);
        
        // 保存最后一条对话到历史记录
        this.saveLastConversationToHistory(recentMessages);
      } catch (error) {
        console.error('保存聊天历史失败:', error);
      }
    },
    
    // 确保chatMessages是数组
    ensureChatMessagesIsArray() {
      if (!Array.isArray(this.chatMessages)) {
        console.error('chatMessages不是数组，重新初始化为空数组');
        this.chatMessages = [];
      }
    },
    
    // 保存最后一条对话到历史
    saveLastConversationToHistory(messages) {
      if (messages.length < 2) return;
      
      const lastUserMsg = messages.slice().reverse().find(msg => msg.isUser);
      const lastAiMsg = messages.slice().reverse().find(msg => !msg.isUser);
      
      if (lastUserMsg && lastAiMsg) {
        Storage.saveChatHistory({
          question: lastUserMsg.content,
          answer: lastAiMsg.content,
          time: Date.now(),
          knowledge: lastAiMsg.knowledge || []
        });
      }
    },
    
    // 加载聊天历史
    loadChatHistory() {
      try {
        // 使用Storage工具类加载
        const history = Storage.getStorage('chat_history', []);
        
        // 确保chatMessages始终是一个数组
        if (history && Array.isArray(history)) {
          this.chatMessages = history;
        } else {
          console.log('历史记录不是数组或为空，初始化为空数组');
          this.chatMessages = [];
        }
      } catch (error) {
        console.error('加载聊天历史失败:', error);
        // 出错时确保chatMessages是一个数组
        this.chatMessages = [];
      }
    },
    
    // 加载配置
    loadConfig() {
      try {
        const config = uni.getStorageSync('app_config');
        if (config) {
          this.config = { ...this.config, ...config };
        }
      } catch (error) {
        console.error('加载配置失败:', error);
      }
    },
    
    // 打开历史记录页面
    openHistory() {
      uni.navigateTo({
        url: '/pages/history/history'
      });
    },
    
    // 清空当前聊天
    clearChat() {
      uni.showModal({
        title: '清空聊天',
        content: '确定要清空当前的聊天记录吗？',
        success: (res) => {
          if (res.confirm) {
            this.chatMessages = [];
            Storage.setStorage('chat_history', []);
            this.addAIMessage('您好，我是智能助手小吕，有什么问题都可以问我哦');
            uni.showToast({
              title: '聊天已清空',
              icon: 'success'
            });
          }
        }
      });
    },
    
    // 处理发送消息（由 ChatInput 组件触发）
    async handleSendMessage(message) {
      if (!message || message.trim() === '') return;
      
      // 添加用户消息
      this.addUserMessage(message);
      
      // 获取AI回答
      await this.fetchAIResponse(message);
    },
    
    // 获取AI回答
    async fetchAIResponse(message) {
      // 显示思考状态
      this.isThinking = true;
      
      try {
        // 调用API获取回答
        const result = await api.getAnswer(message, {
          temperature: this.config.temperature,
          max_tokens: this.config.maxTokens,
          use_knowledge: this.config.useKnowledge
        });
        
        // 添加AI回答
        this.addAIMessage(result.answer, result.knowledge_items);
      } catch (error) {
        console.error('获取回答失败:', error);
        this.handleAPIError();
      } finally {
        this.isThinking = false;
      }
    },
    
    // 处理API错误
    handleAPIError() {
      // 如果发生错误，添加一个默认回答
      this.addAIMessage('抱歉，我遇到了一些问题，无法回答您的问题。');
    },
    
    // 格式化消息历史以发送给API
    formatMessages() {
      // 获取最近的消息（最多10条）
      const recentMessages = this.chatMessages.slice(-10);
      
      // 转换为API格式
      return recentMessages.map(msg => ({
        role: msg.isUser ? 'user' : 'assistant',
        content: msg.content
      }));
    }
  }
};
</script>

<style>
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.status-bar-placeholder {
  width: 100%;
}

.status-bar {
  display: flex;
  padding: 10px 15px;
  background-color: #ffffff;
  border-bottom: 1px solid #eaeaea;
  align-items: center;
}

.history-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: rgba(53, 112, 236, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.history-button:active {
  transform: scale(0.95);
  background-color: rgba(53, 112, 236, 0.2);
}

.history-button .iconfont {
  font-size: 22px;
  color: #3570EC;
}

.clear-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: rgba(244, 67, 54, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 15px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.clear-button:active {
  transform: scale(0.95);
  background-color: rgba(244, 67, 54, 0.2);
}

.clear-button .iconfont {
  font-size: 22px;
  color: #F44336;
}

.app-title {
  flex: 1;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.chat-container {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
}

.chat-list {
  padding-bottom: 10px;
}

.thinking-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  color: #666;
}

.thinking-dots {
  display: flex;
}

.dot {
  animation: thinking 1.4s infinite;
  font-size: 20px;
  line-height: 20px;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes thinking {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.6;
  }
  30% {
    transform: translateY(-5px);
    opacity: 1;
  }
}

.input-container {
  display: flex;
  align-items: center;
  padding: 10rpx 20rpx;
  background-color: #ffffff;
  border-top: 1px solid #eaeaea;
}

.voice-input-wrapper {
  margin-right: 10rpx;
}

.action-button {
  width: 80rpx;
  height: 80rpx;
  border-radius: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin: 0;
  background-color: #f0f0f0;
}

.voice-button {
  background: linear-gradient(135deg, #3570EC, #5A7CFF);
}

.voice-button .iconfont {
  color: #ffffff;
}

.recording {
  background: #ff4d4f !important;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.recording-tip {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.recording-tip-inner {
  background-color: rgba(0, 0, 0, 0.7);
  border-radius: 15px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 160px;
}

.recording-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #007aff;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
}

.recording-icon.cancel {
  background-color: #ff3b30;
}

.recording-icon .iconfont {
  color: #ffffff;
  font-size: 30px;
  animation: pulse 1.5s infinite;
}

.recording-text {
  color: #ffffff;
  font-size: 14px;
}

@keyframes pulse {
  0% {
    opacity: 0.5;
    transform: scale(0.9);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
  100% {
    opacity: 0.5;
    transform: scale(0.9);
  }
}
</style> 