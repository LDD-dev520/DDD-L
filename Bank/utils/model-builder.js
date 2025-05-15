/**
 * 百度千帆ModelBuilder API工具类
 * 用于与百度千帆ModelBuilder API进行交互
 * 支持ERNIE-4.5-turbo-vl-32k模型
 */
class ModelBuilder {
    constructor(config = {}) {
        // 配置信息
        this.config = {
            apiKey: config.apiKey || '',
            secretKey: config.secretKey || '',
            model: config.model || 'ERNIE-4.5-turbo-vl-32k',
            endpoint: config.endpoint || 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie_4.5_turbo_vl_32k',
            temperature: config.temperature !== undefined ? config.temperature : 0.7,
            topP: config.topP !== undefined ? config.topP : 0.8,
            maxTokens: config.maxTokens || 2048,
            stream: config.stream !== undefined ? config.stream : false
        };
        
        // 存储access token
        this._accessToken = null;
        this._tokenExpireTime = 0;
    }
    
    /**
     * 设置API密钥和Secret Key
     * @param {String} apiKey 百度API Key
     * @param {String} secretKey 百度Secret Key
     */
    setCredentials(apiKey, secretKey) {
        this.config.apiKey = 'dnjYJMTtguWouyoJqoV50';
        this.config.secretKey = '9ceb4943b948eb2c77e781570cc1307116ba9e5f';
        // 清除旧的token
        this._accessToken = null;
        this._tokenExpireTime = 0;
    }
    
    /**
     * 设置使用的模型
     * @param {String} model 模型名称
     */
    setModel(model) {
        this.config.model = model;
        
        // 根据模型名称自动更新端点
        if (model === 'ERNIE-4.5-turbo-vl-32k') {
            this.config.endpoint = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie_4.5_turbo_vl_32k';
        } else if (model === 'ERNIE-4.0-turbo-vl-8k') {
            this.config.endpoint = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie_4.0_turbo_vl_8k';
        } else {
            // 默认使用通用API端点，需要在请求中指定模型
            this.config.endpoint = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions';
        }
    }
    
    /**
     * 获取百度API的access_token
     * @returns {Promise<String>} 返回access_token
     */
    async getAccessToken() {
        // 检查是否有有效的token
        const now = Date.now();
        if (this._accessToken && now < this._tokenExpireTime) {
            return this._accessToken;
        }
        
        try {
            if (!this.config.apiKey || !this.config.secretKey) {
                throw new Error('百度API Key或Secret Key未配置');
            }
            
            const url = `https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=${this.config.apiKey}&client_secret=${this.config.secretKey}`;
            
            // 使用uni.request代替fetch以支持小程序和App环境
            try {
                const tokenResult = await new Promise((resolve, reject) => {
                    uni.request({
                        url: url,
                        method: 'POST',
                        header: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        success: (res) => {
                            if (res.statusCode === 200) {
                                resolve(res.data);
                            } else {
                                reject(new Error(`获取百度access_token失败: ${res.statusCode}`));
                            }
                        },
                        fail: (err) => {
                            reject(new Error(`请求access_token网络错误: ${JSON.stringify(err)}`));
                        }
                    });
                });
                
                if (tokenResult && tokenResult.access_token) {
                    console.log('成功获取百度access_token');
                    this._accessToken = tokenResult.access_token;
                    // 设置token过期时间，提前5分钟过期以确保安全
                    this._tokenExpireTime = now + (tokenResult.expires_in * 1000) - (5 * 60 * 1000);
                    return this._accessToken;
                } else {
                    throw new Error('百度access_token返回格式错误: ' + JSON.stringify(tokenResult));
                }
            } catch (requestError) {
                console.error('请求access_token失败:', requestError);
                throw requestError;
            }
        } catch (error) {
            console.error('获取百度access_token失败:', error);
            throw error;
        }
    }
    
