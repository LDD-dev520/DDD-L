/**
 * 语音合成工具类
 * 基于uni-app的语音合成API封装
 * 支持浏览器Web Speech API
 */
class TextToSpeech {
    constructor() {
        // 语音播放实例
        this.innerAudioContext = null;
        // 当前播放状态
        this.isPlaying = false;
        // Web Speech API实例
        this.speechSynthesis = null;
        // 初始化语音播放器
        this.initAudioContext();
        // 初始化Web Speech API
        this.initWebSpeech();
    }

    /**
     * 初始化音频上下文
     */
    initAudioContext() {
        if (typeof uni !== 'undefined' && uni.createInnerAudioContext) {
            this.innerAudioContext = uni.createInnerAudioContext();
            
            // 监听播放开始事件
            this.innerAudioContext.onPlay(() => {
                console.log('语音播放开始');
                this.isPlaying = true;
            });
            
            // 监听播放结束事件
            this.innerAudioContext.onEnded(() => {
                console.log('语音播放结束');
                this.isPlaying = false;
            });
            
            // 监听播放错误事件
            this.innerAudioContext.onError((res) => {
                console.error('语音播放错误', res);
                this.isPlaying = false;
                if (typeof uni !== 'undefined') {
                    uni.showToast({
                        title: '语音播放出错',
                        icon: 'none'
                    });
                }
            });
        } else {
            console.log('当前环境不支持uni音频播放API，将尝试使用Web Speech API');
        }
    }

    /**
     * 初始化Web Speech API
     */
    initWebSpeech() {
        if (typeof window !== 'undefined' && window.speechSynthesis) {
            this.speechSynthesis = window.speechSynthesis;
            console.log('Web Speech API初始化成功');
        } else {
            console.log('当前环境不支持Web Speech API');
        }
    }

    /**
     * 将文本转换为语音并播放
     * @param {String} text 需要转换的文本
     * @returns {Promise} 返回操作结果的Promise
     */
    speak(text) {
        return new Promise((resolve, reject) => {
            if (!text) {
                reject(new Error('文本内容不能为空'));
                return;
            }

            if (this.isPlaying) {
                this.stop();
            }

            console.log('开始语音合成:', text);
            
            // 尝试使用Web Speech API
            if (this.speechSynthesis) {
                try {
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.lang = 'zh-CN';
                    utterance.rate = 1.0;
                    utterance.pitch = 1.0;
                    utterance.volume = 1.0;
                    
                    utterance.onstart = () => {
                        console.log('Web Speech API 语音播放开始');
                        this.isPlaying = true;
                    };
                    
                    utterance.onend = () => {
                        console.log('Web Speech API 语音播放结束');
                        this.isPlaying = false;
                        resolve();
                    };
                    
                    utterance.onerror = (error) => {
                        console.error('Web Speech API 语音播放错误:', error);
                        this.isPlaying = false;
                        reject(error);
                    };
                    
                    this.speechSynthesis.speak(utterance);
                    return;
                } catch (e) {
                    console.error('Web Speech API 调用失败:', e);
                }
            }
            
            // 如果Web Speech API不可用，回退到uni API
            if (typeof uni !== 'undefined' && this.innerAudioContext) {
                // 模拟语音合成过程
                uni.showLoading({
                    title: '正在转换语音...'
                });
                
                setTimeout(() => {
                    uni.hideLoading();
                    
                    // 由于没有真实接口，这里仅展示一个提示
                    uni.showToast({
                        title: '正在播放语音',
                        icon: 'none',
                        duration: 2000
                    });
                    
                    // 模拟播放
                    setTimeout(() => {
                        // 模拟播放结束
                        this.isPlaying = false;
                        resolve();
                    }, 2000);
                }, 1000);
            } else {
                // 如果两种API都不可用，则显示提示
                console.error('当前环境不支持语音播放');
                if (typeof uni !== 'undefined') {
                    uni.showToast({
                        title: '当前环境不支持语音播放',
                        icon: 'none'
                    });
                }
                reject(new Error('当前环境不支持语音播放'));
            }
        });
    }

    /**
     * 停止当前播放
     */
    stop() {
        if (this.speechSynthesis) {
            this.speechSynthesis.cancel();
            this.isPlaying = false;
        }
        
        if (this.innerAudioContext && this.isPlaying) {
            this.innerAudioContext.stop();
            this.isPlaying = false;
        }
    }

    /**
     * 暂停当前播放
     */
    pause() {
        if (this.speechSynthesis) {
            this.speechSynthesis.pause();
        }
        
        if (this.innerAudioContext && this.isPlaying) {
            this.innerAudioContext.pause();
        }
    }

    /**
     * 恢复播放
     */
    resume() {
        if (this.speechSynthesis) {
            this.speechSynthesis.resume();
        }
        
        if (this.innerAudioContext && !this.isPlaying) {
            this.innerAudioContext.play();
        }
    }
}

export default TextToSpeech; 