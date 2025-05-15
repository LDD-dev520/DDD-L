/**
 * 知识库服务模块
 * 模拟金融知识库的查询和处理
 */
// 导入ModelBuilder工具类
import ModelBuilder from './model-builder.js';

class KnowledgeService {
    constructor() {
        // 初始化知识库
        this.knowledgeBase = {
            // 贷款相关知识
            loan: [
                {
                    keywords: ['个人贷款', '贷款条件', '如何贷款', '办理贷款', '申请贷款'],
                    answer: '个人贷款一般需要您提供有效身份证件、收入证明、工作证明、银行流水等材料。具体要求可能因银行而异，我们建议您带上身份证和收入证明到银行咨询最新政策。'
                },
                {
                    keywords: ['贷款利率', '利息', '还款方式', '月供', '利率多少'],
                    answer: '个人贷款利率根据贷款类型、期限和个人信用评分而不同。目前我行个人住房贷款基准利率为X%，个人消费贷款基准利率为Y%。还款方式包括等额本息和等额本金两种主要方式。'
                },
                {
                    keywords: ['贷款期限', '最长可以贷多久', '贷款年限', '贷款时间'],
                    answer: '我行个人贷款期限根据贷款类型有所不同：住房贷款最长可达30年，个人消费贷款最长可达5年，经营贷款最长可达10年。具体期限会根据您的年龄、收入、信用状况等因素综合评定。'
                },
                {
                    keywords: ['提前还款', '提前结清', '还款违约金'],
                    answer: '我行支持提前部分还款和全部结清。提前还款需要提前向银行提出申请，并可能需要支付一定的违约金。目前我行住房贷款提前还款违约金为剩余本金的0-2%，具体比例根据贷款合同约定和已还款期限而定。'
                }
            ],
            
            // 保险相关知识
            insurance: [
                {
                    keywords: ['车险', '车辆保险', '汽车保险', '机动车保险'],
                    answer: '车险主要包括交强险（强制保险）和商业险两大类。商业险包括车损险、第三者责任险、车上人员险、盗抢险、玻璃单独破碎险、自燃险、不计免赔险等多种险种。您可以根据自身需求选择合适的保险组合。'
                },
                {
                    keywords: ['寿险', '人寿保险', '意外险', '人身保险'],
                    answer: '寿险是以人的寿命为保险对象的保险，主要包括定期寿险、终身寿险和两全保险等。意外险则是针对意外事故导致的伤残或死亡提供保障。建议根据个人年龄、家庭责任和经济状况选择合适的保险产品。'
                },
                {
                    keywords: ['健康险', '医疗保险', '重疾险', '癌症保险'],
                    answer: '健康险主要包括医疗险、重疾险、防癌险和长期护理险等。医疗险用于报销医疗费用，重疾险在确诊特定疾病后提供一次性赔付，防癌险专门针对癌症提供保障，长期护理险则为长期失能状态提供资金支持。'
                },
                {
                    keywords: ['保险理赔', '如何理赔', '保险索赔', '理赔流程'],
                    answer: '保险理赔一般流程包括：1.报案：出险后及时向保险公司报案；2.提交理赔材料：准备相关证明、单据等；3.保险公司调查核实；4.理赔结果确定并赔付。不同险种理赔所需材料和流程可能有差异，建议及时联系您的保险顾问或保险公司客服。'
                }
            ],
            
            // 理财相关知识
            investment: [
                {
                    keywords: ['理财产品', '如何理财', '投资', '理财建议'],
                    answer: '我行理财产品丰富多样，有稳健型、平衡型和进取型等不同风险等级的产品。建议您先了解自己的风险承受能力，再选择适合的理财产品。目前我行有多款新发售的理财产品，预期年化收益率在3.5%~5%之间。'
                },
                {
                    keywords: ['基金', '股票', '债券', '投资组合'],
                    answer: '基金是专业机构代客户进行投资的一种方式，分为货币基金、债券基金、混合基金和股票基金等。股票具有较高收益和风险，适合风险承受能力较强的投资者。债券则相对稳健，收益较为固定。'
                },
                {
                    keywords: ['存款', '利率', '定期', '活期', '存款利息'],
                    answer: '我行目前活期存款年利率为0.3%，定期存款根据期限不同，利率在1.5%~3.5%之间。大额存单利率相对更高，同时还有结构性存款等创新产品，可以根据您的流动性需求和收益预期选择合适的存款方式。'
                },
                {
                    keywords: ['投资风险', '风险提示', '风险管理', '风险等级'],
                    answer: '投资理财存在一定风险，主要包括市场风险、信用风险、流动性风险等。我行对理财产品设有R1（谨慎型）至R5（激进型）五级风险评级。建议您进行风险承受能力评估，选择与自身风险承受能力相匹配的产品，并注意分散投资，避免将资金过度集中。'
                }
            ],
            
            // 信用卡相关知识
            creditCard: [
                {
                    keywords: ['信用卡', '办卡', '申请信用卡', '信用卡额度'],
                    answer: '申请信用卡需要您提供身份证、稳定收入证明等材料。您可以通过我行网点、手机银行或官网申请。目前我行有多种信用卡产品，包括普卡、金卡、白金卡等不同等级，针对不同消费场景有特色权益。'
                },
                {
                    keywords: ['信用卡逾期', '还款日', '最低还款', '信用卡还款'],
                    answer: '信用卡逾期会影响您的个人信用记录，产生滞纳金和利息。我行信用卡账单日后的25天为还款期，您至少需要在还款日前支付最低还款额（一般为账单金额的10%）。建议开通自动还款功能，避免忘记还款。'
                },
                {
                    keywords: ['信用卡积分', '优惠', '权益', '积分兑换'],
                    answer: '我行信用卡消费可累积积分，积分可在积分商城兑换商品或抵扣消费。各类卡片还有不同权益，如机场贵宾厅、高尔夫服务、酒店优惠、餐饮折扣等。详细权益可查阅您的卡片说明或咨询客服。'
                },
                {
                    keywords: ['信用卡挂失', '信用卡丢失', '卡片遗失', '冻结卡片'],
                    answer: '信用卡遗失后，请立即拨打我行客服热线进行挂失。挂失成功后，卡片将被冻结，可有效防范资金损失。挂失后您可申请补办新卡，一般7-10个工作日可收到新卡。请注意保护个人信息安全，不要向陌生人透露卡号、密码等敏感信息。'
                }
            ],
            
            // 网银和手机银行
            onlineBanking: [
                {
                    keywords: ['网上银行', '手机银行', 'APP', '电子银行'],
                    answer: '我行网上银行和手机银行提供账户查询、转账汇款、投资理财、生活缴费等全方位服务。您可以在应用商店下载我行手机银行APP，或访问我行官网使用网上银行服务。首次使用需要进行身份验证和注册。'
                },
                {
                    keywords: ['转账', '汇款', '手续费', '转账限额'],
                    answer: '通过我行手机银行进行行内转账免手续费，跨行转账根据金额收取一定手续费（通常为转账金额的0.5%，最低2元，最高50元）。大额转账需要使用U盾或动态密码进行安全验证。'
                },
                {
                    keywords: ['安全', '密码', '支付', '安全保障'],
                    answer: '为保障账户安全，请勿泄露账号密码和验证码，定期更换密码，不要在不安全的网络环境下登录网银。我行采用多重加密技术和风险监控系统，保障您的资金安全。如发现异常交易，请立即联系客服。'
                },
                {
                    keywords: ['绑定手机号', '修改手机号', '更换手机', '绑定银行卡'],
                    answer: '更换绑定手机号需携带您的有效身份证件和银行卡到我行网点办理。为保障账户安全，我行不支持通过电话或网上渠道直接更换预留手机号。如您的手机丢失，请及时挂失并联系我行客服临时冻结您的网银和手机银行账户。'
                }
            ],
            
            // 外汇相关知识
            foreignExchange: [
                {
                    keywords: ['汇率', '外汇兑换', '换汇', '美元兑人民币'],
                    answer: '我行提供多种外币兑换服务，包括美元、欧元、日元等主要货币。当前美元兑人民币汇率为6.9左右，欧元兑人民币汇率为7.5左右。您可以通过我行网点或手机银行进行外币兑换。汇率会根据国际外汇市场实时波动，请以办理时的实际汇率为准。'
                },
                {
                    keywords: ['外币存款', '外汇储蓄', '外币理财', '外币定期'],
                    answer: '我行提供多种外币存款服务，包括美元、欧元、日元等主要货币的活期和定期存款。外币定期存款期限灵活，从1个月至5年不等。目前美元定期存款年利率在0.5%~2.5%之间，具体视存款期限而定。办理外币存款业务需携带有效身份证件。'
                },
                {
                    keywords: ['结汇', '购汇', '外汇管制', '换汇限额'],
                    answer: '根据国家外汇管理局规定，个人年度购汇额度为5万美元等值外币。办理结汇或购汇业务时，需提供有效身份证件并填写相关申请表。超过额度的外汇业务可能需要提供特定用途证明材料。目前通过我行手机银行也可以便捷地办理小额结汇购汇业务。'
                }
            ]
        };
        
        // 初始化上下文存储
        this.conversationContext = {
            lastQuestion: null,
            lastAnswer: null,
            relevantDomain: null,
            // 添加历史对话记录数组，用于提供给外部AI更多上下文
            history: []
        };
        
        // 外部AI服务配置
        this.aiServiceConfig = {
            // 使用哪种外部AI服务: 仅使用'baidu'
            provider: 'baidu',
            // API密钥 - 实际项目中应从安全存储或环境变量获取
            apiKey: 'dnjYJMTtguWouyoJqoV50/9ceb4943b948eb2c77e781570cc1307116ba9e5f', // 这里应填入实际的API密钥和Secret Key，格式为"API Key|Secret Key"
            // API端点
            endpoints: {
                baidu: 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie_4.5_turbo_vl_32k'
            },
            // 模型配置
            models: {
                baidu: 'ERNIE-4.5-turbo-vl-32k' // 更新为ERNIE-4.5-turbo-vl-32k模型
            },
            // 请求头配置函数
            getHeaders() {
                return {
                    'Content-Type': 'application/json'
                };
            },
            // 获取当前配置的API端点
            getEndpoint() {
                return this.endpoints.baidu;
            },
            // 获取当前配置的模型名称
            getModel() {
                return this.models.baidu;
            }
        };
        
        // 初始化ModelBuilder实例
        const [apiKey, secretKey] = this.aiServiceConfig.apiKey.split('|');
        this.modelBuilder = new ModelBuilder({
            apiKey: apiKey, 
            secretKey: secretKey,
            model: this.aiServiceConfig.models.baidu,
            endpoint: this.aiServiceConfig.endpoints.baidu
        });
        
        console.log('初始化ModelBuilder实例，使用模型：' + this.aiServiceConfig.models.baidu);
        console.log('使用端点：' + this.aiServiceConfig.endpoints.baidu);
    }

