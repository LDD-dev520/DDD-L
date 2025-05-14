<template>
	<view class="container">
		<view class="header wave-bg">
			<view class="back-btn" @click="goBack">
				<text class="iconfont icon-back"></text>
			</view>
			<view class="title">历史记录</view>
			<view class="clear-btn" @click="showClearConfirm">
				<text class="iconfont icon-delete"></text>
			</view>
		</view>
		
		<view class="content">
			<view class="history-list">
				<view class="history-item" v-for="(item, index) in historyList" :key="index" @click="viewDetail(item, index)">
					<view class="history-meta">
						<view class="history-time">{{item.time || '未知时间'}}</view>
						<view class="history-indicator">
							<text class="iconfont icon-right"></text>
						</view>
					</view>
					<view class="history-question">{{item.question}}</view>
					<view class="history-answer multi-ellipsis-2">{{item.answer}}</view>
				</view>
				
				<view class="empty-state" v-if="historyList.length === 0">
					<image src="../../static/images/empty-data.png" mode="aspectFit" class="empty-image"></image>
					<view class="empty-text">暂无历史记录</view>
					<view class="btn btn-primary" style="width: 70%; margin-top: 40rpx;" @click="goToHome">去提问</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				historyList: []
			}
		},
		onShow() {
			// 每次显示页面时获取最新历史记录
			this.loadHistoryData();
		},
		methods: {
			// 加载历史记录数据
			loadHistoryData() {
				try {
					const historyData = uni.getStorageSync('chat_history');
					if (historyData) {
						this.historyList = JSON.parse(historyData);
						// 按时间倒序排列，最新的记录在最前面
						this.historyList.reverse();
					} else {
						// 如果没有历史记录，提供一些示例数据
						this.initData();
					}
				} catch (e) {
					console.error('读取历史记录失败:', e);
					// 加载失败时使用示例数据
					this.initData();
				}
			},
			
			// 初始化示例数据
			initData() {
				// 示例历史数据
				this.historyList = [
					{
						id: '001',
						time: '2023-10-15 14:30',
						question: '如何办理信用卡？',
						answer: '您可以通过手机银行APP、网上银行或者前往银行网点申请办理信用卡。申请时需要准备好您的身份证件，并填写相关申请资料。我行目前有多种信用卡产品可供选择...'
					},
					{
						id: '002',
						time: '2023-10-14 09:45',
						question: '车险理赔流程是怎样的？',
						answer: '车险理赔一般包括以下步骤：1.事故发生后立即报警和报案；2.保险公司查勘定损；3.提交理赔资料；4.保险公司审核；5.获得赔付。建议您出险后第一时间联系保险公司...'
					},
					{
						id: '003',
						time: '2023-10-13 16:20',
						question: '理财产品有哪些风险？',
						answer: '理财产品主要包括市场风险、信用风险、流动性风险等。市场风险是指因市场价格波动导致的损失可能；信用风险是指交易对手不履行义务的风险；流动性风险是指资产不能及时变现的风险...'
					}
				];
			},
			
			// 返回上一页
			goBack() {
				uni.navigateBack();
			},
			
			// 前往首页
			goToHome() {
				uni.reLaunch({
					url: '/pages/index/index'
				});
			},
			
			// 查看详情并重新提问
			viewDetail(item, index) {
				// 为每个记录生成一个唯一ID（如果没有的话）
				const id = item.id || `history_${index}_${Date.now()}`;
				
				// 跳转到详情页
				uni.navigateTo({
					url: `/pages/detail/detail?id=${id}&index=${index}`
				});
			},
			
			// 显示清空确认对话框
			showClearConfirm() {
				uni.showModal({
					title: '提示',
					content: '确定要清空所有历史记录吗？',
					success: (res) => {
						if (res.confirm) {
							this.clearHistory();
						}
					}
				});
			},
			
			// 清空历史记录
			clearHistory() {
				try {
					uni.removeStorageSync('chat_history');
					this.historyList = [];
					uni.showToast({
						title: '历史记录已清空',
						icon: 'success'
					});
				} catch (e) {
					console.error('清空历史记录失败:', e);
					uni.showToast({
						title: '操作失败，请重试',
						icon: 'none'
					});
				}
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
	
	.back-btn, .clear-btn {
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
	
	.history-list {
		margin-bottom: 30rpx;
	}
	
	.history-item {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 30rpx;
		margin-bottom: 30rpx;
		box-shadow: 0 8rpx 30rpx rgba(0, 0, 0, 0.05);
		position: relative;
		transition: all 0.3s;
		border: 1rpx solid rgba(228, 237, 255, 0.8);
	}
	
	.history-item:active {
		transform: scale(0.98);
		box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.03);
	}
	
	.history-meta {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20rpx;
	}
	
	.history-time {
		font-size: 24rpx;
		color: #999999;
	}
	
	.history-indicator {
		font-size: 24rpx;
		color: #3570EC;
	}
	
	.history-question {
		font-size: 32rpx;
		font-weight: 500;
		color: #333333;
		margin-bottom: 20rpx;
		padding-left: 16rpx;
		border-left: 4rpx solid #3570EC;
		line-height: 1.5;
	}
	
	.history-answer {
		font-size: 28rpx;
		color: #666666;
		background-color: rgba(228, 237, 255, 0.4);
		padding: 20rpx 24rpx;
		border-radius: 16rpx;
		line-height: 1.5;
	}
	
	/* 空记录提示 */
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 120rpx 0;
	}
	
	.empty-image {
		width: 260rpx;
		height: 260rpx;
		margin-bottom: 40rpx;
	}
	
	.empty-text {
		font-size: 32rpx;
		color: #999999;
		margin-bottom: 20rpx;
	}
	
	/* 图标字体 */
	.iconfont {
		font-size: 42rpx;
	}
	
	.icon-back:before {
		content: "\e679";
	}
	
	.icon-delete:before {
		content: "\e684";
	}
	
	.icon-right:before {
		content: "\e670";
	}
</style> 