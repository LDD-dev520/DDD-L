/**
 * 通用工具函数
 */

/**
 * 格式化时间
 * @param {Date} date 日期对象
 * @param {boolean} showSeconds 是否显示秒
 * @returns {string} 格式化后的时间字符串
 */
export function formatTime(date, showSeconds = false) {
  if (!date) return '';
  if (typeof date === 'string') {
    date = new Date(date);
  }
  
  const year = date.getFullYear();
  const month = padZero(date.getMonth() + 1);
  const day = padZero(date.getDate());
  const hour = padZero(date.getHours());
  const minute = padZero(date.getMinutes());
  const second = padZero(date.getSeconds());
  
  if (isToday(date)) {
    return showSeconds ? `${hour}:${minute}:${second}` : `${hour}:${minute}`;
  } else if (isThisYear(date)) {
    return `${month}-${day} ${hour}:${minute}`;
  } else {
    return `${year}-${month}-${day} ${hour}:${minute}`;
  }
}

/**
 * 数字补零
 * @param {number} num 数字
 * @returns {string} 补零后的字符串
 */
function padZero(num) {
  return num < 10 ? '0' + num : '' + num;
}

/**
 * 判断是否是今天
 * @param {Date} date 日期对象
 * @returns {boolean} 是否是今天
 */
function isToday(date) {
  const today = new Date();
  return date.getDate() === today.getDate() &&
         date.getMonth() === today.getMonth() &&
         date.getFullYear() === today.getFullYear();
}

/**
 * 判断是否是今年
 * @param {Date} date 日期对象
 * @returns {boolean} 是否是今年
 */
function isThisYear(date) {
  const today = new Date();
  return date.getFullYear() === today.getFullYear();
}

/**
 * 格式化文件大小
 * @param {number} bytes 字节数
 * @returns {string} 格式化后的文件大小
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 生成UUID
 * @returns {string} UUID字符串
 */
export function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * 深拷贝对象
 * @param {Object} obj 要拷贝的对象
 * @returns {Object} 拷贝后的对象
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime());
  }
  
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item));
  }
  
  if (obj instanceof Object) {
    const copy = {};
    Object.keys(obj).forEach(key => {
      copy[key] = deepClone(obj[key]);
    });
    return copy;
  }
  
  return obj;
}

/**
 * 防抖函数
 * @param {Function} func 要执行的函数
 * @param {number} wait 等待时间
 * @returns {Function} 防抖后的函数
 */
export function debounce(func, wait = 300) {
  let timeout;
  return function(...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      func.apply(context, args);
    }, wait);
  };
}

/**
 * 节流函数
 * @param {Function} func 要执行的函数
 * @param {number} wait 等待时间
 * @returns {Function} 节流后的函数
 */
export function throttle(func, wait = 300) {
  let timeout = null;
  let previous = 0;
  
  return function(...args) {
    const context = this;
    const now = Date.now();
    
    if (now - previous > wait) {
      if (timeout) {
        clearTimeout(timeout);
        timeout = null;
      }
      func.apply(context, args);
      previous = now;
    } else if (!timeout) {
      timeout = setTimeout(() => {
        previous = Date.now();
        timeout = null;
        func.apply(context, args);
      }, wait - (now - previous));
    }
  };
}

/**
 * 获取URL参数
 * @param {string} url URL字符串
 * @param {string} name 参数名
 * @returns {string|null} 参数值
 */
export function getUrlParam(url, name) {
  const reg = new RegExp('(^|&|\\?)' + name + '=([^&]*)(&|$)');
  const r = url.match(reg);
  if (r != null) {
    return decodeURIComponent(r[2]);
  }
  return null;
}

/**
 * 判断是否是空对象
 * @param {Object} obj 对象
 * @returns {boolean} 是否是空对象
 */
export function isEmptyObject(obj) {
  if (!obj || typeof obj !== 'object') {
    return true;
  }
  return Object.keys(obj).length === 0;
}

/**
 * 随机生成指定范围内的整数
 * @param {number} min 最小值
 * @param {number} max 最大值
 * @returns {number} 随机整数
 */
export function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

/**
 * 数组乱序
 * @param {Array} arr 数组
 * @returns {Array} 乱序后的数组
 */
export function shuffleArray(arr) {
  const result = [...arr];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
} 