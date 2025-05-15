<template>
	<view class="container">
		<!-- 页面顶部导航栏 -->
		<view class="nav-bar">
			<view class="nav-title">智能银行助手</view>
		</view>
		
		<!-- 问答内容展示区域 -->
		<scroll-view scroll-y class="chat-container" :scroll-top="scrollTop">
			<!-- 欢迎信息 -->
			<view class="welcome-card" v-if="chatList.length === 0">
				<span class="iconfont icon-ai"></span>
				<view class="welcome-title">您好，我是您的智能银行助手</view>
				<view class="welcome-desc">我可以回答您关于银行业务的各类问题，请告诉我您需要了解什么？</view>
				<view class="quick-questions">
					<view class="quick-tag" v-for="(item, index) in quickQuestions" :key="index" @click="quickAsk(item)">
						{{item}}
					</view>
				</view>
			</view>
			
			<block v-for="(item, index) in chatList" :key="index">
				<!-- 用户提问 -->
				<view class="question-box">
					<view class="question-content">
						<text>{{item.question}}</text>
					</view>
				</view>
				
				<!-- AI回答 -->
				<view class="answer-box" v-if="item.answer">
					<view class="ai-avatar">
						<span class="iconfont icon-ai"></span>
					</view>
					<view class="answer-content">
						<text>{{item.answer}}</text>
						<view class="answer-tools">
							<view class="tool-btn voice-btn" @click="playVoice(item.answer)">
								<span class="iconfont icon-voice"></span>
							</view>
							<view class="tool-btn copy-btn" @click="copyAnswer(item)">
								<span class="iconfont icon-copy"></span>
							</view>
						</view>
					</view>
				</view>
			</block>
			
			<!-- 加载提示 -->
			<view class="loading-box" v-if="isLoading">
				<view class="ai-avatar">
					<span class="iconfont icon-ai"></span>
				</view>
				<view class="loading-dots">
					<view class="dot"></view>
					<view class="dot"></view>
					<view class="dot"></view>
				</view>
			</view>
		</scroll-view>
		
		<!-- 输入区域 -->
		<view class="input-container">
			<view class="input-box">
				<view class="voice-btn icon-wrapper" @click="toggleVoiceInput">
					<span class="iconfont" :class="isVoiceMode ? 'icon-keyboard' : 'icon-mic'"></span>
				</view>
				
				<input 
					v-if="!isVoiceMode" 
					type="text" 
					class="input-field" 
					v-model="inputContent" 
					placeholder="请输入您的问题..."
					confirm-type="send"
					@confirm="sendQuestion"
				/>
				
				<view v-else class="voice-input-area" @touchstart="startRecording" @touchend="stopRecording">
					<text>{{recordingTip}}</text>
				</view>
				
				<view class="send-btn" @click="sendQuestion" v-if="inputContent.trim().length > 0">
					<span class="iconfont icon-send"></span>
				</view>
				
				<view class="history-btn icon-wrapper" @click="goToHistory" v-else>
					<span class="iconfont icon-history"></span>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import KnowledgeService from '../../utils/knowledge-service.js';
	
	export default {
		data() {
			return {
				inputContent: "",
				isVoiceMode: false,
				isRecording: false,
				recordingTip: "按住说话",
				isLoading: false,
				scrollTop: 0,
				oldScrollTop: 0,
				chatList: [],
				knowledgeService: null,
				quickQuestions: [
					"如何办理信用卡？",
					"车险理赔流程是怎样的？",
					"理财产品有哪些风险？",
					"如何查询贷款利率？"
				]
			}
		},
		onLoad(options) {
			// 初始化数据
			this.chatList = []; // 先清空示例数据，让用户看到欢迎信息
			
			// 初始化知识库服务
			try {
				this.knowledgeService = new KnowledgeService();
				
				// 检查初始化状态
				if (this.knowledgeService.modelBuilder) {
					console.log('KnowledgeService已成功初始化，使用模型：' + 
						this.knowledgeService.aiServiceConfig.models.baidu);
				} else {
					console.error('KnowledgeService初始化成功，但ModelBuilder实例未正确创建');
					// 尝试重新初始化ModelBuilder
					const [apiKey, secretKey] = this.knowledgeService.aiServiceConfig.apiKey.split('|');
					this.knowledgeService.modelBuilder = new this.$modelBuilder.constructor({
						apiKey: apiKey, 
						secretKey: secretKey,
						model: this.knowledgeService.aiServiceConfig.models.baidu,
						endpoint: this.knowledgeService.aiServiceConfig.endpoints.baidu
					});
				}
			} catch (e) {
				console.error('初始化KnowledgeService失败:', e);
				uni.showToast({
					title: '系统初始化失败，部分功能可能无法使用',
					icon: 'none',
					duration: 3000
				});
			}
			
			// 确保conversationContext.history存在
			if (this.knowledgeService && 
				this.knowledgeService.conversationContext && 
				!this.knowledgeService.conversationContext.history) {
				this.knowledgeService.conversationContext.history = [];
			}
			
			// 检查是否有预填充的问题（从历史记录页返回）
			if (options && options.question) {
				this.inputContent = decodeURIComponent(options.question);
			}
			
			// 监听事件（从详情页返回并预填问题）
			uni.$on('fillQuestion', this.handleFillQuestion);
		},
		onUnload() {
			// 移除事件监听
			uni.$off('fillQuestion', this.handleFillQuestion);
		},
		methods: {
			// 快速提问
			quickAsk(question) {
				this.inputContent = question;
				this.sendQuestion();
			},
			
			// 处理从详情页返回并预填问题
			handleFillQuestion(data) {
				if (data && data.question) {
					this.inputContent = data.question;
				}
			},
			
			// 切换语音/文字输入模式
			toggleVoiceInput() {
				this.isVoiceMode = !this.isVoiceMode;
				this.inputContent = "";
			},
			
			// 开始录音
			startRecording() {
				this.isRecording = true;
				this.recordingTip = "松开结束";
				
				// 调用录音API
				try {
					// 优先使用全局的语音识别服务
					if (getApp().globalData.speechRecognition) {
						getApp().globalData.speechRecognition.startRecognize();
						console.log("使用原生语音识别服务开始录音...");
					} else {
						// 回退到Vue原型上定义的服务
						if (this.$speechRecognition && this.$speechRecognition.startRecording) {
							this.$speechRecognition.startRecording();
							console.log("使用JS语音识别服务开始录音...");
						} else {
							console.log("语音识别服务未初始化");
							uni.showToast({
								title: '语音识别服务未启用',
								icon: 'none'
							});
						}
					}
				} catch (e) {
					console.error("启动录音失败:", e);
					uni.showToast({
						title: '启动录音失败，请检查麦克风权限',
						icon: 'none'
					});
				}
			},
			
			// 结束录音
			stopRecording() {
				this.isRecording = false;
				this.recordingTip = "按住说话";
				
				console.log("录音结束");
				
				// 显示加载中状态
				uni.showLoading({
					title: '正在识别...'
				});
				
				try {
					// 优先使用全局的语音识别服务
					if (getApp().globalData.speechRecognition) {
						getApp().globalData.speechRecognition.stopRecognize();
						
						// 监听语音识别结果 - 这里是模拟结果，实际应该对接科大讯飞等语音识别服务
						setTimeout(() => {
							uni.hideLoading();
							this.inputContent = "如何办理银行卡挂失？";
							this.sendQuestion();
						}, 1000);
					} else {
						// 回退到Vue原型上定义的服务
						if (this.$speechRecognition && this.$speechRecognition.stopRecording) {
							this.$speechRecognition.stopRecording();
							
							// 使用语音识别服务识别结果
							this.$speechRecognition.recognizeSpeech('temp')
								.then(result => {
									uni.hideLoading();
									this.inputContent = result;
									this.sendQuestion();
								})
								.catch(error => {
									uni.hideLoading();
									console.error("语音识别失败:", error);
									uni.showToast({
										title: '识别失败，请重试',
										icon: 'none'
									});
								});
						} else {
							uni.hideLoading();
							uni.showToast({
								title: '语音识别服务未初始化',
								icon: 'none'
							});
						}
					}
				} catch (e) {
					uni.hideLoading();
					console.error("停止录音失败:", e);
					uni.showToast({
						title: '语音识别失败，请重试',
						icon: 'none'
					});
				}
			},
			
			// 发送问题
			sendQuestion() {
				if (this.inputContent.trim().length === 0) return;
				
				// 添加问题到列表
				this.chatList.push({
					question: this.inputContent,
					answer: "",
					time: this.getCurrentTime()
				});
				
				// 清空输入
				const question = this.inputContent;
				this.inputContent = "";
				
				// 滚动到底部
				this.$nextTick(() => {
					this.scrollToBottom();
				});
				
				// 显示加载状态
				this.isLoading = true;
				
				// 调用知识库服务获取答案
				this.knowledgeService.generateAnswer(question).then(answer => {
					// 更新回答
					const lastIndex = this.chatList.length - 1;
					this.chatList[lastIndex].answer = answer;
					
					// 保存到历史记录
					this.saveToHistory();
					
					// 隐藏加载状态
					this.isLoading = false;
					
					// 滚动到底部
					this.$nextTick(() => {
						this.scrollToBottom();
					});
				}).catch(err => {
					console.error('获取回答失败:', err);
					
					// 显示错误信息
					const lastIndex = this.chatList.length - 1;
					let errorMessage = "很抱歉，系统暂时无法回答您的问题，请稍后再试。";
					
					// 根据错误类型提供更具体的错误信息
					if (err.message && err.message.includes('Failed to fetch')) {
						errorMessage = "网络连接失败，请检查您的网络连接后重试。";
					} else if (err.message && err.message.includes('Cannot read properties')) {
						errorMessage = "系统处理异常，正在尝试修复，请稍后再试。";
					}
					
					this.chatList[lastIndex].answer = errorMessage;
					
					// 隐藏加载状态
					this.isLoading = false;
					
					// 仍然保存到历史记录
					this.saveToHistory();
					
					// 显示提示
					uni.showToast({
						title: '回答生成失败',
						icon: 'none',
						duration: 2000
					});
				});
			},
			
			// 获取当前时间
			getCurrentTime() {
				const now = new Date();
				const year = now.getFullYear();
				const month = String(now.getMonth() + 1).padStart(2, '0');
				const day = String(now.getDate()).padStart(2, '0');
				const hour = String(now.getHours()).padStart(2, '0');
				const minute = String(now.getMinutes()).padStart(2, '0');
				
				return `${year}-${month}-${day} ${hour}:${minute}`;
			},
			
			// 保存到历史记录
			saveToHistory() {
				try {
					// 只保存最近的20条记录
					const recentChats = this.chatList.slice(-20);
					uni.setStorageSync('chat_history', JSON.stringify(recentChats));
				} catch (e) {
					console.error('保存历史记录失败:', e);
				}
			},
			
			// 复制回答内容
			copyAnswer(item) {
				uni.setClipboardData({
					data: item.answer,
					success: () => {
						uni.showToast({
							title: '已复制到剪贴板',
							icon: 'none'
						});
					}
				});
			},
			
			// 播放语音
			playVoice(text) {
				if (!text) return;
				
				uni.showToast({
					title: '语音播放中...',
					icon: 'none',
					duration: 2000
				});
				
				try {
					// 优先使用App全局语音服务
					if (getApp().globalData.textToSpeech) {
						getApp().globalData.textToSpeech.speak({
							text: text,
							volume: 1.0,
							rate: 1.0,
							pitch: 1.0
						});
						console.log("使用原生语音合成服务");
					} else {
						// 回退到Vue原型上定义的服务
						if (this.$textToSpeech && this.$textToSpeech.speak) {
							this.$textToSpeech.speak(text)
								.then(() => {
									console.log("语音播放完成");
								})
								.catch(error => {
									console.error("语音播放失败:", error);
									uni.showToast({
										title: '语音播放失败',
										icon: 'none'
									});
								});
							console.log("使用JS语音合成服务");
						} else {
							console.log("语音合成服务未初始化");
							uni.showToast({
								title: '语音合成服务未启用',
								icon: 'none'
							});
						}
					}
				} catch (e) {
					console.error("语音播放错误:", e);
					uni.showToast({
						title: '语音播放失败',
						icon: 'none'
					});
				}
			},
			
			// 滚动到底部
			scrollToBottom() {
				// 设置一个较大的值确保滚动到底部
				this.scrollTop = 9999;
			},
			
			// 跳转到历史记录
			goToHistory() {
				uni.navigateTo({
					url: '/pages/history/history'
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
	
	/* 波浪背景 */
	.wave-bg {
		position: relative;
		overflow: hidden;
		z-index: 1;
	}
	
	.wave-bg:after {
		content: '';
		position: absolute;
		bottom: -20rpx;
		left: 0;
		right: 0;
		height: 40rpx;
		background: url('../../static/images/wave.png') repeat-x;
		background-size: 100rpx 40rpx;
		animation: wave 8s linear infinite;
		z-index: 0;
	}
	
	@keyframes wave {
		0% {
			background-position: 0 0;
		}
		100% {
			background-position: 1000rpx 0;
		}
	}
	
	/* 导航栏 */
	.nav-bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 24rpx 30rpx;
		background: linear-gradient(135deg, #3570EC, #5A7CFF);
		color: #FFFFFF;
		box-shadow: 0 4rpx 20rpx rgba(53, 112, 236, 0.2);
	}
	
	.nav-title {
		font-size: 36rpx;
		font-weight: 600;
	}
	
	.nav-right {
		display: flex;
		align-items: center;
	}
	
	.nav-btn {
		width: 80rpx;
		height: 80rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
	}
	
	/* 聊天容器 */
	.chat-container {
		flex: 1;
		overflow: hidden;
		padding: 30rpx 30rpx 0;
	}
	
	/* 欢迎卡片 */
	.welcome-card {
		background: linear-gradient(135deg, #FFFFFF, #f0f5ff);
		border-radius: 24rpx;
		padding: 36rpx;
		margin-bottom: 40rpx;
		box-shadow: 0 8rpx 30rpx rgba(53, 112, 236, 0.08);
		display: flex;
		flex-direction: column;
		align-items: center;
		border: 1rpx solid rgba(228, 237, 255, 0.8);
	}
	
	.welcome-icon {
		width: 120rpx;
		height: 120rpx;
		margin-bottom: 24rpx;
	}
	
	.welcome-title {
		font-size: 34rpx;
		font-weight: 600;
		color: #3570EC;
		margin-bottom: 16rpx;
	}
	
	.welcome-desc {
		font-size: 28rpx;
		color: #666666;
		text-align: center;
		line-height: 1.6;
	}
	
	/* 快速提问 */
	.quick-questions {
		margin-bottom: 40rpx;
	}
	
	.quick-title {
		font-size: 30rpx;
		color: #3570EC;
		margin-bottom: 24rpx;
		font-weight: 500;
		display: flex;
		align-items: center;
	}
	
	.quick-title:before {
		content: '';
		display: inline-block;
		width: 8rpx;
		height: 30rpx;
		background: linear-gradient(to bottom, #3570EC, #5A7CFF);
		border-radius: 4rpx;
		margin-right: 16rpx;
	}
	
	.question-list {
		display: flex;
		flex-wrap: wrap;
		margin: 0 -12rpx;
	}
	
	.question-item {
		background-color: #FFFFFF;
		border-radius: 20rpx;
		padding: 24rpx 30rpx;
		margin: 12rpx;
		flex-basis: calc(50% - 24rpx);
		box-sizing: border-box;
		box-shadow: 0 4rpx 20rpx rgba(53, 112, 236, 0.05);
		transition: all 0.3s;
		border: 1rpx solid rgba(228, 237, 255, 0.8);
	}
	
	.question-item:active {
		transform: scale(0.98);
		background-color: #f0f5ff;
	}
	
	.question-text {
		font-size: 28rpx;
		color: #333333;
		line-height: 1.5;
	}
	
	/* 聊天列表 */
	.chat-list {
		padding-bottom: 40rpx;
	}
	
	/* 问题框 */
	.question-box {
		display: flex;
		justify-content: flex-end;
		margin-bottom: 40rpx;
	}
	
	.question-content {
		background-color: #e1edff;
		border-radius: 20rpx 4rpx 20rpx 20rpx;
		padding: 24rpx 30rpx;
		max-width: 75%;
		font-size: 30rpx;
		color: #333333;
		line-height: 1.6;
		position: relative;
		margin-right: 20rpx;
		box-shadow: 0 4rpx 16rpx rgba(53, 112, 236, 0.1);
	}
	
	.user-avatar {
		width: 80rpx;
		height: 80rpx;
		border-radius: 40rpx;
		background: linear-gradient(135deg, #5E7CFF, #3570EC);
		display: flex;
		align-items: center;
		justify-content: center;
		color: #FFFFFF;
		flex-shrink: 0;
	}
	
	/* 回答框 */
	.answer-box {
		display: flex;
		margin-bottom: 40rpx;
	}
	
	.ai-avatar {
		width: 80rpx;
		height: 80rpx;
		border-radius: 40rpx;
		background: linear-gradient(135deg, #3570EC, #5A7CFF);
		display: flex;
		align-items: center;
		justify-content: center;
		color: #FFFFFF;
		margin-right: 20rpx;
		flex-shrink: 0;
	}
	
	.answer-content {
		background-color: #FFFFFF;
		border-radius: 4rpx 20rpx 20rpx 20rpx;
		padding: 24rpx 30rpx;
		max-width: 75%;
		font-size: 30rpx;
		color: #333333;
		line-height: 1.8;
		position: relative;
		box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
	}
	
	.answer-time {
		font-size: 24rpx;
		color: #999999;
		margin-top: 16rpx;
		text-align: right;
	}
	
	.answer-tools {
		display: flex;
		justify-content: flex-end;
		margin-top: 16rpx;
	}
	
	.tool-item {
		width: 60rpx;
		height: 60rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #3570EC;
		margin-left: 16rpx;
	}
	
	/* 加载框 */
	.loading-box {
		display: flex;
		margin-bottom: 40rpx;
	}
	
	.loading-content {
		background-color: #FFFFFF;
		border-radius: 4rpx 20rpx 20rpx 20rpx;
		padding: 24rpx 30rpx;
		font-size: 28rpx;
		color: #666666;
		min-width: 200rpx;
		box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
	}
	
	.loading-dots {
		display: flex;
		align-items: center;
		margin-bottom: 16rpx;
	}
	
	.loading-dot {
		width: 16rpx;
		height: 16rpx;
		border-radius: 8rpx;
		background-color: #3570EC;
		margin-right: 12rpx;
		opacity: 0.6;
		animation: loading 1.4s infinite ease-in-out;
	}
	
	.loading-dot:nth-child(1) {
		animation-delay: 0s;
	}
	
	.loading-dot:nth-child(2) {
		animation-delay: 0.2s;
	}
	
	.loading-dot:nth-child(3) {
		animation-delay: 0.4s;
	}
	
	@keyframes loading {
		0%, 100% {
			transform: scale(0.6);
			opacity: 0.4;
		}
		50% {
			transform: scale(1);
			opacity: 1;
		}
	}
	
	.loading-text {
		font-size: 26rpx;
		color: #999999;
	}
	
	/* 底部留白 */
	.bottom-space {
		height: 60rpx;
	}
	
	/* 输入区域 */
	.input-container {
		padding: 24rpx;
		background-color: #FFFFFF;
		border-top: 1rpx solid rgba(228, 237, 255, 0.8);
		box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.03);
	}
	
	.input-box {
		display: flex;
		align-items: center;
		background-color: #f8f9fa;
		border-radius: 44rpx;
		padding: 12rpx 20rpx;
		border: 1rpx solid rgba(228, 237, 255, 0.8);
		box-shadow: inset 0 2rpx 6rpx rgba(0, 0, 0, 0.03);
	}
	
	.voice-btn, .history-btn {
		margin: 0 8rpx;
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
		margin: 0 8rpx;
		box-shadow: 0 6rpx 16rpx rgba(53, 112, 236, 0.2);
		transition: all 0.3s;
	}
	
	.send-btn:active {
		transform: scale(0.95);
	}
	
	.input-field {
		flex: 1;
		height: 80rpx;
		font-size: 30rpx;
		padding: 0 24rpx;
		background-color: transparent;
	}
	
	.voice-input-area {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		height: 80rpx;
		font-size: 30rpx;
		color: #999999;
	}
	
	/* 覆盖字体大小 */
	.iconfont {
		font-size: 42rpx;
	}
	#1
	.icon-history:before {
		content: "\e69f";
	}
	#1
	.icon-user:before {
		content: "\e681";
	}
	#1
	.icon-ai:before {
		content: "\e682";
	}
	#1
	.icon-mic:before {
		content: "\e6b1";
	}
	#1
	.icon-keyboard:before {
		content: "\e67c";
	}
	#1
	.icon-send:before {
		content: "\e691";
	}
	#1
	.icon-copy:before {
		content: "\e6a5";
	}
	#1
	.icon-voice:before {
		content: "\e67e";
	}
	#1
	.icon-star:before {
		content: "\e683";
	}
</style> 