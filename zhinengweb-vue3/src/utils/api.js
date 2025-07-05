import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000', // 后端API的基础URL，根据实际情况修改
  timeout: 30000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加认证信息，如token
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers['Authorization'] = `Bearer ${token}`;
    // }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('API响应成功:', response.config.url, response.status);
    return response.data;
  },
  error => {
    // 添加更详细的错误日志
    if (error.response) {
      // 服务器返回了错误状态码
      console.error('API响应错误:', error.config.url, error.response.status, error.response.data);
    } else if (error.request) {
      // 请求发送成功，但没有收到响应
      console.error('API无响应:', error.config.url, '请求已发送但未收到响应');
    } else {
      // 请求设置时发生错误
      console.error('API请求错误:', error.config ? error.config.url : '未知URL', error.message);
    }
    return Promise.reject(error);
  }
);

// API函数
export default {
  // 获取API状态
  getStatus() {
    return api.get('/api/status');
  },
  
  // 发送聊天请求
  sendChat(userId, query) {
    return api.post('/api/chat/ask', {
      user_id: userId,
      query: query
    });
  },
  
  // 搜索知识库
  searchKnowledge(query, limit = 3) {
    return api.post('/api/knowledge/search', {
      query,
      limit
    });
  },
  
  // 获取知识库统计信息
  getKnowledgeStats() {
    return api.get('/api/knowledge/stats');
  }
}; 