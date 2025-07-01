<template>
  <view class="container">
    <!-- 页面顶部导航栏 -->
    <view class="nav-bar">
      <view class="nav-back" @tap="goBack">
        <text class="iconfont icon-back"></text>
      </view>
      <view class="nav-title">历史记录</view>
      <view class="nav-action" @click="clearHistory">
        <text class="iconfont icon-clear"></text>
      </view>
    </view>
    
    <scroll-view class="history-list" scroll-y="true" @scrolltolower="loadMoreHistory">
      <view v-if="historyList.length === 0" class="empty-history">
        <view class="empty-icon">
          <text class="iconfont icon-history" style="font-size: 120rpx !important; color: #cccccc;"></text>
        </view>
        <text class="empty-text">暂无历史记录</text>
      </view>
      
      <view v-else class="history-items">
        <view 
          class="history-item card" 
          v-for="(item, index) in historyList" 
          :key="index"
          @click="viewDetail(item)"
        >
          <view class="item-header">
            <view class="item-time">{{ formatTime(item.time) }}</view>
            <view class="item-actions">
              <view class="action-icon" @click.stop="reAsk(item)">
                <text class="iconfont icon-ask"></text>
              </view>
              <view class="action-icon" @click.stop="deleteItem(index)">
                <text class="iconfont icon-delete"></text>
              </view>
            </view>
          </view>
          
          <view class="item-content">
            <view class="question-box">
              <text class="question-label">问：</text>
              <text class="question-text multi-ellipsis-2">{{ item.question }}</text>
            </view>
            <view class="answer-box">
              <text class="answer-label">答：</text>
              <text class="answer-text multi-ellipsis-2">{{ formatAnswer(item.answer) }}</text>
            </view>
          </view>
        </view>
        
        <view class="loading-more" v-if="isLoading">
          <text>加载中...</text>
        </view>
        
        <view class="no-more" v-if="noMore && historyList.length > 0">
          <text>已加载全部历史记录</text>
        </view>
      </view>
    </scroll-view>
    
    <!-- 详情弹窗 -->
    <view class="detail-popup" v-if="showDetail">
      <view class="popup-mask" @click="closeDetail"></view>
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">对话详情</text>
          <view class="popup-close" @click="closeDetail">
            <text class="iconfont icon-back"></text>
          </view>
        </view>
        
        <scroll-view class="popup-body" scroll-y="true">
          <view class="detail-time">{{ formatTime(currentDetail.time) }}</view>
          
          <view class="detail-question">
            <text class="detail-label">问题：</text>
            <text class="detail-text">{{ currentDetail.question }}</text>
          </view>
          
          <view class="detail-answer">
            <text class="detail-label">回答：</text>
            <text class="detail-text">{{ currentDetail.answer }}</text>
          </view>
          
          <view class="detail-keywords" v-if="currentDetail.keywords && currentDetail.keywords.length > 0">
            <text class="detail-label">关键词：</text>
            <view class="keyword-list">
              <text class="keyword-item" v-for="(keyword, kIndex) in currentDetail.keywords" :key="kIndex">
                {{ keyword }}
              </text>
            </view>
          </view>
        </scroll-view>
        
        <view class="popup-footer">
          <view class="btn btn-primary" @click="reAsk(currentDetail)">
            <text class="btn-text">再次提问</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import * as Storage from '@/utils/storage.js';
import * as Nlp from '@/utils/nlp.js';

