/**
 * 知识库服务模块
 * 模拟金融知识库的查询和处理
 */
class KnowledgeService {
    constructor() {
        // 初始化知识库
        this.knowledgeBase = {
            // 贷款相关知识
            loan: [
                {
                    keywords: ['个人贷款', '贷款条件', '如何贷款'],
                    answer: '个人贷款一般需要您提供有效身份证件、收入证明、工作证明、银行流水等材料。具体要求可能因银行而异，我们建议您带上身份证和收入证明到银行咨询最新政策。'
                },
                {
                    keywords: ['贷款利率', '利息', '还款方式'],
                    answer: '个人贷款利率根据贷款类型、期限和个人信用评分而不同。目前我行个人住房贷款基准利率为X%，个人消费贷款基准利率为Y%。还款方式包括等额本息和等额本金两种主要方式。'
                },
                {
                    keywords: ['贷款期限', '最长可以贷多久'],
                    answer: '我行个人贷款期限根据贷款类型有所不同：住房贷款最长可达30年，个人消费贷款最长可达5年，经营贷款最长可达10年。具体期限会根据您的年龄、收入、信用状况等因素综合评定。'
                }
            ],
            
            // 保险相关知识
            insurance: [
                {
                    keywords: ['车险', '车辆保险', '汽车保险'],
                    answer: '车险主要包括交强险（强制保险）和商业险两大类。商业险包括车损险、第三者责任险、车上人员险、盗抢险、玻璃单独破碎险、自燃险、不计免赔险等多种险种。您可以根据自身需求选择合适的保险组合。'
                },
                {
                    keywords: ['寿险', '人寿保险', '意外险'],
                    answer: '寿险是以人的寿命为保险对象的保险，主要包括定期寿险、终身寿险和两全保险等。意外险则是针对意外事故导致的伤残或死亡提供保障。建议根据个人年龄、家庭责任和经济状况选择合适的保险产品。'
                },
                {
                    keywords: ['健康险', '医疗保险', '重疾险'],
                    answer: '健康险主要包括医疗险、重疾险、防癌险和长期护理险等。医疗险用于报销医疗费用，重疾险在确诊特定疾病后提供一次性赔付，防癌险专门针对癌症提供保障，长期护理险则为长期失能状态提供资金支持。'
                }
            ],
            
            // 理财相关知识
            investment: [
                {
                    keywords: ['理财产品', '如何理财', '投资'],
                    answer: '我行理财产品丰富多样，有稳健型、平衡型和进取型等不同风险等级的产品。建议您先了解自己的风险承受能力，再选择适合的理财产品。目前我行有多款新发售的理财产品，预期年化收益率在3.5%~5%之间。'
                },
                {
                    keywords: ['基金', '股票', '债券'],
                    answer: '基金是专业机构代客户进行投资的一种方式，分为货币基金、债券基金、混合基金和股票基金等。股票具有较高收益和风险，适合风险承受能力较强的投资者。债券则相对稳健，收益较为固定。'
                },
                {
                    keywords: ['存款', '利率', '定期'],
                    answer: '我行目前活期存款年利率为0.3%，定期存款根据期限不同，利率在1.5%~3.5%之间。大额存单利率相对更高，同时还有结构性存款等创新产品，可以根据您的流动性需求和收益预期选择合适的存款方式。'
                }
            ],
            
            // 信用卡相关知识
            creditCard: [
                {
                    keywords: ['信用卡', '办卡', '申请信用卡'],
                    answer: '申请信用卡需要您提供身份证、稳定收入证明等材料。您可以通过我行网点、手机银行或官网申请。目前我行有多种信用卡产品，包括普卡、金卡、白金卡等不同等级，针对不同消费场景有特色权益。'
                },
                {
                    keywords: ['信用卡逾期', '还款日', '最低还款'],
                    answer: '信用卡逾期会影响您的个人信用记录，产生滞纳金和利息。我行信用卡账单日后的25天为还款期，您至少需要在还款日前支付最低还款额（一般为账单金额的10%）。建议开通自动还款功能，避免忘记还款。'
                },
                {
                    keywords: ['信用卡积分', '优惠', '权益'],
                    answer: '我行信用卡消费可累积积分，积分可在积分商城兑换商品或抵扣消费。各类卡片还有不同权益，如机场贵宾厅、高尔夫服务、酒店优惠、餐饮折扣等。详细权益可查阅您的卡片说明或咨询客服。'
                }
            ],
            
            // 网银和手机银行
            onlineBanking: [
                {
                    keywords: ['网上银行', '手机银行', 'APP'],
                    answer: '我行网上银行和手机银行提供账户查询、转账汇款、投资理财、生活缴费等全方位服务。您可以在应用商店下载我行手机银行APP，或访问我行官网使用网上银行服务。首次使用需要进行身份验证和注册。'
                },
                {
                    keywords: ['转账', '汇款', '手续费'],
                    answer: '通过我行手机银行进行行内转账免手续费，跨行转账根据金额收取一定手续费（通常为转账金额的0.5%，最低2元，最高50元）。大额转账需要使用U盾或动态密码进行安全验证。'
                },
                {
                    keywords: ['安全', '密码', '支付'],
                    answer: '为保障账户安全，请勿泄露账号密码和验证码，定期更换密码，不要在不安全的网络环境下登录网银。我行采用多重加密技术和风险监控系统，保障您的资金安全。如发现异常交易，请立即联系客服。'
                }
            ]
        };
    }

    /**
     * 关键词匹配查询
     * @param {String} question 用户问题
     * @returns {String} 匹配到的答案
     */
    queryByKeywords(question) {
        // 简化版的关键词匹配
        // 实际系统中应该使用更复杂的算法，如TF-IDF、词向量等
        
        let bestAnswer = null;
        let maxMatches = 0;
        
        // 遍历所有知识领域
        for (const domain in this.knowledgeBase) {
            const knowledgeItems = this.knowledgeBase[domain];
            
            // 遍历该领域的所有知识点
            for (const item of knowledgeItems) {
                // 计算关键词匹配度
                const matches = this.calculateMatches(question, item.keywords);
                
                // 更新最佳匹配
                if (matches > maxMatches) {
                    maxMatches = matches;
                    bestAnswer = item.answer;
                }
            }
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
        
        // 简单的字符串匹配
        // 实际系统中应该使用更复杂的文本相似度算法
        for (const keyword of keywords) {
            if (question.includes(keyword)) {
                matches += 1;
            }
        }
        
        return matches;
    }
    
    /**
     * 语义分析和回答生成
     * 这是一个模拟的高级功能，实际项目中应该使用NLP服务如百度AI、讯飞等
     * @param {String} question 用户问题
     * @returns {Promise} 返回生成答案的Promise
     */
    async generateAnswer(question) {
        // 模拟异步处理过程
        return new Promise((resolve) => {
            setTimeout(() => {
                // 1. 模拟输入理解阶段（词法分析、句法分析、语义理解）
                console.log('进行语义分析...');
                
                // 2. 模拟知识检索
                const answer = this.queryByKeywords(question);
                
                // 3. 模拟信息整合与答案生成
                console.log('生成回答...');
                
                resolve(answer);
            }, 1000);
        });
    }
}

export default KnowledgeService; 