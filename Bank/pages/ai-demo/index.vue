<template>
	<view class="container">
		<view class="header">
			<view class="title">百度千帆ModelBuilder演示</view>
			<view class="subtitle">ERNIE-4.5-turbo-vl-32k模型</view>
		</view>
		
		<view class="card">
			<view class="section-title">文本对话</view>
			<view class="input-area">
				<textarea class="textarea" v-model="textQuestion" placeholder="请输入您的问题..."></textarea>
				<button class="btn btn-primary" @click="sendTextQuestion" :disabled="loading">发送</button>
			</view>
		</view>
		
		<view class="card">
			<view class="section-title">图像识别</view>
			<view class="image-area">
				<image v-if="imageUrl" :src="imageUrl" mode="aspectFit" class="selected-image"></image>
				<view v-else class="image-placeholder">
					<text class="iconfont icon-add">+</text>
					<text>选择图片</text>
				</view>
				
				<view class="image-actions">
					<button class="btn btn-secondary" @click="selectImage">选择图片</button>
					<button class="btn btn-primary" @click="sendImageQuestion" :disabled="loading || !imageUrl">发送</button>
				</view>
				
				<input class="image-question" v-model="imageQuestion" placeholder="关于图片的问题(可选)..."/>
			</view>
		</view>
		
		<view class="card response-card" v-if="response">
			<view class="section-title">AI回复</view>
			<view class="response-content">
				{{ response }}
			</view>
		</view>
		
		<view class="loading-mask" v-if="loading">
			<view class="loading-spinner"></view>
			<text>正在处理...</text>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			textQuestion: '',
			imageQuestion: '请分析这张图片并告诉我你看到了什么?',
			imageUrl: '',
			imageBase64: '',
			response: '',
			loading: false,
			history: []
		}
	},
	onLoad() {
		// 页面加载时检查ModelBuilder是否可用
		if (!this.$modelBuilder) {
			uni.showToast({
				title: 'ModelBuilder未初始化',
				icon: 'none'
			});
		}
	},
	methods: {
		// 发送纯文本问题
		async sendTextQuestion() {
			if (!this.textQuestion.trim()) {
				uni.showToast({
					title: '请输入问题',
					icon: 'none'
				});
				return;
			}
			
			try {
				this.loading = true;
				
				// 构建消息
				const messages = [
					...this.history,
					{ role: 'user', content: this.textQuestion }
				];
				
				// 调用ModelBuilder
				const result = await this.$modelBuilder.chat(messages);
				
				if (result.success) {
					this.response = result.content;
					
					// 更新历史记录
					this.history.push(
						{ role: 'user', content: this.textQuestion },
						{ role: 'assistant', content: result.content }
					);
					
					// 如果历史太长，截取最近的
					if (this.history.length > 10) {
						this.history = this.history.slice(-10);
					}
					
					// 清空输入
					this.textQuestion = '';
				} else {
					this.response = `出错了: ${result.error}`;
					uni.showToast({
						title: '请求失败',
						icon: 'none'
					});
				}
			} catch (error) {
				console.error('发送文本问题失败:', error);
				this.response = `出错了: ${error.message}`;
				uni.showToast({
					title: '请求失败',
					icon: 'none'
				});
			} finally {
				this.loading = false;
			}
		},
		
		// 选择图片
		selectImage() {
			uni.chooseImage({
				count: 1,
				sourceType: ['album', 'camera'],
				success: (res) => {
					this.imageUrl = res.tempFilePaths[0];
					
					// 读取图片为base64
					uni.getFileSystemManager().readFile({
						filePath: this.imageUrl,
						encoding: 'base64',
						success: (res) => {
							this.imageBase64 = res.data;
						},
						fail: (err) => {
							console.error('读取图片失败:', err);
							uni.showToast({
								title: '读取图片失败',
								icon: 'none'
							});
						}
					});
				}
			});
		},
		
		// 发送图片问题
		async sendImageQuestion() {
			if (!this.imageUrl || !this.imageBase64) {
				uni.showToast({
					title: '请先选择图片',
					icon: 'none'
				});
				return;
			}
			
			try {
				this.loading = true;
				
				// 构建消息 - 多模态格式
				const content = [
					{
						type: 'text',
						text: this.imageQuestion || '请分析这张图片'
					},
					{
						type: 'image',
						data: `data:image/jpeg;base64,${this.imageBase64}`
					}
				];
				
				const messages = [
					{ 
						role: 'user', 
						content: content
					}
				];
				
				// 调用ModelBuilder的多模态对话
				const result = await this.$modelBuilder.chatWithImages(messages);
				
				if (result.success) {
					this.response = result.content;
					
					// 清空图片
					// this.imageUrl = '';
					// this.imageBase64 = '';
				} else {
					this.response = `出错了: ${result.error}`;
					uni.showToast({
						title: '请求失败',
						icon: 'none'
					});
				}
			} catch (error) {
				console.error('发送图片问题失败:', error);
				this.response = `出错了: ${error.message}`;
				uni.showToast({
					title: '请求失败',
					icon: 'none'
				});
			} finally {
				this.loading = false;
			}
		}
	}
}
</script>