    /**
     * 关键词匹配查询
     * @param {String} question 用户问题
     * @returns {String} 匹配到的答案
     */
    queryByKeywords(question) {
        // 如果有上下文参考，增加上下文相关领域的权重
        const hasContext = this.conversationContext.relevantDomain !== null;
        
        let bestAnswer = null;
        let maxMatches = 0;
        let matchedDomain = null;
        
        // 遍历所有知识领域
        for (const domain in this.knowledgeBase) {
            const knowledgeItems = this.knowledgeBase[domain];
            
            // 上下文权重加成
            const contextBonus = (hasContext && domain === this.conversationContext.relevantDomain) ? 0.5 : 0;
            
            // 遍历该领域的所有知识点
            for (const item of knowledgeItems) {
                // 计算关键词匹配度
                const matches = this.calculateMatches(question, item.keywords) + contextBonus;
                
                // 更新最佳匹配
                if (matches > maxMatches) {
                    maxMatches = matches;
                    bestAnswer = item.answer;
                    matchedDomain = domain;
                }
            }
        }
        
        // 更新对话上下文
        if (bestAnswer) {
            this.conversationContext = {
                lastQuestion: question,
                lastAnswer: bestAnswer,
                relevantDomain: matchedDomain,
                // 确保保留history数组
                history: this.conversationContext.history || []
            };
        }
        
        // 如果没找到匹配的答案，返回默认回复
        if (!bestAnswer) {
            return "您好，很抱歉我没能完全理解您的问题。请您尝试更具体地描述您的需求，或者换一种方式提问，我会尽力为您提供准确的答案。";
        }
        
        return bestAnswer;
    }
    
