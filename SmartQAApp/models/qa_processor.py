#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
问答处理器模块
实现对用户输入的理解、知识检索、答案生成等核心功能
"""

import os
import json
import time
import re
import jieba
import jieba.analyse
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
from thefuzz import process
import logging
import random

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 尝试导入高级模型（可能不可用时会使用简单模型）
try:
    import torch
    from transformers import BertTokenizer, BertModel
    HAS_ADVANCED_MODELS = True
except ImportError:
    HAS_ADVANCED_MODELS = False


class QAProcessor:
    """
    智能问答处理器，负责理解用户输入，知识检索和回答生成
    增强版：支持银行业务领域的模糊查询和意图识别
    """
    
    def __init__(self, knowledge_base_path=None):
        """
        初始化问答处理器
        
        Args:
            knowledge_base_path: 知识库文件路径
        """
        self.knowledge_base = []
        self.vectorizer = None
        self.question_vectors = None
        self.categories = set()
        self.banking_keywords = self._load_banking_keywords()
        
        # 加载默认知识库
        if knowledge_base_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            knowledge_base_path = os.path.join(os.path.dirname(current_dir), "data", "knowledge_base.json")
        
        self.load_knowledge_base(knowledge_base_path)
        
        # 加载结巴词典和自定义词典
        self._initialize_jieba()
        
        # 训练TF-IDF向量化器
        self._train_vectorizer()
        
        logger.info("QA处理器初始化完成")
    
    def _load_banking_keywords(self):
        """加载银行业务相关的关键词和同义词"""
        banking_keywords = {
            "账户服务": ["账户", "开户", "开卡", "销户", "冻结", "解冻", "余额", "账号", "卡号", "存折"],
            "贷款服务": ["贷款", "房贷", "车贷", "消费贷", "信用贷", "抵押", "利率", "还款", "本金", "利息", "LPR", "贷记", "借记"],
            "信用卡": ["信用卡", "额度", "提额", "账单", "分期", "刷卡", "还款日", "免息期", "年费", "积分", "取现"],
            "理财投资": ["理财", "投资", "基金", "股票", "债券", "收益", "风险", "本金", "利息", "收益率", "风险等级"],
            "存款服务": ["存款", "定期", "活期", "大额存单", "智能存款", "存单", "利率", "利息", "存期", "提前支取"],
            "电子银行": ["网银", "手机银行", "APP", "电子银行", "在线", "线上", "数字", "移动", "指纹", "人脸识别"],
            "支付结算": ["转账", "汇款", "支付", "收款", "二维码", "扫码", "手续费", "到账", "快捷支付", "跨境"],
            "账户安全": ["密码", "挂失", "冻结", "解冻", "风控", "安全", "诈骗", "盗刷", "短信通知", "验证码"],
            "网点服务": ["网点", "柜台", "营业厅", "营业时间", "排队", "预约", "大堂", "工作日", "周末", "假日"],
            "征信服务": ["征信", "信用", "信用记录", "信用报告", "逾期", "黑名单", "白名单", "人行", "央行"]
        }
        return banking_keywords
        
    def _initialize_jieba(self):
        """初始化结巴分词，添加银行业务领域词典"""
        # 添加银行业务领域的词汇
        banking_terms = []
        for category, keywords in self.banking_keywords.items():
            banking_terms.extend(keywords)
            
        # 添加一些常见的银行业务专有名词
        specialized_terms = [
            "LPR", "ATM", "POS", "CRS", "ETC", "NFC", "OTP", "CVV", "AUM", "IPO",
            "理财产品", "结构性存款", "大额存单", "智能存款", "存款证明", 
            "房贷", "车贷", "消费贷", "经营贷", "按揭贷款", "抵押贷款", "信用贷款",
            "信用卡", "储蓄卡", "借记卡", "贷记卡", "预付卡", "联名卡", "白金卡", "钻石卡",
            "手机银行", "网上银行", "电话银行", "短信银行", "自助银行",
            "跨境汇款", "电子支付", "快捷支付", "二维码支付", "指纹支付", "人脸支付",
            "征信报告", "信用记录", "逾期记录", "失信记录", "征信查询",
            "风险等级", "收益率", "年化收益", "本金保障", "浮动收益"
        ]
        banking_terms.extend(specialized_terms)
        
        # 将这些词添加到结巴词典中
        for term in banking_terms:
            jieba.add_word(term)
            
        logger.info(f"已添加{len(banking_terms)}个银行业务领域词汇到分词词典")
    
    def load_knowledge_base(self, file_path):
        """
        加载知识库
        
        Args:
            file_path: 知识库文件路径
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
                
            # 提取所有类别
            self.categories = set(item["category"] for item in self.knowledge_base)
            logger.info(f"成功加载知识库，共{len(self.knowledge_base)}条记录，{len(self.categories)}个类别")
        except Exception as e:
            logger.error(f"加载知识库失败: {str(e)}")
            # 初始化一个空的知识库
            self.knowledge_base = []
    
    def _train_vectorizer(self):
        """训练TF-IDF向量化器"""
        if not self.knowledge_base:
            logger.warning("知识库为空，无法训练向量化器")
            return
            
        # 准备语料库
        corpus = []
        for item in self.knowledge_base:
            # 使用问题和关键词组合作为特征文本
            question_text = item["question"]
            keywords_text = " ".join(item["keywords"])
            combined_text = f"{question_text} {keywords_text}"
            corpus.append(combined_text)
        
        # 训练TF-IDF向量化器
        self.vectorizer = TfidfVectorizer(tokenizer=lambda x: jieba.lcut(x))
        self.question_vectors = self.vectorizer.fit_transform(corpus)
        
        logger.info("TF-IDF向量化器训练完成")
    
    def _extract_keywords(self, query):
        """
        从查询中提取关键词，增强版
        
        Args:
            query: 用户查询文本
            
        Returns:
            关键词列表
        """
        # 使用结巴分词提取关键词，考虑银行业务领域特点
        keywords = jieba.analyse.extract_tags(query, topK=8)
        
        # 添加完整的数字作为关键词（可能是金额、利率等）
        numbers = re.findall(r'\d+\.?\d*%?', query)
        keywords.extend(numbers)
        
        # 查找可能的银行业务专有名词
        words = jieba.lcut(query)
        for word in words:
            for category, category_keywords in self.banking_keywords.items():
                if word in category_keywords and word not in keywords:
                    keywords.append(word)
        
        # 添加词组匹配 - 检测常见的银行业务词组
        bank_phrases = [
            "信用卡", "储蓄卡", "借记卡", "贷记卡", "银行卡",
            "定期存款", "活期存款", "大额存单", "智能存款",
            "房贷", "车贷", "消费贷", "信用贷", "经营贷",
            "手机银行", "网上银行", "电话银行", "自助银行",
            "理财产品", "结构性存款", "风险等级", "收益率"
        ]
        
        for phrase in bank_phrases:
            if phrase in query and phrase not in keywords:
                keywords.append(phrase)
        
        # 处理同义词和近义词
        synonyms = {
            "查询": ["查看", "了解", "知道", "询问"],
            "办理": ["申请", "开通", "开户", "开卡"],
            "额度": ["限额", "上限", "额度"],
            "利率": ["利息", "利息率", "年化", "收益率"],
            "转账": ["汇款", "付款", "支付", "打钱"]
        }
        
        # 扩展同义词
        expanded_keywords = keywords.copy()
        for keyword in keywords:
            for base_word, synonym_list in synonyms.items():
                if keyword in synonym_list and base_word not in expanded_keywords:
                    expanded_keywords.append(base_word)
        
        logger.info(f"从查询中提取的关键词: {expanded_keywords}")
        return expanded_keywords
    
    def _identify_intent(self, query, keywords):
        """
        识别用户查询意图
        
        Args:
            query: 用户查询文本
            keywords: 提取的关键词列表
            
        Returns:
            意图类别和置信度
        """
        # 定义意图模式
        intent_patterns = {
            "查询": r"(如何|怎么|怎样|哪里|什么|多少|几点|查询|查看|了解|知道|告诉|说明)",
            "办理": r"(如何|怎么|怎样|去哪|在哪|办理|开通|申请|开户|开卡)",
            "问题": r"(出现|遇到|碰到|发生|问题|错误|失败|无法|不能)",
            "比较": r"(对比|比较|区别|差异|不同|优势|好处|哪个好)",
            "咨询": r"(请问|想问|咨询|了解|想知道)"
        }
        
        # 检查查询中的意图模式
        detected_intents = {}
        for intent, pattern in intent_patterns.items():
            if re.search(pattern, query):
                detected_intents[intent] = 0.8
        
        # 根据关键词进一步判断意图
        category_scores = {}
        for keyword in keywords:
            for category, category_keywords in self.banking_keywords.items():
                if keyword in category_keywords:
                    category_scores[category] = category_scores.get(category, 0) + 1
        
        # 如果有明确的类别，将其作为意图的一部分
        if category_scores:
            top_category = max(category_scores.items(), key=lambda x: x[1])[0]
            detected_intents[top_category] = 0.9
        
        # 如果没有检测到意图，默认为查询
        if not detected_intents:
            detected_intents["查询"] = 0.6
        
        # 返回最可能的意图和置信度
        top_intent = max(detected_intents.items(), key=lambda x: x[1])
        return top_intent[0], top_intent[1]
    
    def _find_best_match(self, query, keywords, intent):
        """
        查找最佳匹配的知识条目，使用增强的模糊匹配算法
        
        Args:
            query: 用户查询文本
            keywords: 提取的关键词列表
            intent: 识别的意图
            
        Returns:
            最佳匹配的知识条目和相似度分数
        """
        if not self.knowledge_base:
            logger.warning("知识库为空，无法查找匹配")
            return None, 0
        
        # 向量化查询
        query_vector = self.vectorizer.transform([query])
        
        # 计算余弦相似度
        cosine_similarities = cosine_similarity(query_vector, self.question_vectors).flatten()
        
        # 使用增强的模糊匹配计算相似度
        fuzzy_scores = []
        category_matches = []
        
        # 预处理：从查询中识别可能的类别
        query_categories = set()
        for category, keywords_list in self.banking_keywords.items():
            for keyword in keywords_list:
                if keyword in query:
                    query_categories.add(category)
                    break
        
        for item in self.knowledge_base:
            # 计算问题与查询的模糊匹配分数 (使用多种模糊匹配算法)
            token_set_ratio = fuzz.token_set_ratio(query, item["question"]) / 100.0
            token_sort_ratio = fuzz.token_sort_ratio(query, item["question"]) / 100.0
            partial_ratio = fuzz.partial_ratio(query, item["question"]) / 100.0
            
            # 综合不同的模糊匹配算法结果
            question_score = (token_set_ratio * 0.5 + token_sort_ratio * 0.3 + partial_ratio * 0.2)
            
            # 计算关键词匹配分数 (改进版)
            keyword_score = 0
            matched_keywords = 0
            
            for keyword in keywords:
                # 精确匹配
                if keyword in item["keywords"] or any(keyword in k for k in item["keywords"]):
                    keyword_score += 0.25
                    matched_keywords += 1
                    continue
                    
                # 模糊匹配
                best_match, score = process.extractOne(keyword, item["keywords"], scorer=fuzz.token_set_ratio)
                if score > 85:  # 提高匹配阈值
                    keyword_score += 0.2
                    matched_keywords += 0.8
                elif score > 70:
                    keyword_score += 0.1
                    matched_keywords += 0.5
            
            # 考虑匹配关键词的覆盖率
            if keywords:
                keyword_coverage = matched_keywords / len(keywords)
                keyword_score = 0.7 * keyword_score + 0.3 * keyword_coverage
            
            # 限制关键词分数上限为1.0
            keyword_score = min(keyword_score, 1.0)
            
            # 类别匹配加分
            category_score = 0
            if item["category"] in query_categories:
                category_score = 0.2
            
            # 综合分数 (调整权重)
            combined_score = 0.4 * question_score + 0.4 * keyword_score + 0.2 * category_score
            fuzzy_scores.append(combined_score)
            
            # 记录类别是否匹配
            category_matches.append(1 if item["category"] in query_categories else 0)
        
        # 综合考虑余弦相似度、模糊匹配分数和类别匹配
        final_scores = [0.6 * cosine_similarities[i] + 0.4 * fuzzy_scores[i] + 0.1 * category_matches[i] 
                       for i in range(len(self.knowledge_base))]
        
        # 找出最佳匹配
        best_match_index = np.argmax(final_scores)
        best_match_score = final_scores[best_match_index]
        
        # 如果最佳匹配分数过低，可能没有合适的回答
        if best_match_score < 0.35:  # 略微降低阈值以增加匹配概率
            logger.info(f"未找到高置信度匹配，最高分数: {best_match_score:.2f}")
            
            # 尝试查找相关类别的次优匹配
            if query_categories:
                category_items = [(i, item) for i, item in enumerate(self.knowledge_base) 
                                 if item["category"] in query_categories]
                if category_items:
                    category_scores = [final_scores[i] for i, _ in category_items]
                    best_category_index = np.argmax(category_scores)
                    best_category_score = category_scores[best_category_index]
                    
                    # 如果类别内最佳匹配分数达到阈值，使用它
                    if best_category_score >= 0.3:
                        best_match_index = category_items[best_category_index][0]
                        best_match_score = best_category_score
                        logger.info(f"使用类别匹配的次优结果，ID: {self.knowledge_base[best_match_index]['id']}, 分数: {best_match_score:.2f}")
                        return self.knowledge_base[best_match_index], best_match_score
            
            return None, best_match_score
        
        logger.info(f"找到最佳匹配，ID: {self.knowledge_base[best_match_index]['id']}, 分数: {best_match_score:.2f}")
        return self.knowledge_base[best_match_index], best_match_score
    
    def process_query(self, query):
        """
        处理用户查询，增强版
        
        Args:
            query: 用户查询文本
            
        Returns:
            回答文本
        """
        logger.info(f"处理用户查询: {query}")
        
        # 预处理查询文本
        query = self._preprocess_query(query)
        
        # 提取关键词
        keywords = self._extract_keywords(query)
        
        # 识别意图
        intent, intent_confidence = self._identify_intent(query, keywords)
        logger.info(f"识别到的意图: {intent}, 置信度: {intent_confidence:.2f}")
        
        # 查找最佳匹配
        best_match, match_score = self._find_best_match(query, keywords, intent)
        
        # 生成回答
        if best_match and match_score >= 0.35:  # 略微降低阈值以增加匹配概率
            answer = self._generate_answer(query, best_match, keywords, intent, match_score)
        else:
            # 尝试查找相似问题作为建议
            similar_questions = self._find_similar_questions(query, keywords)
            answer = self._generate_fallback_answer(query, keywords, intent, similar_questions)
        
        return answer
    
    def _preprocess_query(self, query):
        """
        预处理用户查询
        
        Args:
            query: 原始查询文本
            
        Returns:
            处理后的查询文本
        """
        # 去除多余空格
        query = re.sub(r'\s+', ' ', query).strip()
        
        # 替换常见的标点符号
        query = re.sub(r'[?？!！.。,，:：;；]', ' ', query)
        
        # 替换常见的同义表达
        replacements = {
            r'怎么样|怎样|如何': '如何',
            r'能不能|可不可以|是否可以': '可以',
            r'什么是|是什么': '什么是',
            r'哪些|有哪些|有什么': '哪些',
            r'多少钱|什么价格|价格是|费用是': '多少钱'
        }
        
        for pattern, replacement in replacements.items():
            query = re.sub(pattern, replacement, query)
        
        return query
    
    def _find_similar_questions(self, query, keywords):
        """
        查找与当前查询相似的问题，用于在无匹配时提供建议
        
        Args:
            query: 用户查询文本
            keywords: 提取的关键词
            
        Returns:
            相似问题列表 (最多3个)
        """
        if not self.knowledge_base:
            return []
        
        # 向量化查询
        query_vector = self.vectorizer.transform([query])
        
        # 计算余弦相似度
        similarities = cosine_similarity(query_vector, self.question_vectors).flatten()
        
        # 获取前3个最相似的问题
        top_indices = similarities.argsort()[-3:][::-1]
        similar_questions = []
        
        for idx in top_indices:
            if similarities[idx] > 0.2:  # 只返回相似度超过阈值的问题
                similar_questions.append(self.knowledge_base[idx]["question"])
        
        return similar_questions
    
    def _generate_answer(self, query, knowledge_item, keywords, intent, confidence):
        """
        根据知识条目生成回答
        
        Args:
            query: 用户查询文本
            knowledge_item: 匹配的知识条目
            keywords: 提取的关键词
            intent: 识别的意图
            confidence: 匹配置信度
            
        Returns:
            生成的回答文本
        """
        answer = knowledge_item["answer"]
        
        # 如果置信度较高，直接返回答案
        if confidence > 0.7:
            return answer
        
        # 如果置信度中等，添加一些提示语
        if 0.5 <= confidence <= 0.7:
            prefix_templates = [
                "根据您的问题，",
                "您可能想了解的是，",
                "对于这个问题，",
                "针对您的咨询，"
            ]
            prefix = random.choice(prefix_templates)
            return f"{prefix}{answer}"
        
        # 如果置信度较低但仍然可接受，添加更多提示语
        suffix_templates = [
            "如果这不是您想了解的内容，请尝试更详细地描述您的问题。",
            "希望这个回答对您有所帮助，如需更多信息，请告诉我。",
            "如果您有更具体的问题，请随时咨询。"
        ]
        suffix = random.choice(suffix_templates)
        return f"{answer}\n\n{suffix}"
    
    def _generate_fallback_answer(self, query, keywords, intent, similar_questions=None):
        """
        生成备选回答，当没有找到合适的知识条目时使用
        
        Args:
            query: 用户查询文本
            keywords: 提取的关键词
            intent: 识别的意图
            similar_questions: 相似问题列表
            
        Returns:
            生成的备选回答文本
        """
        # 根据意图和关键词生成不同的回答模板
        if intent == "查询":
            templates = [
                "很抱歉，我目前没有关于\"{}\"的详细信息。您可以尝试咨询银行客服或前往银行网点获取准确信息。",
                "对于\"{}\"的查询，我暂时没有找到匹配的信息。您可以换个方式提问，或直接联系银行客服热线。",
                "关于\"{}\"的信息，我的知识库暂时没有收录。建议您通过手机银行APP或官方网站查询最新信息。"
            ]
        elif intent == "办理":
            templates = [
                "关于如何办理\"{}\"，我目前没有具体的操作流程。建议您携带有效身份证件前往银行网点咨询。",
                "办理\"{}\"的具体要求可能因银行而异。建议您致电银行客服热线或访问官方网站了解详情。",
                "很抱歉，我无法提供关于\"{}\"的办理指南。您可以通过银行APP预约办理或前往网点咨询。"
            ]
        elif intent == "问题":
            templates = [
                "对于您遇到的\"{}\"问题，我建议您联系银行客服热线获取专业解答和帮助。",
                "很抱歉，我无法解决您关于\"{}\"的具体问题。请联系银行客服或前往网点寻求帮助。",
                "关于\"{}\"的问题可能需要专业人员处理。建议您拨打银行客服热线或在手机银行APP上提交反馈。"
            ]
        else:
            templates = [
                "很抱歉，我无法回答关于\"{}\"的问题。您可以尝试重新表述或咨询更具体的问题。",
                "对于\"{}\"，我目前没有相关信息。您可以联系银行客服获取更准确的答案。",
                "我的知识库中没有关于\"{}\"的信息。建议您通过官方渠道获取准确答案。"
            ]
        
        # 选择一个模板并填充关键词
        template = random.choice(templates)
        keyword_text = "、".join(keywords[:3]) if keywords else query[:10] + "..."
        answer = template.format(keyword_text)
        
        # 如果有相似问题，添加建议
        if similar_questions and len(similar_questions) > 0:
            answer += "\n\n您可能想问的是：\n"
            for i, question in enumerate(similar_questions):
                answer += f"{i+1}. {question}\n"
        
        return answer
    
    def add_to_knowledge_base(self, question, answer, keywords=None, category=None):
        """
        添加新的知识条目到知识库
        
        Args:
            question: 问题文本
            answer: 答案文本
            keywords: 关键词列表，如果为None则自动提取
            category: 类别，如果为None则尝试自动分类
            
        Returns:
            成功添加返回True，否则返回False
        """
        try:
            # 如果未提供关键词，自动提取
            if keywords is None:
                keywords = jieba.analyse.extract_tags(question, topK=5)
                
            # 如果未提供类别，尝试自动分类
            if category is None:
                # 计算与各类别的关联度
                category_scores = {}
                for cat, cat_keywords in self.banking_keywords.items():
                    score = sum(1 for kw in keywords if kw in cat_keywords or any(kw in ck for ck in cat_keywords))
                    category_scores[cat] = score
                
                # 选择得分最高的类别，如果都是0分则使用"其他"
                if max(category_scores.values(), default=0) > 0:
                    category = max(category_scores.items(), key=lambda x: x[1])[0]
                else:
                    category = "其他"
            
            # 创建新的知识条目
            new_id = max([item["id"] for item in self.knowledge_base], default=0) + 1
            new_item = {
                "id": new_id,
                "question": question,
                "answer": answer,
                "keywords": keywords,
                "category": category
            }
            
            # 添加到知识库
            self.knowledge_base.append(new_item)
            
            # 更新类别集合
            self.categories.add(category)
            
            # 重新训练向量化器
            self._train_vectorizer()
            
            logger.info(f"成功添加新知识条目，ID: {new_id}")
            return True
        except Exception as e:
            logger.error(f"添加知识条目失败: {str(e)}")
            return False
    
    def save_knowledge_base(self, file_path=None):
        """
        保存知识库到文件
        
        Args:
            file_path: 保存路径，如果为None则使用默认路径
            
        Returns:
            成功保存返回True，否则返回False
        """
        try:
            if file_path is None:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(os.path.dirname(current_dir), "data", "knowledge_base.json")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=4)
                
            logger.info(f"成功保存知识库到 {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存知识库失败: {str(e)}")
            return False

    def initialize(self):
        """初始化QA处理器资源"""
        logger.info("QA处理器资源初始化")
        
        # 确保知识库已加载
        if not self.knowledge_base:
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                knowledge_base_path = os.path.join(os.path.dirname(current_dir), "data", "knowledge_base.json")
                self.load_knowledge_base(knowledge_base_path)
            except Exception as e:
                logger.error(f"初始化时加载知识库失败: {str(e)}")
        
        # 确保向量化器已训练
        if self.knowledge_base and self.vectorizer is None:
            self._train_vectorizer()
            
        # 初始化结巴分词
        if not jieba.dt.initialized:
            self._initialize_jieba()
            
        logger.info("QA处理器初始化完成")

    def cleanup(self):
        """清理资源"""
        # 保存知识库
        self.save_knowledge_base()
        
        # 清理模型（如果存在）
        if hasattr(self, 'model') and self.model:
            del self.model
            self.model = None
        
        if hasattr(self, 'tokenizer') and self.tokenizer:
            del self.tokenizer
            self.tokenizer = None 