    /**
     * 发送聊天请求到ModelBuilder API
     * @param {Array} messages 消息数组，格式为[{role: 'user', content: '内容'}]
     * @param {Object} options 可选参数覆盖默认配置
     * @returns {Promise<Object>} 返回API响应对象
     */
    async chat(messages, options = {}) {
        try {
            // 验证消息格式
            if (!Array.isArray(messages) || messages.length === 0) {
                throw new Error('messages必须是非空数组');
            }
            
            // 获取access token
            const accessToken = await this.getAccessToken();
            
            // 构建请求URL
            const endpoint = `${this.config.endpoint}?access_token=${accessToken}`;
            
            // 合并选项
            const opts = {
                temperature: options.temperature !== undefined ? options.temperature : this.config.temperature,
                top_p: options.topP !== undefined ? options.topP : this.config.topP,
                max_tokens: options.maxTokens !== undefined ? options.maxTokens : this.config.maxTokens,
                stream: options.stream !== undefined ? options.stream : this.config.stream
            };
            
            // 构建请求体 - 根据不同端点调整参数
            const requestBody = {
                messages: messages,
                temperature: opts.temperature,
                top_p: opts.top_p,
                max_tokens: opts.max_tokens,
                stream: opts.stream
            };
            
            // 只有使用通用端点时才需要指定模型
            if (this.config.endpoint.includes('completions')) {
                requestBody.model = this.config.model;
            }
            
            console.log(`调用百度千帆ModelBuilder的${this.config.model}模型...`);
            console.log(`使用端点: ${this.config.endpoint}`);
            
            // 使用uni.request代替fetch以支持小程序和App环境
            try {
                const result = await new Promise((resolve, reject) => {
                    uni.request({
                        url: endpoint,
                        method: 'POST',
                        header: {
                            'Content-Type': 'application/json'
                        },
                        data: requestBody,
                        success: (res) => {
                            if (res.statusCode === 200) {
                                resolve(res.data);
                            } else {
                                reject(new Error(`百度千帆API请求失败: ${res.statusCode} ${JSON.stringify(res.data || {})}`));
                            }
                        },
                        fail: (err) => {
                            reject(new Error(`请求百度千帆API网络错误: ${JSON.stringify(err)}`));
                        }
                    });
                });
                
                // 处理响应数据
                if (result && result.result) {
                    return {
                        success: true,
                        content: result.result,
                        rawResponse: result
                    };
                } else if (result && result.response) {
                    return {
                        success: true,
                        content: result.response,
                        rawResponse: result
                    };
                } else if (result && result.output && result.output.text) {
                    return {
                        success: true,
                        content: result.output.text,
                        rawResponse: result
                    };
                } else {
                    throw new Error('百度千帆API返回数据格式错误: ' + JSON.stringify(result));
                }
            } catch (requestError) {
                console.error('请求百度千帆API失败:', requestError);
                throw requestError;
            }
        } catch (error) {
            console.error('调用百度千帆ModelBuilder失败:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    /**
     * 使用图片进行多模态对话
     * @param {Array} messages 消息数组，格式为[{role: 'user', content: [{type: 'text', text: '内容'}, {type: 'image', data: 'base64编码图片'}]}]
     * @param {Object} options 可选参数覆盖默认配置
     * @returns {Promise<Object>} 返回API响应对象
     */
    async chatWithImages(messages, options = {}) {
        try {
            // 验证消息格式
            if (!Array.isArray(messages) || messages.length === 0) {
                throw new Error('messages必须是非空数组');
            }
            
            // 获取access token
            const accessToken = await this.getAccessToken();
            
            // 构建请求URL
            const endpoint = `${this.config.endpoint}?access_token=${accessToken}`;
            
            // 合并选项
            const opts = {
                temperature: options.temperature !== undefined ? options.temperature : this.config.temperature,
                top_p: options.topP !== undefined ? options.topP : this.config.topP,
                max_tokens: options.maxTokens !== undefined ? options.maxTokens : this.config.maxTokens,
                stream: options.stream !== undefined ? options.stream : this.config.stream
            };
            
            // 构建请求体
            const requestBody = {
                messages: messages,
                model: this.config.model,
                temperature: opts.temperature,
                top_p: opts.top_p,
                max_tokens: opts.max_tokens,
                stream: opts.stream
            };
            
            console.log(`调用百度千帆ModelBuilder的${this.config.model}模型（多模态）...`);
            
            // 发送请求
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`百度千帆API请求失败: ${response.status} ${JSON.stringify(errorData)}`);
            }
            
            // 处理常规响应
            if (!opts.stream) {
                const data = await response.json();
                // 处理响应数据格式
                if (data && data.result) {
                    return {
                        success: true,
                        content: data.result,
                        rawResponse: data
                    };
                } else if (data && data.response) {
                    return {
                        success: true,
                        content: data.response,
                        rawResponse: data
                    };
                } else if (data && data.output && data.output.text) {
                    return {
                        success: true,
                        content: data.output.text,
                        rawResponse: data
                    };
                } else {
                    throw new Error('百度千帆API返回数据格式错误: ' + JSON.stringify(data));
                }
            } 
            // 处理流式响应
            else {
                // 返回响应对象，由调用方处理流式数据
                return {
                    success: true,
                    stream: response.body,
                    rawResponse: response
                };
            }
        } catch (error) {
            console.error('调用百度千帆ModelBuilder多模态对话失败:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
}

export default ModelBuilder; 