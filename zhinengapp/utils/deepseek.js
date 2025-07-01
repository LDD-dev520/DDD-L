/**
 * DeepSeek AI 工具类
 * 用于对接本地Ollama部署的DeepSeek模型
 */

import * as api from './api.js';

// Ollama API URL
const OLLAMA_API_URL = 'http://localhost:11434/api';
const DEFAULT_MODEL = 'deepseek-r1:7b';

// 简化配置
const CONFIG = {
  modelName: 'deepseek-r1:7b',
  temperature: 0.7,
  maxTokens: 2000,
  timeout: 30000,
  useKnowledge: true
};

/**
 * 通过API检索知识库
 * @param {string} query 查询文本
 * @returns {Promise<Array>} 知识库检索结果
 */
async function searchKnowledgeViaAPI(query) {
  try {
    const result = await api.searchKnowledge(query);
    if (result && result.success && result.results) {
      return result.results.map(item => ({
        id: item.id || '',
        topic: item.metadata?.source || '知识库',
        content: item.content,
        similarity: 0.5, // 默认相似度
        metadata: item.metadata || {}
      }));
    }
    return [];
  } catch (error) {
    console.error('知识库API检索失败:', error);
    return [];
  }
}

/**
 * 检查Ollama服务状态
 * @returns {Promise} 返回Promise，包含服务状态
 */
export function checkOllamaStatus() {
  console.log('[DeepSeek] 检查Ollama服务状态');
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${OLLAMA_API_URL}/tags`,
      method: 'GET',
      timeout: 5000,
      success: (res) => {
        if (res.statusCode === 200) {
          const hasDeepSeek = res.data?.models?.some(
            model => model.name.toLowerCase().includes('deepseek')
          );
          
          resolve({
            running: true,
            hasDeepSeek: hasDeepSeek,
            response: res.data
          });
        } else {
          resolve({
            running: false,
            error: `请求异常，状态码: ${res.statusCode}`
          });
        }
      },
      fail: (err) => {
        resolve({
          running: false,
          error: err.errMsg || '连接失败'
        });
      }
    });
  });
}

/**
 * 向Ollama发送问题
 * @param {string} question 用户问题
 * @param {Object} options 请求选项
 * @returns {Promise} 返回Promise，包含AI回答
 */
export function askOllama(question, options = {}) {
  // 显示加载提示
  uni.showLoading({
    title: 'AI思考中...'
  });

  // 准备请求参数
  let enrichedQuestion = question;
  let knowledgeContext = "";
  
  return new Promise(async (resolve, reject) => {
    try {
      if (CONFIG.useKnowledge) {
        // 通过API获取知识库搜索结果
        const knowledgeResults = await searchKnowledgeViaAPI(question);
        
        if (knowledgeResults && knowledgeResults.length > 0) {
          // 构建知识库上下文
          knowledgeContext = knowledgeResults.map(
            item => `[${item.topic}]: ${item.content}`
          ).join("\n\n");
          
          // 构建增强版问题
          if (knowledgeContext) {
            enrichedQuestion = `基于以下知识:
${knowledgeContext}

用户问题: ${question}

请基于上述知识回答问题。回答要简洁、准确，如果知识库中没有相关信息，请坦诚说明。`;
          }
        }
      }
      
      // 构建Ollama请求参数
      const ollamaRequestData = {
        model: options.model || CONFIG.modelName,
        prompt: enrichedQuestion,
        temperature: options.temperature || CONFIG.temperature,
        system: options.system || "你是一个专业的AI助手，提供准确、有帮助的回答。",
        options: {
          num_predict: options.maxTokens || CONFIG.maxTokens
        }
      };
      
      // 发送请求到本地Ollama服务
      uni.request({
        url: `${OLLAMA_API_URL}/generate`,
        method: 'POST',
        header: {
          'Content-Type': 'application/json'
        },
        data: ollamaRequestData,
        timeout: CONFIG.timeout,
        success: (res) => {
          uni.hideLoading();
          
          if (res.statusCode === 200 && res.data && res.data.response) {
            resolve({
              answer: res.data.response,
              success: true,
              model: CONFIG.modelName,
              usedKnowledge: knowledgeContext.length > 0
            });
          } else {
            console.error('Ollama响应异常:', res);
            reject({
              error: '本地AI响应异常',
              details: res.data,
              statusCode: res.statusCode,
              success: false
            });
          }
        },
        fail: (err) => {
          uni.hideLoading();
          console.error('Ollama请求失败:', err);
          reject({
            error: err.errMsg || '网络请求失败',
            success: false
          });
        }
      });
    } catch (error) {
      uni.hideLoading();
      console.error('处理请求时发生错误:', error);
      reject({
        error: error.message || '处理请求发生错误',
        success: false
      });
    }
  });
}

/**
 * 生成文本完成
 * @param {string} prompt 提示词
 * @param {Object} options 可选参数
 * @returns {Promise} 返回Promise，包含生成结果
 */
export function generateCompletion(prompt, options = {}) {
  console.log('[DeepSeek] 生成文本:', prompt.substring(0, 50) + '...');
  
  const model = options.model || DEFAULT_MODEL;
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${OLLAMA_API_URL}/generate`,
      method: 'POST',
      data: {
        model: model,
        prompt: prompt,
        stream: false,
        options: {
          temperature: options.temperature !== undefined ? options.temperature : CONFIG.temperature,
          top_k: options.top_k !== undefined ? options.top_k : 40,
          top_p: options.top_p !== undefined ? options.top_p : 0.9,
          num_predict: options.max_tokens !== undefined ? options.max_tokens : CONFIG.maxTokens
        }
      },
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data) {
          resolve({
            success: true,
            response: res.data.response,
            done: res.data.done
          });
        } else {
          reject({
            success: false,
            error: `请求异常，状态码: ${res.statusCode}`,
            response: res.data
          });
        }
      },
      fail: (err) => {
        console.error('[DeepSeek] 生成文本失败:', err);
        reject({
          success: false,
          error: err.errMsg || '网络请求失败'
        });
      }
    });
  });
}

/**
 * 设置配置选项
 * @param {Object} options 配置选项
 */
export function setConfig(options = {}) {
  Object.assign(CONFIG, options);
  console.log('[DeepSeek] 配置已更新:', CONFIG);
}

/**
 * 获取当前配置
 * @returns {Object} 当前配置
 */
export function getConfig() {
  return { ...CONFIG }; // 返回拷贝
} 