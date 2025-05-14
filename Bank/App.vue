<script>
	export default {
		onLaunch: function() {
			console.log('App Launch');
			// 初始化语音合成服务
			this.initTextToSpeech();
		},
		onShow: function() {
			console.log('App Show');
		},
		onHide: function() {
			console.log('App Hide');
		},
		globalData: {
			textToSpeech: null,
			speechRecognition: null
		},
		methods: {
			// 初始化语音合成服务
			initTextToSpeech() {
				// 判断是否在真机环境
				uni.getSystemInfo({
					success: (sysInfo) => {
						if (sysInfo.platform !== 'devtools') {
							// 真机环境下，初始化TTS服务
							try {
								this.globalData.textToSpeech = uni.requireNativePlugin('TextToSpeech');
								this.globalData.speechRecognition = uni.requireNativePlugin('SpeechRecognition');
								console.log('语音服务初始化成功');
							} catch (e) {
								console.error('语音服务初始化失败:', e);
							}
						}
					}
				});
			}
		}
	}
</script>

<style>
	/* 直接定义字体图标，不通过CSS文件导入 */
	@font-face {
		font-family: "iconfont";
		src: url('static/icon/iconfont.ttf') format('truetype');
		font-weight: normal;
		font-style: normal;
		font-display: swap;
	}
	
	/* 覆盖iconfont默认大小 */
	.iconfont {
		font-family: "iconfont" !important;
		font-size: 42rpx !important;
		font-style: normal;
		-webkit-font-smoothing: antialiased;
		-moz-osx-font-smoothing: grayscale;
	}
	
	/* 定义所有图标代码 - 使用icon目录下的图标代码 */
	.icon-right:before {
		content: "\e642";
	}
	
	.icon-copy:before {
		content: "\e744";
	}
	
	.icon-ask:before {
		content: "\e7ca";
	}
	
	.icon-star:before {
		content: "\e7df";
	}
	
	.icon-share:before {
		content: "\e729";
	}
	
	.icon-clear:before {
		content: "\e900";
	}
	
	.icon-voice:before {
		content: "\e6a5";
	}
	
	.icon-send:before {
		content: "\e916";
	}
	
	.icon-user:before {
		content: "\e682";
	}
	
	.icon-delete:before {
		content: "\e681";
	}
	
	.icon-history:before {
		content: "\e69f";
	}
	
	.icon-keyboard:before {
		content: "\e6a4";
	}
	
	.icon-mic:before {
		content: "\e6b1";
	}
	
	.icon-back:before {
		content: "\e666";
	}
	
	/* 特别保留ai图标，确保其兼容性 */
	.icon-ai:before {
		content: "\e682";
	}
	
	/* 全局样式 */
	* {
		box-sizing: border-box;
	}
	
	page {
		background-color: #f8faff;
		font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei', sans-serif;
		color: #333;
		font-size: 28rpx;
		line-height: 1.6;
	}
	
	/* 全局卡片样式 */
	.card {
		background-color: #ffffff;
		border-radius: 20rpx;
		box-shadow: 0 8rpx 30rpx rgba(0, 0, 0, 0.05);
		padding: 30rpx;
		margin-bottom: 24rpx;
		transition: all 0.3s;
		border: 1rpx solid rgba(228, 237, 255, 0.8);
	}
	
	/* 全局按钮样式 */
	.btn {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 88rpx;
		border-radius: 44rpx;
		font-size: 30rpx;
		font-weight: 500;
		transition: all 0.3s;
	}
	
	.btn-primary {
		background: linear-gradient(135deg, #3570EC, #5A7CFF);
		color: #ffffff;
		box-shadow: 0 10rpx 20rpx rgba(90, 124, 255, 0.3);
	}
	
	.btn-secondary {
		background-color: rgba(228, 237, 255, 0.6);
		color: #3570EC;
		border: 1rpx solid rgba(90, 124, 255, 0.2);
	}
	
	/* 输入框全局样式 */
	.input-common {
		background-color: #f8f9fa;
		border-radius: 44rpx;
		padding: 16rpx 30rpx;
		font-size: 28rpx;
		border: 1rpx solid #e2e8f0;
		box-shadow: inset 0 2rpx 6rpx rgba(0, 0, 0, 0.03);
	}
	
	/* 文本溢出省略 */
	.text-ellipsis {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	
	/* 多行文本溢出省略 */
	.multi-ellipsis-2 {
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 2;
		overflow: hidden;
	}
	
	/* 细分割线 */
	.divider {
		height: 1px;
		background-color: rgba(228, 237, 255, 0.8);
		margin: 24rpx 0;
	}
	
	/* 动画过渡 */
	.fade-enter-active, .fade-leave-active {
		transition: opacity 0.3s;
	}
	.fade-enter, .fade-leave-to {
		opacity: 0;
	}
	
	/* 图标通用样式 */
	.icon-wrapper {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 80rpx;
		height: 80rpx;
		border-radius: 40rpx;
		background: rgba(228, 237, 255, 0.6);
		color: #3570EC;
		transition: all 0.3s;
	}
	
	.icon-wrapper:active {
		transform: scale(0.95);
		background: rgba(228, 237, 255, 0.9);
	}
	
	/* 波浪效果 */
	.wave-bg {
		position: relative;
		overflow: hidden;
	}
	
	.wave-bg::before {
		content: '';
		position: absolute;
		top: -180rpx;
		left: -300rpx;
		width: 200%;
		height: 250rpx;
		background: rgba(228, 237, 255, 0.4);
		border-radius: 50%;
		transform: rotate(-8deg);
		z-index: -1;
	}
</style> 