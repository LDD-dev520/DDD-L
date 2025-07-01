/**
 * API工具类
 * 用于处理与后端Ollama服务的交互
 */

// API基础URL - 根据实际情况修改为Ollama服务器地址和端口
// 注意：在模拟器或真机上，不能使用127.0.0.1或localhost，必须使用电脑的实际IP地址
const API_BASE_URL = 'http://192.168.1.8:8000'; // 请替换为您电脑的实际IP地址

/**
 * 测试后端连接
 * @returns {Promise} 返回Promise，包含连接状态
 */
export function testConnection() {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE_URL}/api/status`,
      method: 'GET',
      timeout: 5000,
      success: (res) => {
        if (res.statusCode === 200 && res.data && res.data.success) {
          resolve({
            connected: true,
            message: res.data.message || '连接成功',
            datetime: res.data.datetime,
            response: res.data
          });
        } else {
          resolve({
            connected: false,
            message: res.data?.message || `请求异常，状态码: ${res.statusCode}`,
            statusCode: res.statusCode
          });
        }
      },
      fail: (err) => {
        resolve({
          connected: false,
          message: err.errMsg || '连接失败',
          error: err
        });
      }
    });
  });
}

/**
 * 获取问题回答
 * @param {string} question 问题文本
 * @param {Object} options 可选参数
 * @returns {Promise} 返回Promise，包含回答
 */
export function getAnswer(question, options = {}) {
  console.log('[API] 发送问题:', question);
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE_URL}/chat`,
      method: 'POST',
      data: {
        user_id: options.user_id || 'default_user',
        query: question
      },
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data) {
          resolve({
            success: true,
            answer: res.data.answer,
            used_knowledge: res.data.docs && res.data.docs.length > 0,
            knowledge_items: res.data.docs || [],
            processing_time: 0
          });
        } else {
          reject({
            success: false,
            error: `请求异常，状态码: ${res.statusCode}`,
            statusCode: res.statusCode
          });
        }
      },
      fail: (err) => {
        console.error('[API] 获取回答失败:', err);
        reject({
          success: false,
          error: err.errMsg || '网络请求失败'
        });
      }
    });
  });
}

/**
 * 搜索知识库
 * @param {string} query 搜索查询
 * @param {number} limit 结果数量限制 
 * @returns {Promise} 返回Promise，包含搜索结果
 */
export function searchKnowledge(query, limit = 5) {
  console.log('[API] 搜索知识库:', query);
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE_URL}/api/knowledge/search`,
      method: 'POST',
      data: {
        query: query,
        limit: limit
      },
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data) {
          resolve({
            success: true,
            results: res.data.results || [],
            count: res.data.count || 0
          });
        } else {
          reject({
            success: false,
            error: `请求异常，状态码: ${res.statusCode}`,
            statusCode: res.statusCode
          });
        }
      },
      fail: (err) => {
        console.error('[API] 搜索知识库失败:', err);
        reject({
          success: false,
          error: err.errMsg || '网络请求失败'
        });
      }
    });
  });
}

/**
 * 测试知识库服务连接
 * @returns {Promise} 返回Promise，包含连接状态
 */
export function testKnowledgeConnection() {
  console.log('[API] 测试知识库连接');
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE_URL}/`,
      method: 'GET',
      timeout: 5000,
      success: (res) => {
        if (res.statusCode === 200) {
          resolve({
            connected: true,
            message: res.data.message || '连接成功',
            response: res.data
          });
        } else {
          resolve({
            connected: false,
            message: res.data?.message || `请求异常，状态码: ${res.statusCode}`,
            statusCode: res.statusCode
          });
        }
      },
      fail: (err) => {
        resolve({
          connected: false,
          message: err.errMsg || '连接失败',
          error: err
        });
      }
    });
  });
}

/**
 * 获取知识库集合列表
 * @returns {Promise} 返回Promise，包含集合列表
 */
export function getCollections() {
  console.log('[API] 获取知识库统计信息');
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE_URL}/api/knowledge/stats`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200 && res.data) {
          resolve({
            success: true,
            collections: [{
              name: "kb_store",
              count: res.data.count || 0
            }]
          });
        } else {
          reject({
            success: false,
            error: res.data?.error || `请求异常，状态码: ${res.statusCode}`,
            statusCode: res.statusCode
          });
        }
      },
      fail: (err) => {
        console.error('[API] 获取知识库统计信息失败:', err);
        reject({
          success: false,
          error: err.errMsg || '网络请求失败'
        });
      }
    });
  });
}

/**
 * 聊天（结合知识库检索）
 * @param {Array} messages 消息列表
 * @param {string} query 用于知识库检索的查询
 * @returns {Promise} 返回Promise，包含回复
 */
export function chatWithKnowledge(messages, query) {
  console.log('[API] 知识库聊天，查询:', query);
  
  // 获取最后一条用户消息作为查询
  const userMessage = messages.find(msg => msg.role === 'user');
  const user_id = 'default_user';
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE_URL}/chat`,
      method: 'POST',
      data: {
        user_id: user_id,
        query: query || userMessage?.content
      },
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data) {
          resolve({
            success: true,
            response: {
              message: {
                content: res.data.answer
              },
              context_documents: res.data.docs || []
            }
          });
        } else {
          reject({
            success: false,
            error: res.data?.error || `请求异常，状态码: ${res.statusCode}`,
            statusCode: res.statusCode
          });
        }
      },
      fail: (err) => {
        console.error('[API] 知识库聊天失败:', err);
        reject({
          success: false,
          error: err.errMsg || '网络请求失败'
        });
      }
    });
  });
} 