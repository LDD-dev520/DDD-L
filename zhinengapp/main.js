import App from './App'
import * as DeepSeek from './utils/deepseek.js'

// #ifndef VUE3
import Vue from 'vue'
Vue.config.productionTip = false
App.mpType = 'app'

// 初始化DeepSeek配置
DeepSeek.setConfig({
  modelName: 'deepseek-r1:7b',
  temperature: 0.7,
  maxTokens: 2000,
  useKnowledge: true
});

// 输出DeepSeek配置信息
console.log('DeepSeek配置信息:', DeepSeek.getConfig());

// 全局混入
Vue.mixin({
  methods: {
    // 全局方法
  }
})

// 全局过滤器
Vue.filter('dateFormat', function(timestamp, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!timestamp) return '';
  
  const date = new Date(timestamp);
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  const hour = date.getHours().toString().padStart(2, '0');
  const minute = date.getMinutes().toString().padStart(2, '0');
  const second = date.getSeconds().toString().padStart(2, '0');
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hour)
    .replace('mm', minute)
    .replace('ss', second);
});

// 创建Vue实例
const app = new Vue({
  ...App
})
app.$mount()
// #endif

// #ifdef VUE3
import { createSSRApp } from 'vue'
export function createApp() {
  const app = createSSRApp(App)
  
  // 全局方法
  app.config.globalProperties.$utils = {
    // 工具方法
  }
  
  return {
    app
  }
}
// #endif 