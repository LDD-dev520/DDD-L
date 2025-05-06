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
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 尝试导入高级模型（可能不可用时会使用简单模型）
try:
    import torch
    from transformers import BertTokenizer, BertModel
    HAS_ADVANCED_MODELS = True
except ImportError:
    HAS_ADVANCED_MODELS = False


class QAProcessor:
    """问答处理器类"""
    
    def __init__(self):
        """初始化"""
        self.knowledge_base = []
        self.initialized = False
        self.vectorizer = None
        self.tokenizer = None
        self.model = None
    
    def initialize(self):
        """初始化资源"""
        # 声明使用全局变量
        global HAS_ADVANCED_MODELS
        
        # 加载知识库
        self._load_knowledge_base()
        
        # 初始化分词器
        jieba.initialize()
        
        # 初始化向量化器
        self.vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
        
        # 如果有高级模型，初始化Bert模型
        if HAS_ADVANCED_MODELS:
            try:
                # 使用中文BERT模型
                model_name = "bert-base-chinese"
                self.tokenizer = BertTokenizer.from_pretrained(model_name)
                self.model = BertModel.from_pretrained(model_name)
                
                # 设置为评估模式
                self.model.eval()
            except Exception as e:
                print(f"加载BERT模型失败: {e}")
                HAS_ADVANCED_MODELS = False
        
        self.initialized = True
    
    def _load_knowledge_base(self):
        """加载知识库"""
        # 知识库文件路径
        kb_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'knowledge_base.json')
        
        # 检查文件是否存在
        if os.path.exists(kb_file):
            try:
                with open(kb_file, 'r', encoding='utf-8') as f:
                    self.knowledge_base = json.load(f)
            except Exception as e:
                print(f"加载知识库失败: {e}")
                self._create_sample_knowledge_base()
        else:
            # 如果文件不存在，创建示例知识库
            self._create_sample_knowledge_base()
            
            # 保存示例知识库
            self._save_knowledge_base()
    
    def _create_sample_knowledge_base(self):
        """创建示例知识库"""
        self.knowledge_base = [
            {
                "id": 1,
                "question": "什么是人工智能?",
                "answer": "人工智能是计算机科学的一个分支，致力于创造能够模拟人类智能的机器。它包括机器学习、深度学习、自然语言处理等多个领域。",
                "keywords": ["人工智能", "AI", "机器学习", "深度学习", "自然语言处理"],
                "category": "科技"
            },
            {
                "id": 2,
                "question": "什么是机器学习?",
                "answer": "机器学习是人工智能的一个子领域，它使用算法使计算机系统能够从数据中学习和改进，而无需明确编程。常见的机器学习算法包括决策树、神经网络、支持向量机等。",
                "keywords": ["机器学习", "算法", "数据", "决策树", "神经网络"],
                "category": "科技"
            },
            {
                "id": 3,
                "question": "什么是深度学习?",
                "answer": "深度学习是机器学习的一个子领域，使用多层神经网络（称为深度神经网络）对数据进行建模。它在图像识别、语音识别和自然语言处理等任务上表现出色。",
                "keywords": ["深度学习", "神经网络", "图像识别", "语音识别"],
                "category": "科技"
            },
            {
                "id": 4,
                "question": "什么是Python?",
                "answer": "Python是一种高级编程语言，以其简洁、易读的语法和强大的生态系统而闻名。它被广泛应用于Web开发、数据分析、人工智能、科学计算等领域。",
                "keywords": ["Python", "编程语言", "开发", "数据分析"],
                "category": "科技"
            },
            {
                "id": 5,
                "question": "地球是什么形状?",
                "answer": "地球近似球形，但实际上是略微扁平的椭球体。在赤道处略微膨胀，在两极略微扁平。这种形状称为椭球体或者更精确地称为地球椭球体。",
                "keywords": ["地球", "形状", "球体", "椭球体"],
                "category": "科学"
            }
        ]
    
    def _save_knowledge_base(self):
        """保存知识库"""
        # 创建数据目录
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # 知识库文件路径
        kb_file = os.path.join(data_dir, 'knowledge_base.json')
        
        # 保存知识库
        try:
            with open(kb_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存知识库失败: {e}")
    
    def process_query(self, query):
        """处理用户查询"""
        if not self.initialized:
            return "系统正在初始化中，请稍后再试..."
        
        # 1. 输入理解阶段
        clean_query = self._preprocess_text(query)
        keywords = self._extract_keywords(clean_query)
        intent = self._identify_intent(clean_query)
        
        print(f"处理查询: {query}")
        print(f"提取关键词: {keywords}")
        print(f"识别意图: {intent}")
        
        # 2. 知识检索阶段
        relevant_knowledge = self._retrieve_knowledge(clean_query, keywords)
        
        # 3. 信息整合与答案生成阶段
        if relevant_knowledge:
            answer = self._generate_answer(query, relevant_knowledge, intent)
        else:
            # 如果没有找到相关知识，尝试生成一个通用回答
            answer = self._generate_fallback_answer(query, intent)
        
        return answer
    
    def _preprocess_text(self, text):
        """预处理文本"""
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        # 转换为小写（对中文没有影响）
        text = text.lower()
        return text
    
    def _extract_keywords(self, text):
        """提取关键词"""
        # 使用结巴分词提取关键词
        words = jieba.cut(text)
        # 过滤停用词（简化版）
        stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        return [word for word in words if word not in stopwords and len(word) > 1]
    
    def _identify_intent(self, text):
        """识别意图"""
        # 简单的基于规则的意图识别
        intent = "information"  # 默认为信息查询
        
        if any(word in text for word in ['什么是', '如何', '怎么', '为什么']):
            intent = "definition"  # 定义解释
        elif any(word in text for word in ['如何', '怎样', '怎么才能']):
            intent = "howto"  # 如何做
        elif any(word in text for word in ['比较', '区别', '不同']):
            intent = "comparison"  # 比较
        elif any(word in text for word in ['你好', '您好', '嗨', 'hi', 'hello']):
            intent = "greeting"  # 问候
        elif any(word in text for word in ['再见', '拜拜', 'bye']):
            intent = "farewell"  # 告别
        
        return intent
    
    def _retrieve_knowledge(self, query, keywords):
        """检索相关知识"""
        if not self.knowledge_base:
            return []
        
        # 提取所有问题和答案
        all_qa = [f"{item['question']} {item['answer']}" for item in self.knowledge_base]
        
        # 使用TF-IDF向量化文本
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_qa)
            query_vector = self.vectorizer.transform([query])
            
            # 计算余弦相似度
            cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
            
            # 获取最相似的知识条目
            top_indices = cosine_similarities.argsort()[-3:][::-1]  # 取相似度最高的3个
            
            # 过滤相似度太低的结果
            relevant_knowledge = []
            for i in top_indices:
                if cosine_similarities[i] > 0.1:  # 相似度阈值
                    relevant_knowledge.append(self.knowledge_base[i])
            
            return relevant_knowledge
        except Exception as e:
            print(f"知识检索错误: {e}")
            # 回退到关键词匹配
            return self._keyword_based_retrieval(keywords)
    
    def _keyword_based_retrieval(self, keywords):
        """基于关键词的知识检索"""
        relevant_knowledge = []
        
        for item in self.knowledge_base:
            # 计算关键词匹配度
            kb_keywords = set(item['keywords'])
            query_keywords = set(keywords)
            
            # 计算交集大小
            match_count = len(kb_keywords.intersection(query_keywords))
            
            if match_count > 0:
                # 添加匹配度信息
                item_copy = item.copy()
                item_copy['match_score'] = match_count / len(kb_keywords)
                relevant_knowledge.append(item_copy)
        
        # 按匹配度排序
        relevant_knowledge.sort(key=lambda x: x['match_score'], reverse=True)
        
        return relevant_knowledge[:3]  # 返回最相关的3个
    
    def _generate_answer(self, query, relevant_knowledge, intent):
        """生成答案"""
        # 如果是问候或告别意图，使用模板回复
        if intent == "greeting":
            return "您好！我是智能问答助手，有什么可以帮您解答的问题吗？"
        elif intent == "farewell":
            return "再见！如果有其他问题，随时可以问我。"
        
        # 对于其他意图，基于检索到的知识生成回答
        if len(relevant_knowledge) == 1:
            # 只有一个相关知识条目，直接使用其答案
            return relevant_knowledge[0]['answer']
        elif len(relevant_knowledge) > 1:
            # 有多个相关知识条目，进行整合
            combined_answer = "根据您的问题，我找到了以下信息：\n\n"
            
            for i, item in enumerate(relevant_knowledge):
                combined_answer += f"{item['answer']}\n\n"
            
            return combined_answer.strip()
        else:
            # 没有相关知识，返回无法回答
            return "抱歉，我暂时无法回答该问题。您可以尝试换个问法或者询问其他问题。"
    
    def _generate_fallback_answer(self, query, intent):
        """生成后备答案"""
        if intent == "greeting":
            return "您好！我是智能问答助手，有什么可以帮您解答的问题吗？"
        elif intent == "farewell":
            return "再见！如果有其他问题，随时可以问我。"
        else:
            responses = [
                "抱歉，我暂时无法回答这个问题。您可以尝试换个问法或者询问其他问题。",
                "这个问题有点超出我的知识范围，您可以尝试提问其他相关问题。",
                "我对这个问题的了解有限，无法提供准确的回答。您可以尝试询问更具体的问题。",
                "我正在不断学习中，目前还不能回答这个问题。您可以问我其他问题。"
            ]
            return np.random.choice(responses)
    
    def add_to_knowledge_base(self, question, answer, keywords=None, category="未分类"):
        """添加知识到知识库"""
        if keywords is None:
            # 自动提取关键词
            keywords = self._extract_keywords(question + " " + answer)
        
        # 生成唯一ID
        new_id = max([item['id'] for item in self.knowledge_base], default=0) + 1
        
        # 创建新知识条目
        new_item = {
            "id": new_id,
            "question": question,
            "answer": answer,
            "keywords": keywords,
            "category": category,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到知识库
        self.knowledge_base.append(new_item)
        
        # 保存知识库
        self._save_knowledge_base()
        
        return new_id
    
    def cleanup(self):
        """清理资源"""
        # 保存知识库
        self._save_knowledge_base()
        
        # 清理模型
        if self.model:
            del self.model
            self.model = None
        
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None 