/**
 * 语音合成工具类
 * 基于uni-app的语音合成API封装
 * 支持浏览器Web Speech API和原生插件
 */
class TextToSpeech {
    constructor() {
        // 语音播放实例
        this.innerAudioContext = null;
        // 当前播放状态
        this.isPlaying = false;
        // Web Speech API实例
        this.speechSynthesis = null;
        // 当前播放的utterance
        this.currentUtterance = null;
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
            
            // 获取可用的声音列表
            if (window.speechSynthesis.getVoices) {
                // 有些浏览器需要异步获取
                if (window.speechSynthesis.getVoices().length === 0) {
                    window.speechSynthesis.addEventListener('voiceschanged', () => {
                        console.log('可用语音列表:', window.speechSynthesis.getVoices().filter(voice => voice.lang.indexOf('zh') > -1));
                    });
                } else {
                    console.log('可用语音列表:', window.speechSynthesis.getVoices().filter(voice => voice.lang.indexOf('zh') > -1));
                }
            }
        } else {
            console.log('当前环境不支持Web Speech API');
        }
    }

    /**
     * 将文本转换为语音并播放
     * @param {String} text 需要转换的文本
     * @param {Object} options 播放选项
     * @returns {Promise} 返回操作结果的Promise
     */
    speak(text, options = {}) {
        return new Promise((resolve, reject) => {
            if (!text) {
                reject(new Error('文本内容不能为空'));
                return;
            }

            // 如果正在播放，先停止
            if (this.isPlaying) {
                this.stop();
            }

            console.log('开始语音合成:', text);
            
            // 合并选项
            const opts = {
                volume: options.volume || 1.0,  // 音量
                rate: options.rate || 1.0,      // 语速
                pitch: options.pitch || 1.0     // 音调
            };
            
            // 1. 首先尝试使用原生插件
            if (typeof plus !== 'undefined') {
                try {
                    // 使用讯飞语音合成等原生插件
                    const speech = uni.requireNativePlugin('Speech');
                    if (speech && speech.speak) {
                        speech.speak({
                            text: text,
                            volume: opts.volume,
                            rate: opts.rate,
                            pitch: opts.pitch,
                            success: () => {
                                console.log('原生TTS播放完成');
                                resolve();
                            },
                            fail: (err) => {
                                console.error('原生TTS播放失败:', err);
                                // 失败后尝试使用其他方法
                                this._fallbackSpeak(text, opts, resolve, reject);
                            }
                        });
                        return;
                    }
                } catch (e) {
                    console.error('原生语音合成调用失败:', e);
                }
            }
            
            // 2. 尝试使用Web Speech API
            if (this.speechSynthesis) {
                try {
                    const utterance = new SpeechSynthesisUtterance(text);
                    
                    // 设置参数
                    utterance.lang = 'zh-CN';
                    utterance.rate = opts.rate;
                    utterance.pitch = opts.pitch;
                    utterance.volume = opts.volume;
                    
                    // 尝试设置中文声音
                    const voices = this.speechSynthesis.getVoices();
                    const chineseVoice = voices.find(voice => 
                        voice.lang.indexOf('zh') > -1 || 
                        voice.name.toLowerCase().indexOf('chinese') > -1
                    );
                    if (chineseVoice) {
                        utterance.voice = chineseVoice;
                    }
                    
                    // 保存当前utterance用于后续控制
                    this.currentUtterance = utterance;
                    
                    // 设置回调
                    utterance.onstart = () => {
                        console.log('Web Speech API 语音播放开始');
                        this.isPlaying = true;
                    };
                    
                    utterance.onend = () => {
                        console.log('Web Speech API 语音播放结束');
                        this.isPlaying = false;
                        this.currentUtterance = null;
                        resolve();
                    };
                    
                    utterance.onerror = (error) => {
                        console.error('Web Speech API 语音播放错误:', error);
                        this.isPlaying = false;
                        this.currentUtterance = null;
                        
                        // 尝试使用其他方法
                        this._fallbackSpeak(text, opts, resolve, reject);
                    };
                    
                    this.speechSynthesis.speak(utterance);
                    return;
                } catch (e) {
                    console.error('Web Speech API 调用失败:', e);
                }
            }
            
            // 3. 如果前两种方法都失败，使用最后的回退方案
            this._fallbackSpeak(text, opts, resolve, reject);
        });
    }
    
    /**
     * 回退方案：使用uni音频播放或模拟
     * @private
     */
    _fallbackSpeak(text, opts, resolve, reject) {
        // 如果有innerAudioContext，尝试播放在线TTS转换的音频
        if (this.innerAudioContext) {
            // 实际项目中这里应该调用在线TTS服务获取语音URL
            // 例如百度、讯飞等提供的REST API
            // 这里仅做模拟
            
            console.log('尝试使用模拟TTS播放');
            
            // 模拟语音合成过程
            if (typeof uni !== 'undefined') {
                uni.showLoading({
                    title: '正在转换语音...'
                });
            }
            
            setTimeout(() => {
                if (typeof uni !== 'undefined') {
                    uni.hideLoading();
                
                    // 由于没有真实接口，这里仅展示一个提示
                    uni.showToast({
                        title: '正在播放语音',
                        icon: 'none',
                        duration: 2000
                    });
                }
                
                // 模拟播放
                this.isPlaying = true;
                setTimeout(() => {
                    // 模拟播放结束
                    this.isPlaying = false;
                    resolve();
                }, 2000);
            }, 1000);
        } else {
            // 如果所有API都不可用，则显示提示
            console.error('当前环境不支持语音播放');
            if (typeof uni !== 'undefined') {
                uni.showToast({
                    title: '当前环境不支持语音播放',
                    icon: 'none'
                });
            }
            reject(new Error('当前环境不支持语音播放'));
        }
    }

    /**
     * 停止当前播放
     */
    stop() {
        if (this.speechSynthesis) {
            this.speechSynthesis.cancel();
        }
        
        if (this.currentUtterance) {
            this.currentUtterance = null;
        }
        
        if (this.innerAudioContext && this.isPlaying) {
            this.innerAudioContext.stop();
        }
        
        this.isPlaying = false;
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