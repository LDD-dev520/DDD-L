/**
 * 存储工具类
 * 处理本地数据存储
 */

/**
 * 设置存储数据
 * @param {string} key 键名
 * @param {any} data 数据
 * @param {number} expires 过期时间（毫秒），可选
 * @returns {boolean} 是否成功
 */
export function setStorage(key, data, expires = 0) {
  try {
    const item = {
      data,
      time: Date.now()
    };
    
    // 如果设置了过期时间
    if (expires > 0) {
      item.expires = expires;
    }
    
    uni.setStorageSync(key, item);
    return true;
  } catch (e) {
    console.error('存储数据失败:', e);
    return false;
  }
}

/**
 * 获取存储数据
 * @param {string} key 键名
 * @param {any} defaultValue 默认值，可选
 * @returns {any} 存储的数据或默认值
 */
export function getStorage(key, defaultValue = null) {
  try {
    const item = uni.getStorageSync(key);
    
    // 如果数据不存在
    if (!item) {
      return defaultValue;
    }
    
    // 如果数据已过期
    if (item.expires && Date.now() - item.time > item.expires) {
      uni.removeStorageSync(key);
      return defaultValue;
    }
    
    return item.data;
  } catch (e) {
    console.error('获取数据失败:', e);
    return defaultValue;
  }
}

/**
 * 移除存储数据
 * @param {string} key 键名
 * @returns {boolean} 是否成功
 */
export function removeStorage(key) {
  try {
    uni.removeStorageSync(key);
    return true;
  } catch (e) {
    console.error('移除数据失败:', e);
    return false;
  }
}

/**
 * 清空所有存储数据
 * @returns {boolean} 是否成功
 */
export function clearStorage() {
  try {
    uni.clearStorageSync();
    return true;
  } catch (e) {
    console.error('清空数据失败:', e);
    return false;
  }
}

/**
 * 获取所有存储的键名
 * @returns {Array} 键名数组
 */
export function getStorageKeys() {
  try {
    const res = uni.getStorageInfoSync();
    return res.keys || [];
  } catch (e) {
    console.error('获取存储信息失败:', e);
    return [];
  }
}

/**
 * 获取存储使用情况
 * @returns {Object} 存储使用情况
 */
export function getStorageInfo() {
  try {
    return uni.getStorageInfoSync();
  } catch (e) {
    console.error('获取存储信息失败:', e);
    return {
      keys: [],
      currentSize: 0,
      limitSize: 0
    };
  }
}

/**
 * 存储聊天历史记录
 * @param {Object} chatItem 聊天记录项
 * @returns {boolean} 是否成功
 */
export function saveChatHistory(chatItem) {
  try {
    if (!chatItem) {
      console.error('保存聊天历史失败: 聊天记录项为空');
      return false;
    }
    
    // 获取现有历史记录
    let history = getStorage('chat_history', []);
    
    // 确保history是一个数组
    if (!Array.isArray(history)) {
      console.warn('历史记录不是数组，重置为空数组');
      history = [];
    }
    
    // 添加新记录
    history.push({
      ...chatItem,
      time: chatItem.time || Date.now()
    });
    
    // 限制历史记录数量，最多保存100条
    const limitedHistory = history.slice(-100);
    
    // 保存回存储
    return setStorage('chat_history', limitedHistory);
  } catch (e) {
    console.error('保存聊天历史失败:', e);
    return false;
  }
}

/**
 * 获取聊天历史记录
 * @param {number} limit 限制数量，可选
 * @returns {Array} 历史记录数组
 */
export function getChatHistory(limit = 0) {
  try {
    const history = getStorage('chat_history', []);
    
    // 确保history始终是一个数组
    if (!Array.isArray(history)) {
      console.warn('历史记录不是数组，返回空数组');
      return [];
    }
    
    // 如果指定了限制数量
    if (limit > 0 && history.length > limit) {
      return history.slice(-limit);
    }
    
    return history;
  } catch (e) {
    console.error('获取聊天历史失败:', e);
    return [];
  }
}

/**
 * 清空聊天历史记录
 * @returns {boolean} 是否成功
 */
export function clearChatHistory() {
  return setStorage('chat_history', []);
}

/**
 * 删除指定的聊天记录
 * @param {number} index 索引
 * @returns {boolean} 是否成功
 */
export function deleteChatItem(index) {
  try {
    const history = getStorage('chat_history', []);
    
    if (index >= 0 && index < history.length) {
      history.splice(index, 1);
      return setStorage('chat_history', history);
    }
    
    return false;
  } catch (e) {
    console.error('删除聊天记录失败:', e);
    return false;
  }
}

/**
 * 添加聊天历史记录（saveChatHistory的别名，用于兼容性）
 * @param {Object} chatItem 聊天记录项
 * @returns {boolean} 是否成功
 */
export function addChatHistory(chatItem) {
  return saveChatHistory(chatItem);
} 