export default {
  data() {
    return {
      historyList: [],
      pageSize: 10,
      currentPage: 1,
      isLoading: false,
      noMore: false,
      showDetail: false,
      currentDetail: {},
      loadMoreTimer: null
    }
  },
  onLoad() {
    this.loadHistory();
  },
  onUnload() {
    if (this.loadMoreTimer) {
      clearTimeout(this.loadMoreTimer);
      this.loadMoreTimer = null;
    }
    this.historyList = [];
    this.showDetail = false;
    this.currentDetail = {};
  },
  methods: {
    // 返回上一页
    goBack() {
      uni.navigateBack();
    },
    
    // 加载历史记录
    loadHistory() {
      const history = Storage.getChatHistory();
      
      // 按时间倒序排序
      if (Array.isArray(history)) {
        history.sort((a, b) => b.time - a.time);
        
        // 分页加载
        this.historyList = history.slice(0, this.pageSize);
        this.noMore = history.length <= this.pageSize;
      } else {
        console.error('历史记录不是数组');
        this.historyList = [];
        this.noMore = true;
      }
    },
    
    // 加载更多历史记录
    loadMoreHistory() {
      if (this.isLoading || this.noMore) return;
      
      this.isLoading = true;
      
      // 清除之前的计时器（如果有）
      if (this.loadMoreTimer) {
        clearTimeout(this.loadMoreTimer);
      }
      
      // 使用类实例中的计时器引用
      this.loadMoreTimer = setTimeout(() => {
        try {
          const history = Storage.getChatHistory();
          
          // 确保history是一个数组
          if (!Array.isArray(history)) {
            console.error('历史记录不是数组');
            this.isLoading = false;
            this.noMore = true;
            return;
          }
          
          // 按时间倒序排序
          history.sort((a, b) => b.time - a.time);
          
          const nextPage = this.currentPage + 1;
          const start = this.currentPage * this.pageSize;
          const end = nextPage * this.pageSize;
          const moreItems = history.slice(start, end);
          
          if (moreItems.length > 0) {
            this.historyList = [...this.historyList, ...moreItems];
            this.currentPage = nextPage;
            this.noMore = end >= history.length;
          } else {
            this.noMore = true;
          }
        } catch (error) {
          console.error('加载更多历史记录失败:', error);
        } finally {
          this.isLoading = false;
          this.loadMoreTimer = null;
        }
      }, 500);
    },
    
    // 格式化时间
    formatTime(timestamp) {
      // 处理无效时间戳
      if (!timestamp) {
        return '未知时间';
      }
      
      try {
        const date = new Date(timestamp);
        
        // 检查日期是否有效
        if (isNaN(date.getTime())) {
          return '未知时间';
        }
        
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const hour = date.getHours().toString().padStart(2, '0');
        const minute = date.getMinutes().toString().padStart(2, '0');
        
        return `${year}-${month}-${day} ${hour}:${minute}`;
      } catch (error) {
        console.error('格式化时间失败:', error);
        return '未知时间';
      }
    },
    
    // 格式化回答（截取前50个字符）
    formatAnswer(answer) {
      // 处理空值
      if (!answer) {
        return '无回答内容';
      }
      
      // 确保answer是字符串
      answer = String(answer);
      
      if (answer.length > 50) {
        return answer.substring(0, 50) + '...';
      }
      return answer;
    },
    
    // 查看详情
    viewDetail(item) {
      // 确保item包含必要的属性
      if (!item) {
        console.error('查看详情失败: item为空');
        return;
      }
      
      // 确保问题和回答字段存在
      if (!item.question) {
        item.question = '未知问题';
      }
      
      if (!item.answer) {
        item.answer = '未知回答';
      }
      
      // 如果没有关键词，尝试提取
      if (!item.keywords || item.keywords.length === 0) {
        item.keywords = Nlp.extractKeywords(item.question);
      }
      
      this.currentDetail = item;
      this.showDetail = true;
    },
    
    // 关闭详情
    closeDetail() {
      this.showDetail = false;
    },
    
    // 再次提问
    reAsk(item) {
      // 确保item包含问题
      if (!item || !item.question) {
        console.error('再次提问失败: 问题为空');
        uni.showToast({
          title: '无法提问，问题为空',
          icon: 'none'
        });
        return;
      }
      
      // 跳转到首页并传递问题
      uni.navigateBack({
        success: () => {
          // 使用全局事件总线传递数据
          uni.$emit('reask', {
            question: item.question
          });
        }
      });
    },
    
    // 删除单条记录
    deleteItem(index) {
      // 检查索引是否有效
      if (index < 0 || index >= this.historyList.length) {
        console.error('删除失败: 索引无效', index);
        return;
      }
      
      uni.showModal({
        title: '提示',
        content: '确定要删除这条记录吗？',
        success: (res) => {
          if (res.confirm) {
            try {
              // 从当前列表中删除
              const item = this.historyList[index];
              if (!item) {
                console.error('删除失败: 项目不存在');
                return;
              }
              
              this.historyList.splice(index, 1);
              
              // 从存储中删除
              const history = Storage.getChatHistory();
              
              // 确保history是一个数组
              if (!Array.isArray(history)) {
                console.error('删除失败: 历史记录不是数组');
                Storage.setStorage('chat_history', this.historyList);
              } else {
                // 安全地过滤历史记录
                const newHistory = history.filter(h => {
                  // 确保h和item都有必要的属性
                  if (!h || !item) return true;
                  
                  const questionMatch = h.question === item.question;
                  const timeMatch = h.time === item.time;
                  
                  return !(questionMatch && timeMatch);
                });
                
                // 确保newHistory是一个数组
                if (!Array.isArray(newHistory)) {
                  console.error('过滤后的历史记录不是数组，使用当前列表');
                  Storage.setStorage('chat_history', this.historyList);
                } else {
                  Storage.setStorage('chat_history', newHistory);
                }
              }
              
              uni.showToast({
                title: '删除成功',
                icon: 'success'
              });
            } catch (error) {
              console.error('删除过程中发生错误:', error);
              uni.showToast({
                title: '删除失败',
                icon: 'none'
              });
            }
          }
        }
      });
    },
    
    // 清空历史记录
    clearHistory() {
      uni.showModal({
        title: '提示',
        content: '确定要清空所有历史记录吗？',
        success: (res) => {
          if (res.confirm) {
            Storage.clearChatHistory();
            this.historyList = [];
            
            uni.showToast({
              title: '已清空历史记录',
              icon: 'success'
            });
          }
        }
      });
    }
  }
}
</script>

