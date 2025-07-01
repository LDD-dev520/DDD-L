//这东西是一个叫吕迪的山西大学的孩子花了三个星期完成的前端后端的项目，遇到很多困难，做出来其实很一般，但是我觉得我一直不断努力一会一定会更好的

<script>
import { createWavDirIfNeeded, checkBaiduApiConfig, initRecorder, initDeviceId } from '@/utils/speech.js';
import * as Storage from '@/utils/storage.js';

export default {
    onLaunch: function() {
        console.log('App Launch');
        // 初始化应用时的逻辑
        this.initApp();
    },
    onShow: function() {
        console.log('App Show');
        // 设置手机状态栏样式
        this.setStatusBarStyle();
    },
    onHide: function() {
        console.log('App Hide');
    },
    onError: function(err) {
        console.error('应用错误:', err);
    },
    onUnload: function() {
        console.log('App Unload');
        // 清理全局事件监听器
        uni.$off();
        
        // 保存必要的数据
        try {
            // 确保聊天历史被保存
            const chatHistory = uni.getStorageSync('chat_messages');
            if (chatHistory && Array.isArray(chatHistory)) {
                Storage.setStorage('chat_history', chatHistory);
            }
        } catch (error) {
            console.error('应用卸载时保存数据失败:', error);
        }
    },
    methods: {
        async initApp() {
            console.log('开始初始化应用...');
            
            // 初始化设备唯一标识符
            try {
                console.log('初始化设备唯一标识符...');
                const deviceId = initDeviceId();
                console.log('设备唯一标识符初始化完成:', deviceId);
            } catch (error) {
                console.error('初始化设备唯一标识符失败:', error);
            }
            
            // 检查本地存储中是否有历史记录，如果没有则初始化
            try {
                // 使用Storage工具类初始化聊天历史
                const history = Storage.getStorage('chat_history');
                if (!history || !Array.isArray(history)) {
                    console.log('初始化聊天历史记录');
                    Storage.setStorage('chat_history', []);
                }
            } catch (storageError) {
                console.error('初始化聊天历史记录失败:', storageError);
                // 确保历史记录被初始化为数组
                Storage.setStorage('chat_history', []);
            }
            
            // 确保wav目录存在
            try {
                console.log('开始初始化wav目录...');
                await createWavDirIfNeeded();
                console.log('wav目录初始化完成');
            } catch (error) {
                console.error('wav目录初始化失败:', error);
            }
            
            // 检查百度API配置
            try {
                console.log('开始检查百度API配置...');
                // 安全调用检查函数
                if (typeof checkBaiduApiConfig !== 'function') {
                    console.error('checkBaiduApiConfig不是一个函数，请检查speech.js导出');
                    throw new Error('语音API函数未正确导出');
                }
                
                const isConfigValid = await checkBaiduApiConfig().catch(err => {
                    console.error('百度API配置检查时发生异常:', err);
                    return false;
                });
                
                if (isConfigValid) {
                    console.log('百度语音API配置有效');
                } else {
                    console.warn('百度语音API配置无效，将使用本地模拟识别');
                    // 显示提示
                    uni.showToast({
                        title: '语音API配置无效，将使用本地识别',
                        icon: 'none',
                        duration: 2000
                    });
                }
            } catch (error) {
                console.error('检查百度API配置时出错:', error);
                // 如果检查失败，我们仍然可以继续初始化其他模块
                uni.showToast({
                    title: '语音API检查失败，将使用本地识别',
                    icon: 'none',
                    duration: 2000
                });
            }
            
            // 初始化语音模块
            this.initSpeechModule();
            
            // 设置状态栏样式
            this.setStatusBarStyle();
            
            console.log('应用初始化完成');
        },
        
        // 设置手机状态栏样式
        setStatusBarStyle() {
            // 获取状态栏高度
            try {
                uni.getSystemInfo({
                    success: (res) => {
                        // 将状态栏高度保存到全局变量
                        getApp().globalData = getApp().globalData || {};
                        getApp().globalData.statusBarHeight = res.statusBarHeight;
                        console.log('状态栏高度:', res.statusBarHeight);
                        
                        // 设置状态栏样式
                        uni.setNavigationBarColor({
                            frontColor: '#ffffff',
                            backgroundColor: '#4080FF'
                        });
                    }
                });
            } catch (e) {
                console.error('获取状态栏高度失败:', e);
            }
        },
        
        initSpeechModule() {
            try {
                console.log('开始初始化语音模块...');
                
                // 初始化录音管理器
                const recorder = initRecorder();
                if (recorder) {
                    console.log('录音管理器初始化成功');
                } else {
                    console.warn('录音管理器初始化失败，语音录制功能可能不可用');
                }
                
                // 检查录音权限
                this.checkRecordPermission();
                
                console.log('语音模块初始化完成');
            } catch (error) {
                console.error('初始化语音模块失败:', error);
            }
        },
        
        checkRecordPermission() {
            // 检查录音权限
            try {
                console.log('开始检查录音权限...');
                
                // 在App环境中检查权限
                if (typeof plus !== 'undefined') {
                    plus.android.requestPermissions(
                        ['android.permission.RECORD_AUDIO'], 
                        function(result) {
                            if (result.granted.length > 0) {
                                console.log('录音权限已授予');
                            } else {
                                console.warn('录音权限被拒绝，语音录制功能不可用');
                                // 显示提示
                                uni.showToast({
                                    title: '录音权限被拒绝，语音功能不可用',
                                    icon: 'none',
                                    duration: 2000
                                });
                            }
                        },
                        function(error) {
                            console.error('请求录音权限失败:', error);
                        }
                    );
                } else {
                    // 非App环境不需要主动申请权限
                    console.log('非App环境，跳过权限检查');
                }
            } catch (error) {
                console.error('检查录音权限失败:', error);
            }
        }
    }
};
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
	
	/* 定义所有图标代码 */
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
	
	.icon-wuguan:before {
		content: "\ec5f";
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
	
	.icon-keyboard-26:before {
		content: "\e6a4";
	}
	
	.icon-mic:before {
		content: "\e6b1";
	}
	
	.icon-back:before {
		content: "\e666";
	}
	
	.icon-settings:before {
		content: "\e683";
	}
	
	.icon-refresh:before {
		content: "\e62d";
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
		line-clamp: 2;
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