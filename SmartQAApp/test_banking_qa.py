#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
银行业务智能问答系统测试脚本
用于测试银行业务知识库和模糊查询功能
"""

import os
import sys
import logging
from models.qa_processor import QAProcessor

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_banking_qa():
    """测试银行业务智能问答系统"""
    print("="*50)
    print("银行业务智能问答系统测试")
    print("="*50)
    
    # 初始化QA处理器
    qa = QAProcessor()
    qa.initialize()
    
    # 测试问题集 - 包含精确问题和模糊问题
    test_questions = [
        # 精确问题（与知识库中的问题完全匹配）
        "如何开立银行账户?",
        "银行卡丢失了怎么办?",
        "如何申请个人贷款?",
        
        # 模糊问题（与知识库中的问题相似但表述不同）
        "我想开个银行卡",
        "信用卡丢了该怎么办",
        "怎样才能贷款买房",
        "房贷现在是多少利息",
        "信用卡逾期会影响征信吗",
        "怎么提高我的信用卡额度",
        "银行都有什么理财产品",
        "大额存单和定期存款哪个好",
        "手机银行怎么注册",
        "如何给别人转账",
        
        # 复杂问题（需要更强的理解能力）
        "我的卡丢了，但是我不知道卡号，能挂失吗",
        "现在首套房贷款利率是多少，需要什么材料",
        "信用卡逾期三天会有什么影响，会上征信吗",
        "我想买理财产品，风险等级二级的有哪些推荐",
        "大额存单提前支取利息怎么算"
    ]
    
    # 测试每个问题
    for i, question in enumerate(test_questions):
        print(f"\n问题 {i+1}: {question}")
        print("-"*50)
        
        # 处理问题并获取回答
        answer = qa.process_query(question)
        
        # 显示回答
        print(f"回答: {answer}")
        print("-"*50)
    
    print("\n测试完成!")

def interactive_mode():
    """交互式问答模式"""
    print("="*50)
    print("银行业务智能问答系统 - 交互模式")
    print("="*50)
    print("输入问题开始对话，输入'退出'结束对话")
    
    # 初始化QA处理器
    qa = QAProcessor()
    qa.initialize()
    
    while True:
        print("\n" + "-"*50)
        question = input("您的问题: ")
        
        if question in ["退出", "exit", "quit", "q"]:
            break
            
        if not question.strip():
            continue
            
        # 处理问题并获取回答
        answer = qa.process_query(question)
        
        # 显示回答
        print(f"\n回答: {answer}")
    
    print("\n感谢使用银行业务智能问答系统!")

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        test_banking_qa() 