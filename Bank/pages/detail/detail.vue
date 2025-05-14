<template>
	<view class="container">
		<view class="header wave-bg">
			<view class="back-btn" @click="goBack">
				<span class="iconfont icon-back"></span>
			</view>
			<view class="title">问答详情</view>
			<view class="action-btn" @click="reaskQuestion">
				<span class="iconfont icon-ask"></span>
			</view>
		</view>
		
		<view class="content">
			<view class="detail-card">
				<view class="detail-time">{{detail.time || '未知时间'}}</view>
				
				<!-- 问题部分 -->
				<view class="question-section">
					<view class="section-title">我的提问</view>
					<view class="question-content">{{detail.question}}</view>
				</view>
				
				<!-- 回答部分 -->
				<view class="answer-section">
					<view class="section-title">AI回答</view>
					<view class="answer-content">{{detail.answer}}</view>
					<view class="answer-tools">
						<view class="tool-btn copy-btn" @click="copyAnswer">
							<view class="tool-icon">
								<span class="iconfont icon-copy"></span>
							</view>
							<span class="tool-text">复制</span>
						</view>
						<view class="tool-btn voice-btn" @click="playVoice">
							<view class="tool-icon">
								<span class="iconfont icon-voice"></span>
							</view>
							<span class="tool-text">朗读</span>
						</view>
						<view class="tool-btn share-btn" @click="shareAnswer">
							<view class="tool-icon">
								<span class="iconfont icon-share"></span>
							</view>
							<span class="tool-text">分享</span>
						</view>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				id: '',
				index: -1,
				detail: {
					id: '',
					time: '',
					question: '',
					answer: ''
				}
			}
		},
		onLoad(options) {
			if (options.id) {
				this.id = options.id;
				if (options.index) {
					this.index = parseInt(options.index);
				}
				this.getDetailData();
			}
		},
		methods: {
			// 获取详情数据
			getDetailData() {
				// 先尝试从本地存储获取历史记录
				try {
					const historyData = uni.getStorageSync('chat_history');
					if (historyData && this.index >= 0) {
						const historyList = JSON.parse(historyData);
						// 注意：历史页面的数据是倒序的，所以这里需要反转索引
						const reversedIndex = historyList.length - 1 - this.index;
						if (reversedIndex >= 0 && reversedIndex < historyList.length) {
							this.detail = historyList[reversedIndex];
							return;
						}
					}
				} catch (e) {
					console.error('读取历史记录失败:', e);
				}
				
				// 如果从本地存储获取失败，使用模拟数据
				this.getMockData();
			},
			
			// 获取模拟数据
			getMockData() {
				// 模拟从服务器或本地存储获取数据
				const mockData = {
					'001': {
						id: '001',
						time: '2023-10-15 14:30',
						question: '如何办理信用卡？',
						answer: '您可以通过以下几种方式申请办理信用卡：\n\n1. 手机银行APP申请：下载我行手机银行APP，登录后在"信用卡"栏目选择"申请信用卡"，按提示填写个人信息并上传证件照片即可。\n\n2. 网上银行申请：登录我行网上银行，在"信用卡"栏目选择"在线申请"，填写申请表并提交资料。\n\n3. 银行网点申请：携带本人身份证、收入证明等资料前往任一网点柜台办理。\n\n申请条件一般包括：年龄在18-65周岁，有稳定收入来源，个人信用记录良好等。我行现有多种信用卡产品，如标准卡、金卡、白金卡等，每种卡有不同的额度和权益，您可以根据自身需求选择。\n\n申请审核通常需要5-7个工作日，审核通过后，卡片将在7个工作日内寄出。'
					},
					'002': {
						id: '002',
						time: '2023-10-14 09:45',
						question: '车险理赔流程是怎样的？',
						answer: '车险理赔流程一般包括以下步骤：\n\n1. 报案：事故发生后应立即拨打保险公司客服电话报案，同时根据情况报警。\n\n2. 现场查勘：保险公司会指派查勘员到现场查看车辆损失情况，并拍照记录。\n\n3. 定损：查勘员会评估车辆的损失程度并出具定损单。\n\n4. 提交理赔资料：需要提交的资料一般包括：\n   - 保险单正本\n   - 驾驶证、行驶证复印件\n   - 事故责任认定书\n   - 维修发票\n   - 索赔申请书\n   - 被保险人身份证明\n   - 车辆照片等\n\n5. 审核：保险公司对资料进行审核。\n\n6. 赔付：审核通过后，保险公司进行赔款支付。\n\n需要注意的是，不同类型的事故和险种理赔流程可能有所不同。建议您在出险后第一时间联系您的保险顾问或直接联系保险公司客服，以获得最准确的指导。'
					},
					'003': {
						id: '003',
						time: '2023-10-13 16:20',
						question: '理财产品有哪些风险？',
						answer: '理财产品主要存在以下几种风险：\n\n1. 市场风险：由于市场价格变动导致投资收益或本金发生损失的可能性。如股票价格波动、利率变化、汇率变动等。\n\n2. 信用风险：交易对手不履行合约义务的风险，可能导致本金和收益损失。\n\n3. 流动性风险：因市场流动性不足或投资期限较长，无法及时将资产变现的风险。\n\n4. 政策风险：因国家宏观政策、监管政策变化导致的投资环境变化风险。\n\n5. 操作风险：因内部流程不完善、人为错误、系统故障等原因导致的损失风险。\n\n6. 通货膨胀风险：通货膨胀导致货币购买力下降，实际收益率降低的风险。\n\n不同类型的理财产品风险程度不同：\n- 银行存款：风险最低，但收益也较低\n- 货币基金：风险较低，流动性好\n- 债券类产品：风险适中\n- 混合型基金：风险较高\n- 股票型基金和股票：风险最高，但潜在收益也高\n\n建议您根据自身风险承受能力选择合适的理财产品，不要将全部资金投入高风险产品，适当分散投资可以降低整体风险。'
					}
				};
				
				if (mockData[this.id]) {
					this.detail = mockData[this.id];
				} else {
					uni.showToast({
						title: '数据不存在',
						icon: 'none'
					});
				}
			},
			
			// 返回上一页
			goBack() {
				uni.navigateBack();
			},
			
			// 重新提问
			reaskQuestion() {
				// 回到主页并预填写问题
				const pages = getCurrentPages();
				const indexPage = pages.find(page => page.route === 'pages/index/index');
				
				if (indexPage) {
					// 如果主页存在，直接通信
					uni.$emit('fillQuestion', {
						question: this.detail.question
					});
					uni.navigateBack({
						delta: getCurrentPages().length - pages.indexOf(indexPage) - 1
					});
				} else {
					// 如果主页不在栈中，重新打开
					uni.reLaunch({
						url: '/pages/index/index?question=' + encodeURIComponent(this.detail.question)
					});
				}
			},
			
			// 复制回答
			copyAnswer() {
				uni.setClipboardData({
					data: this.detail.answer,
					success: () => {
						uni.showToast({
							title: '已复制到剪贴板',
							icon: 'none'
						});
					}
				});
			},
			
			// 语音播报
			playVoice() {
				// 使用TTS服务播放语音
				uni.showToast({
					title: '语音播放中...',
					icon: 'none',
					duration: 2000
				});
				
				// 调用语音合成服务
				try {
					// 优先使用App全局语音服务
					if (getApp().globalData.textToSpeech) {
						getApp().globalData.textToSpeech.speak({
							text: this.detail.answer,
							volume: 1.0,
							rate: 1.0,
							pitch: 1.0
						});
						console.log("使用原生语音合成服务");
					} else {
						// 回退到Vue原型上定义的服务
						if (this.$textToSpeech && this.$textToSpeech.speak) {
							this.$textToSpeech.speak(this.detail.answer)
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
			
			// 分享回答
			shareAnswer() {
				uni.showShareMenu({
					withShareTicket: true,
					menus: ['shareAppMessage', 'shareTimeline']
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
	
	/* 头部 */
	.header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		height: 100rpx;
		background: linear-gradient(135deg, #3570EC, #5A7CFF);
		padding: 0 30rpx;
		box-shadow: 0 4rpx 20rpx rgba(53, 112, 236, 0.2);
	}
	
	.title {
		font-size: 36rpx;
		font-weight: 600;
		color: #FFFFFF;
	}
	
	.back-btn, .action-btn {
		width: 60rpx;
		height: 60rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #FFFFFF;
	}
	
	/* 内容区 */
	.content {
		flex: 1;
		padding: 30rpx;
	}
	
	.detail-card {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 36rpx;
		box-shadow: 0 8rpx 30rpx rgba(0, 0, 0, 0.05);
		border: 1rpx solid rgba(228, 237, 255, 0.8);
	}
	
	.detail-time {
		font-size: 24rpx;
		color: #999999;
		margin-bottom: 36rpx;
	}
	
	.section-title {
		font-size: 30rpx;
		color: #3570EC;
		margin-bottom: 24rpx;
		display: flex;
		align-items: center;
		font-weight: 500;
	}
	
	.section-title:before {
		content: '';
		display: inline-block;
		width: 8rpx;
		height: 30rpx;
		background: linear-gradient(to bottom, #3570EC, #5A7CFF);
		border-radius: 4rpx;
		margin-right: 16rpx;
	}
	
	/* 问题部分 */
	.question-section {
		margin-bottom: 40rpx;
	}
	
	.question-content {
		font-size: 32rpx;
		color: #333333;
		font-weight: 500;
		line-height: 1.6;
		background-color: rgba(228, 237, 255, 0.4);
		padding: 28rpx;
		border-radius: 20rpx;
		border-left: 6rpx solid #3570EC;
	}
	
	/* 回答部分 */
	.answer-section {
		padding-top: 36rpx;
		border-top: 1rpx solid rgba(228, 237, 255, 0.8);
	}
	
	.answer-content {
		font-size: 30rpx;
		color: #333333;
		line-height: 1.8;
		white-space: pre-wrap;
		background-color: #f8faff;
		padding: 28rpx;
		border-radius: 20rpx;
	}
	
	.answer-tools {
		display: flex;
		margin-top: 40rpx;
		justify-content: space-around;
	}
	
	.tool-btn {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		width: 160rpx;
	}
	
	.tool-icon {
		width: 88rpx;
		height: 88rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		background-color: rgba(228, 237, 255, 0.6);
		border-radius: 44rpx;
		margin-bottom: 16rpx;
		transition: all 0.3s;
	}
	
	.tool-btn:active .tool-icon {
		transform: scale(0.95);
		background-color: rgba(228, 237, 255, 0.9);
	}
	
	.copy-btn .tool-icon {
		color: #3570EC;
	}
	
	.voice-btn .tool-icon {
		color: #34A5FF;
	}
	
	.share-btn .tool-icon {
		color: #5E7CFF;
	}
	
	.tool-text {
		font-size: 26rpx;
		color: #666666;
	}
	
	/* 图标字体 */
	.iconfont {
		font-size: 42rpx;
	}
	#1
	.icon-back:before {
		content: "\e679";
	}
	#1
	.icon-ask:before {
		content: "\e67d";
	}
	#1
	.icon-copy:before {
		content: "\e67f";
	}
	#1
	.icon-voice:before {
		content: "\e67e";
	}
	#1
	.icon-share:before {
		content: "\e680";
	}
</style> 