    /**
     * 计算问题与关键词的匹配度
     * @param {String} question 用户问题
     * @param {Array} keywords 关键词数组
     * @returns {Number} 匹配度分数
     */
    calculateMatches(question, keywords) {
        let matches = 0;
        
        // 1. 简单分词（实际应使用专业分词库如jieba）
        const words = question.split(/[,，。？！；：\s]/);
        
        // 2. 为每个关键词计算相似度
        for (const keyword of keywords) {
            // 精确匹配得高分
            if (question.includes(keyword)) {
                matches += 2;
                continue;
            }
            
            // 部分词语匹配得低分
            for (const word of words) {
                if (word.length > 1) { // 忽略单字匹配，减少噪音
                    if (keyword.includes(word) || word.includes(keyword)) {
                        matches += 0.5;
                        break;
                    }
                }
            }
        }
        
        return matches;
    }
    
    /**
     * 语义分析和回答生成
     * 实现本地知识库查询和外部AI服务调用的集成
     * @param {String} question 用户问题
     * @returns {Promise} 返回生成答案的Promise
     */
    async generateAnswer(question) {
        // 首先尝试本地知识库匹配
        const localAnswer = this.queryByKeywords(question);
        
        // 保存到历史记录
        this.conversationContext.history.push({
            role: 'user',
            content: question
        });
        
        // 匹配度阈值，低于此值表示匹配度不足
        const confidenceThreshold = 0.8;
        const hasLowConfidence = localAnswer.startsWith("您好，很抱歉我没能完全理解");
        
        // 如果本地匹配结果是默认回复或置信度低，尝试调用外部AI服务
        if (hasLowConfidence) {
            try {
                console.log('本地知识库无匹配或匹配度低，调用外部AI服务...');
                
                // 调用外部AI服务获取回答
                const aiAnswer = await this.callExternalAI(question);
                
                // 保存AI回答到历史
                this.conversationContext.history.push({
                    role: 'assistant',
                    content: aiAnswer
                });
                
                // 限制历史记录长度，避免过长
                if (this.conversationContext.history.length > 10) {
                    this.conversationContext.history = this.conversationContext.history.slice(-10);
                }
                
                return aiAnswer;
            } catch (error) {
                console.error('外部AI服务调用失败:', error);
                
                // 保存本地回答到历史
                this.conversationContext.history.push({
                    role: 'assistant',
                    content: localAnswer
                });
                
                // 失败时返回本地匹配结果
                return localAnswer;
            }
        } else {
            // 本地匹配结果良好，直接返回
            
            // 保存到历史
            this.conversationContext.history.push({
                role: 'assistant',
                content: localAnswer
            });
            
            // 限制历史记录长度
            if (this.conversationContext.history.length > 10) {
                this.conversationContext.history = this.conversationContext.history.slice(-10);
            }
            
            return localAnswer;
        }
    }
    