<style>
.container {
	padding: 40rpx 30rpx;
}

.header {
	margin-bottom: 40rpx;
}

.title {
	font-size: 44rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 10rpx;
}

.subtitle {
	font-size: 28rpx;
	color: #666;
}

.card {
	background-color: #fff;
	border-radius: 20rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.section-title {
	font-size: 32rpx;
	font-weight: 500;
	color: #333;
	margin-bottom: 20rpx;
	border-left: 8rpx solid #3570EC;
	padding-left: 20rpx;
}

.input-area {
	display: flex;
	flex-direction: column;
}

.textarea {
	width: 100%;
	height: 200rpx;
	background-color: #f8f9fa;
	border-radius: 12rpx;
	padding: 20rpx;
	margin-bottom: 20rpx;
	font-size: 28rpx;
}

.image-area {
	display: flex;
	flex-direction: column;
	align-items: center;
}

.selected-image,
.image-placeholder {
	width: 400rpx;
	height: 400rpx;
	border-radius: 12rpx;
	margin-bottom: 20rpx;
	background-color: #f8f9fa;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	color: #999;
	font-size: 28rpx;
}

.image-placeholder .iconfont {
	font-size: 60rpx;
	margin-bottom: 10rpx;
}

.image-actions {
	display: flex;
	justify-content: space-between;
	width: 100%;
	margin-bottom: 20rpx;
}

.image-actions .btn {
	width: 48%;
}

.image-question {
	width: 100%;
	height: 80rpx;
	background-color: #f8f9fa;
	border-radius: 12rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
}

.response-card {
	background-color: #f0f7ff;
}

.response-content {
	padding: 20rpx;
	font-size: 28rpx;
	line-height: 1.6;
	white-space: pre-wrap;
}

.loading-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background-color: rgba(0, 0, 0, 0.5);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	color: #fff;
	z-index: 999;
}

.loading-spinner {
	width: 80rpx;
	height: 80rpx;
	border: 6rpx solid rgba(255, 255, 255, 0.3);
	border-radius: 50%;
	border-top-color: #fff;
	animation: spin 1s linear infinite;
	margin-bottom: 20rpx;
}

@keyframes spin {
	to {
		transform: rotate(360deg);
	}
}

.btn {
	height: 80rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 12rpx;
	font-size: 28rpx;
	margin-bottom: 0;
}

.btn-primary {
	background-color: #3570EC;
	color: #fff;
}

.btn-secondary {
	background-color: #f8f9fa;
	color: #333;
	border: 1px solid #ddd;
}

.btn[disabled] {
	opacity: 0.6;
}
</style> 