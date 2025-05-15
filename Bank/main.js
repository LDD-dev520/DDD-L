import Vue from 'vue'
import App from './App'

Vue.config.productionTip = false

// 引入语音识别和语音合成的工具类
import SpeechRecognition from './utils/speech-recognition.js'
import TextToSpeech from './utils/text-to-speech.js'
// 引入知识库服务和ModelBuilder
import KnowledgeService from './utils/knowledge-service.js'
import ModelBuilder from './utils/model-builder.js'

// 全局挂载语音工具
Vue.prototype.$speechRecognition = new SpeechRecognition()
Vue.prototype.$textToSpeech = new TextToSpeech()

// 设置API密钥（实际应用中应从安全存储或环境变量获取）
// 为了安全建议在实际项目中从服务器端或安全的配置获取
const API_CONFIG = {
  // 百度千帆API配置
  apiKey: 'UenGRY86Xhrmgrmi0uIGyY5Q',
  secretKey: 'Lb8BkiDEz2BUQArgmpJpCtwM2Yq40O7a',
  model: 'ERNIE-4.5-turbo-vl-32k',
  endpoint: 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie_4.5_turbo_vl_32k'
}

// 全局挂载知识库服务和ModelBuilder
Vue.prototype.$knowledgeService = new KnowledgeService()
Vue.prototype.$modelBuilder = new ModelBuilder({
  apiKey: API_CONFIG.apiKey,
  secretKey: API_CONFIG.secretKey,
  model: API_CONFIG.model,
  endpoint: API_CONFIG.endpoint
})

console.log('初始化全局ModelBuilder实例：' + API_CONFIG.model);

App.mpType = 'app'

// 全局混入，为所有组件添加语音相关方法
Vue.mixin({
  beforeCreate() {
    // 在组件实例创建前初始化
    const app = getApp();
    
    // 确保全局组件可以访问TextToSpeech服务
    if (app && app.globalData) {
      this.$textToSpeech = {
        speak(text) {
          return new Promise((resolve, reject) => {
            try {
              if (app.globalData.textToSpeech) {
                app.globalData.textToSpeech.speak({
                  text: text,
                  volume: 1.0,
                  rate: 1.0,
                  pitch: 1.0
                });
                resolve();
              } else {
                console.log('语音合成服务未初始化，尝试使用本地服务');
                // 使用Vue原型上的服务作为备选
                if (Vue.prototype.$textToSpeech) {
                  Vue.prototype.$textToSpeech.speak(text)
                    .then(() => resolve())
                    .catch(e => reject(e));
                } else {
                  console.error('语音合成服务未初始化');
                  reject(new Error('语音合成服务未初始化'));
                }
              }
            } catch (e) {
              console.error('语音播放失败:', e);
              reject(e);
            }
          });
        }
      };
      
      // 确保全局组件可以访问SpeechRecognition服务
      this.$speechRecognition = {
        startRecording() {
          try {
            if (app.globalData.speechRecognition) {
              app.globalData.speechRecognition.startRecognize();
              return true;
            } else if (Vue.prototype.$speechRecognition) {
              // 使用Vue原型上的服务作为备选
              return Vue.prototype.$speechRecognition.startRecording();
            }
            return false;
          } catch (e) {
            console.error('开始录音失败:', e);
            return false;
          }
        },
        stopRecording() {
          try {
            if (app.globalData.speechRecognition) {
              app.globalData.speechRecognition.stopRecognize();
              return true;
            } else if (Vue.prototype.$speechRecognition) {
              // 使用Vue原型上的服务作为备选
              return Vue.prototype.$speechRecognition.stopRecording();
            }
            return false;
          } catch (e) {
            console.error('停止录音失败:', e);
            return false;
          }
        },
        recognizeSpeech(text) {
          return new Promise((resolve, reject) => {
            // 模拟语音识别结果
            // 实际项目中应该调用真实的语音识别API
            setTimeout(() => {
              if (text === 'temp') {
                resolve('如何办理银行卡挂失？');
              } else {
                resolve(text || '未能识别您的语音');
              }
            }, 500);
          });
        }
      };
    }
  }
});

const app = new Vue({
    ...App
})
app.$mount() 