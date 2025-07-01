/**
 * 自然语言处理工具类
 * 包含文本分析和处理功能
 */

/**
 * 分词处理
 * 将句子分解为词语
 * @param {string} text 输入文本
 * @returns {Array} 分词结果数组
 */
export function tokenize(text) {
  // 处理空值
  if (!text) {
    return [];
  }
  
  // 确保text是字符串
  text = String(text);
  
  // 这里是简化的分词处理，实际应用中应该使用专业的NLP库
  // 例如jieba分词等
  
  // 简单的按空格和标点符号分词
  return text
    .replace(/[,.!?;:，。！？；：]/g, ' ')
    .split(' ')
    .filter(word => word.trim().length > 0);
}

/**
 * 关键词提取
 * 从文本中提取关键词
 * @param {string} text 输入文本
 * @param {number} limit 关键词数量限制
 * @returns {Array} 关键词数组
 */
export function extractKeywords(text, limit = 5) {
  // 处理空值
  if (!text) {
    return [];
  }
  
  // 确保text是字符串
  text = String(text);
  
  // 这里是简化的关键词提取，实际应用中应该使用专业的NLP库
  // 例如TF-IDF算法等
  
  // 简单的按词频提取
  const words = tokenize(text);
  const wordCount = {};
  
  // 统计词频
  words.forEach(word => {
    if (word.length > 1) { // 忽略单字词
      wordCount[word] = (wordCount[word] || 0) + 1;
    }
  });
  
  // 按词频排序
  const sortedWords = Object.keys(wordCount).sort((a, b) => wordCount[b] - wordCount[a]);
  
  // 返回指定数量的关键词
  return sortedWords.slice(0, limit);
}

/**
 * 意图识别
 * 识别用户输入的意图
 * @param {string} text 输入文本
 * @returns {Object} 意图对象，包含意图类型和置信度
 */
export function recognizeIntent(text) {
  // 这里是简化的意图识别，实际应用中应该使用专业的NLP库
  // 例如基于机器学习的意图分类器
  
  // 简单的规则匹配
  const lowerText = text.toLowerCase();
  
  // 定义一些简单的意图模式
  const intentPatterns = [
    { type: 'greeting', patterns: ['你好', '您好', '早上好', '下午好', '晚上好', 'hello', 'hi'], confidence: 0.9 },
    { type: 'farewell', patterns: ['再见', '拜拜', '回头见', 'bye', 'goodbye'], confidence: 0.9 },
    { type: 'thanks', patterns: ['谢谢', '感谢', '多谢', 'thanks', 'thank you'], confidence: 0.9 },
    { type: 'help', patterns: ['帮助', '怎么用', '使用说明', 'help', 'how to'], confidence: 0.8 },
    { type: 'query', patterns: ['什么是', '如何', '为什么', '怎么', '哪些', 'what is', 'how to', 'why'], confidence: 0.7 }
  ];
  
  // 检查是否匹配任何意图模式
  for (const intent of intentPatterns) {
    for (const pattern of intent.patterns) {
      if (lowerText.includes(pattern)) {
        return {
          type: intent.type,
          confidence: intent.confidence
        };
      }
    }
  }
  
  // 默认为一般查询意图
  return {
    type: 'general_query',
    confidence: 0.5
  };
}

/**
 * 情感分析
 * 分析文本的情感倾向
 * @param {string} text 输入文本
 * @returns {Object} 情感对象，包含情感类型和置信度
 */
export function analyzeSentiment(text) {
  // 这里是简化的情感分析，实际应用中应该使用专业的NLP库
  // 例如基于机器学习的情感分析模型
  
  // 简单的规则匹配
  const lowerText = text.toLowerCase();
  
  // 定义一些简单的情感词汇
  const positiveWords = ['好', '棒', '赞', '喜欢', '感谢', '开心', '满意', '优秀', 'good', 'great', 'excellent', 'happy', 'like', 'love'];
  const negativeWords = ['差', '糟', '烂', '不好', '讨厌', '失望', '不满', '生气', 'bad', 'poor', 'terrible', 'hate', 'dislike', 'angry'];
  
  // 计算情感得分
  let score = 0;
  
  // 检查正面词汇
  positiveWords.forEach(word => {
    if (lowerText.includes(word)) {
      score += 1;
    }
  });
  
  // 检查负面词汇
  negativeWords.forEach(word => {
    if (lowerText.includes(word)) {
      score -= 1;
    }
  });
  
  // 确定情感类型
  let sentimentType = 'neutral';
  let confidence = 0.5;
  
  if (score > 0) {
    sentimentType = 'positive';
    confidence = Math.min(0.5 + score * 0.1, 0.9);
  } else if (score < 0) {
    sentimentType = 'negative';
    confidence = Math.min(0.5 + Math.abs(score) * 0.1, 0.9);
  }
  
  return {
    type: sentimentType,
    confidence: confidence
  };
}

/**
 * 文本摘要
 * 生成文本的摘要
 * @param {string} text 输入文本
 * @param {number} maxLength 最大长度
 * @returns {string} 摘要文本
 */
export function summarizeText(text, maxLength = 100) {
  // 这里是简化的文本摘要，实际应用中应该使用专业的NLP库
  // 例如基于抽取式或生成式的摘要算法
  
  // 简单的截取前N个字符
  if (text.length <= maxLength) {
    return text;
  }
  
  // 尝试在句子边界截断
  const sentences = text.split(/[。！？.!?]/);
  let summary = '';
  
  for (const sentence of sentences) {
    if ((summary + sentence).length <= maxLength - 3) { // 为"..."留出空间
      summary += sentence;
    } else {
      break;
    }
  }
  
  return summary + '...';
}

/**
 * 实体识别
 * 识别文本中的命名实体
 * @param {string} text 输入文本
 * @returns {Array} 实体数组
 */
export function recognizeEntities(text) {
  // 这里是简化的实体识别，实际应用中应该使用专业的NLP库
  // 例如基于条件随机场(CRF)或深度学习的命名实体识别
  
  // 简单的规则匹配
  const entities = [];
  
  // 识别日期
  const dateRegex = /(\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}月\d{1,2}日|\d{4}-\d{1,2}-\d{1,2}|\d{1,2}-\d{1,2})/g;
  let match;
  
  while ((match = dateRegex.exec(text)) !== null) {
    entities.push({
      type: 'date',
      value: match[0],
      position: match.index
    });
  }
  
  // 识别数字
  const numberRegex = /\d+(\.\d+)?/g;
  
  while ((match = numberRegex.exec(text)) !== null) {
    // 避免与日期重复
    const isPartOfDate = entities.some(entity => 
      entity.type === 'date' && 
      match.index >= entity.position && 
      match.index < entity.position + entity.value.length
    );
    
    if (!isPartOfDate) {
      entities.push({
        type: 'number',
        value: match[0],
        position: match.index
      });
    }
  }
  
  // 返回按位置排序的实体
  return entities.sort((a, b) => a.position - b.position);
} 