    /**
     * 调用外部AI服务
     * @param {String} question 用户问题
     * @returns {Promise<String>} 返回AI生成的回答
     */
    async callExternalAI(question) {
        try {
            // 构建系统提示，提供背景信息和指导
            const systemPrompt = `你是一家银行的智能客服助手，你的任务是回答用户关于银行业务的问题。
请提供准确、专业、简洁的回答，使用礼貌友好的语气。
回答应该集中在银行业务上，如：个人贷款、信用卡、理财产品、保险服务、网银、手机银行等。
不要回答与银行业务无关的问题，对于你不确定的信息，可以建议用户联系客服或前往银行网点咨询。
回答请使用中文，避免过长，控制在300字以内。`;

            // 构建用户指令，引导AI生成特定格式的回答
            const userInstruction = `请回答以下关于银行业务的问题。
如果你不知道答案，请诚实地说你不确定，并建议用户咨询专业的银行工作人员。
我的问题是: ${question}`;

            // 构建消息数组
            const messages = [
                { role: 'system', content: systemPrompt }
            ];
            
            // 添加历史对话以提供上下文（最多3轮）
            const recentHistory = this.conversationContext.history.slice(-6);
            if (recentHistory.length > 0) {
                messages.push(...recentHistory);
            }
            
            // 添加当前问题指令
            messages.push({ role: 'user', content: userInstruction });
            
            console.log(`调用百度千帆ModelBuilder的ERNIE-4.5-turbo-vl-32k模型...`);
            
            // 使用ModelBuilder调用千帆API
            const result = await this.modelBuilder.chat(messages, {
                temperature: 0.7,
                topP: 0.8
            });
            
            if (result.success) {
                return result.content;
            } else {
                throw new Error(`调用失败: ${result.error}`);
            }
        } catch (error) {
            console.error('调用百度千帆ModelBuilder失败:', error);
            throw error;
        }
    }
    
    /**
     * 获取百度API的access_token
     * 百度文心API必需
     * @returns {Promise<String>} 返回access_token
     */
    async getBaiduAccessToken() {
        try {
            // 使用ModelBuilder获取access_token
            return await this.modelBuilder.getAccessToken();
        } catch (error) {
            console.error('获取百度access_token失败:', error);
            throw error;
        }
    }
    
    /**
     * 猜测用户意图
     * 简单的意图分析函数
     * @param {String} question 用户问题
     * @returns {String} 猜测的意图描述
     */
    guessIntent(question) {
        if (question.includes('贷款') || question.includes('借钱')) {
            return '贷款业务';
        } else if (question.includes('保险') || question.includes('理赔')) {
            return '保险服务';
        } else if (question.includes('理财') || question.includes('投资')) {
            return '理财产品';
        } else if (question.includes('信用卡') || question.includes('银行卡')) {
            return '卡片业务';
        } else if (question.includes('转账') || question.includes('汇款')) {
            return '转账汇款';
        } else if (question.includes('外汇') || question.includes('汇率')) {
            return '外汇业务';
        } else if (question.includes('存款') || question.includes('利率')) {
            return '存款业务';
        } else if (question.includes('手机银行') || question.includes('网银')) {
            return '电子银行服务';
        } else {
            return '银行金融服务';
        }
    }
}

export default KnowledgeService; 