<style>
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f8faff;
}

/* 顶部导航栏 */
.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 90rpx;
  background: linear-gradient(135deg, #3570EC, #5A7CFF);
  color: #FFFFFF;
  padding: 0 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(53, 112, 236, 0.15);
  z-index: 100;
}

.nav-back {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-title {
  font-size: 36rpx;
  font-weight: 500;
  flex: 1;
  text-align: center;
}

.nav-action {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-list {
  flex: 1;
  padding: 20rpx;
}

.empty-history {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 500rpx;
}

.empty-icon {
  width: 200rpx;
  height: 200rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999999;
}

.history-items {
  padding-bottom: 20rpx;
}

.history-item {
  margin-bottom: 20rpx;
  transition: all 0.3s;
}

.history-item:active {
  transform: scale(0.98);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15rpx;
}

.item-time {
  font-size: 24rpx;
  color: #999999;
}

.item-actions {
  display: flex;
}

.action-icon {
  padding: 10rpx;
  color: #3570EC;
}

.item-content {
  display: flex;
  flex-direction: column;
}

.question-box, .answer-box {
  display: flex;
  margin-bottom: 10rpx;
}

.question-label, .answer-label {
  font-size: 28rpx;
  font-weight: 500;
  margin-right: 10rpx;
  flex-shrink: 0;
}

.question-label {
  color: #3570EC;
}

.answer-label {
  color: #52c41a;
}

.question-text, .answer-text {
  font-size: 28rpx;
  color: #333333;
  flex: 1;
}

.loading-more, .no-more {
  text-align: center;
  padding: 20rpx 0;
  color: #999999;
  font-size: 24rpx;
}

/* 详情弹窗 */
.detail-popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
}

.popup-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
}

.popup-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #ffffff;
  border-top-left-radius: 20rpx;
  border-top-right-radius: 20rpx;
  display: flex;
  flex-direction: column;
  max-height: 80vh;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #eeeeee;
}

.popup-title {
  font-size: 32rpx;
  font-weight: 500;
  color: #333333;
}

.popup-close {
  padding: 10rpx;
  transform: rotate(90deg);
}

.popup-body {
  flex: 1;
  padding: 30rpx;
  max-height: 60vh;
}

.detail-time {
  font-size: 24rpx;
  color: #999999;
  margin-bottom: 20rpx;
}

.detail-question, .detail-answer, .detail-keywords {
  margin-bottom: 30rpx;
}

.detail-label {
  font-size: 28rpx;
  font-weight: 500;
  color: #333333;
  margin-bottom: 10rpx;
  display: block;
}

.detail-text {
  font-size: 28rpx;
  color: #666666;
  line-height: 1.6;
}

.keyword-list {
  display: flex;
  flex-wrap: wrap;
}

.keyword-item {
  font-size: 24rpx;
  color: #3570EC;
  background-color: rgba(64, 128, 255, 0.1);
  padding: 6rpx 16rpx;
  border-radius: 30rpx;
  margin-right: 16rpx;
  margin-bottom: 16rpx;
}

.popup-footer {
  padding: 20rpx 30rpx;
  border-top: 1rpx solid #eeeeee;
  display: flex;
  justify-content: flex-end;
}

.btn-text {
  color: #ffffff;
  font-size: 28rpx;
}

/* 图标字体 */
.iconfont {
  font-family: "iconfont" !important;
  font-size: 40rpx;
  font-style: normal;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.icon-back:before {
  content: "\e666";
}

.icon-clear:before {
  content: "\e900";
}

.icon-ask:before {
  content: "\e7ca";
}

.icon-delete:before {
  content: "\e681";
}
</style> 