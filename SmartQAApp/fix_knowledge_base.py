#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复知识库JSON文件格式错误
"""

import os
import json
import re
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_json_file(file_path):
    """
    修复JSON文件格式错误
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        成功修复返回True，否则返回False
    """
    logger.info(f"检查JSON文件: {file_path}")
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试解析JSON
        try:
            json.loads(content)
            logger.info("JSON格式正确，无需修复")
            return True
        except json.JSONDecodeError as e:
            logger.error(f"JSON格式错误: {e}")
            
            # 显示错误位置附近的内容
            error_pos = e.pos
            start = max(0, error_pos - 50)
            end = min(len(content), error_pos + 50)
            error_context = content[start:end].replace('\n', '\\n')
            logger.info(f"错误位置附近的内容: {error_context}")
            
            # 根据错误类型尝试修复
            if "Expecting ',' delimiter" in str(e):
                # 在错误位置插入逗号
                fixed_content = content[:error_pos] + "," + content[error_pos:]
                logger.info("尝试在错误位置插入逗号")
            elif "Expecting ':' delimiter" in str(e):
                # 在错误位置插入冒号
                fixed_content = content[:error_pos] + ":" + content[error_pos:]
                logger.info("尝试在错误位置插入冒号")
            elif "Expecting value" in str(e):
                # 可能是缺少值或引号不匹配
                # 这种情况比较复杂，尝试重新创建一个有效的知识库
                logger.warning("检测到可能是值格式错误，尝试重建知识库")
                return rebuild_knowledge_base(file_path)
            else:
                # 其他错误，尝试使用更通用的修复方法
                logger.warning("未知错误类型，尝试通用修复方法")
                return rebuild_knowledge_base(file_path)
            
            # 尝试验证修复后的内容
            try:
                json.loads(fixed_content)
                # 写回文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                logger.info("成功修复JSON格式错误")
                return True
            except Exception as fix_error:
                logger.error(f"修复失败: {fix_error}")
                # 尝试更通用的修复方法
                return rebuild_knowledge_base(file_path)
    
    except Exception as e:
        logger.error(f"处理文件时出错: {e}")
        return False

def rebuild_knowledge_base(file_path):
    """
    重建知识库文件
    
    Args:
        file_path: 知识库文件路径
        
    Returns:
        成功重建返回True，否则返回False
    """
    logger.info("尝试重建知识库文件")
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试提取有效的条目
        entries = []
        # 使用正则表达式匹配每个条目
        pattern = r'\s*\{\s*"id"\s*:\s*(\d+)\s*,\s*"question"\s*:\s*"([^"]+)"\s*,\s*"answer"\s*:\s*"([^"]+)"\s*,\s*"keywords"\s*:\s*\[(.*?)\]\s*,\s*"category"\s*:\s*"([^"]+)"\s*\}'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            try:
                entry_id = int(match.group(1))
                question = match.group(2)
                answer = match.group(3)
                keywords_str = match.group(4)
                category = match.group(5)
                
                # 解析关键词
                keywords = []
                keyword_pattern = r'"([^"]+)"'
                keyword_matches = re.finditer(keyword_pattern, keywords_str)
                for keyword_match in keyword_matches:
                    keywords.append(keyword_match.group(1))
                
                # 创建条目
                entry = {
                    "id": entry_id,
                    "question": question,
                    "answer": answer,
                    "keywords": keywords,
                    "category": category
                }
                entries.append(entry)
                logger.info(f"成功提取条目ID: {entry_id}")
            except Exception as e:
                logger.warning(f"提取条目时出错: {e}")
        
        # 如果没有提取到任何条目，尝试创建一个基本的知识库
        if not entries:
            logger.warning("未能提取任何有效条目，创建基本知识库")
            entries = [
                {
                    "id": 1,
                    "question": "如何开立银行账户?",
                    "answer": "开立银行账户需要您携带有效身份证件(身份证/护照)、手机号码等到银行网点办理。",
                    "keywords": ["开户", "开立账户", "银行账户"],
                    "category": "账户服务"
                },
                {
                    "id": 2,
                    "question": "银行卡丢失了怎么办?",
                    "answer": "银行卡丢失后，请立即拨打银行客服热线挂失卡片，并前往银行网点补办新卡。",
                    "keywords": ["银行卡丢失", "丢卡", "挂失"],
                    "category": "账户安全"
                }
            ]
        
        # 写入新的知识库文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=4)
        
        logger.info(f"成功重建知识库，共{len(entries)}个条目")
        return True
    
    except Exception as e:
        logger.error(f"重建知识库失败: {e}")
        
        # 创建一个最小的知识库
        try:
            minimal_kb = [
                {
                    "id": 1,
                    "question": "如何开立银行账户?",
                    "answer": "开立银行账户需要您携带有效身份证件(身份证/护照)、手机号码等到银行网点办理。",
                    "keywords": ["开户", "开立账户", "银行账户"],
                    "category": "账户服务"
                }
            ]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(minimal_kb, f, ensure_ascii=False, indent=4)
            
            logger.info("已创建最小知识库")
            return True
        except Exception as e2:
            logger.error(f"创建最小知识库失败: {e2}")
            return False

def main():
    """主函数"""
    # 获取知识库文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    knowledge_base_path = os.path.join(current_dir, "data", "knowledge_base.json")
    
    # 检查文件是否存在
    if not os.path.exists(knowledge_base_path):
        logger.error(f"知识库文件不存在: {knowledge_base_path}")
        # 尝试创建data目录
        data_dir = os.path.join(current_dir, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"已创建目录: {data_dir}")
        
        # 创建一个基本的知识库文件
        basic_kb = [
            {
                "id": 1,
                "question": "如何开立银行账户?",
                "answer": "开立银行账户需要您携带有效身份证件(身份证/护照)、手机号码等到银行网点办理。个人账户可通过柜台或自助机办理，企业账户需提供营业执照、组织机构代码证等材料。",
                "keywords": ["开户", "开立账户", "银行账户", "开卡"],
                "category": "账户服务"
            },
            {
                "id": 2,
                "question": "银行卡丢失了怎么办?",
                "answer": "银行卡丢失后，请立即采取以下措施：1. 拨打银行客服热线挂失卡片；2. 登录手机银行或网上银行冻结账户；3. 携带有效身份证件到银行网点补办新卡。",
                "keywords": ["银行卡丢失", "丢卡", "挂失", "补办"],
                "category": "账户安全"
            }
        ]
        
        try:
            with open(knowledge_base_path, 'w', encoding='utf-8') as f:
                json.dump(basic_kb, f, ensure_ascii=False, indent=4)
            logger.info(f"已创建基本知识库文件: {knowledge_base_path}")
        except Exception as e:
            logger.error(f"创建知识库文件失败: {e}")
            return
    
    # 修复知识库文件
    if fix_json_file(knowledge_base_path):
        logger.info("知识库修复完成")
    else:
        logger.error("知识库修复失败")

def add_rate_questions_to_knowledge_base():
    """添加更多银行利率相关问题到知识库"""
    logger.info("开始添加银行利率相关问题到知识库")
    
    # 获取知识库文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    knowledge_base_path = os.path.join(current_dir, "data", "knowledge_base.json")
    
    # 检查文件是否存在
    if not os.path.exists(knowledge_base_path):
        logger.error(f"知识库文件不存在: {knowledge_base_path}")
        return False
    
    try:
        # 读取当前知识库
        with open(knowledge_base_path, 'r', encoding='utf-8') as f:
            knowledge_base = json.load(f)
        
        # 获取当前最大ID
        current_max_id = max(item["id"] for item in knowledge_base)
        
        # 新的利率相关问题
        new_questions = [
            {
                "id": current_max_id + 1,
                "question": "哪家银行的存款利率最高?",
                "answer": "一般来说，中小型银行和互联网银行的存款利率通常高于大型国有银行。截至2023年，某些城商行和农商行的定期存款利率可达2.25%-2.75%，而互联网银行如微众银行、网商银行等的智能存款产品利率可达3.0%-3.5%。具体最高利率会随市场变化调整，建议通过银行官网或咨询客服获取最新准确信息。同时，可以关注大额存单、结构性存款等特殊存款产品，它们的利率通常高于普通定期存款。",
                "keywords": [
                    "存款利率最高",
                    "最高利率",
                    "高利率",
                    "存款收益",
                    "定期存款",
                    "大额存单"
                ],
                "category": "存款服务"
            },
            {
                "id": current_max_id + 2,
                "question": "哪家银行的贷款利率最低?",
                "answer": "贷款利率的高低主要受贷款类型、个人资质、银行政策等多方面因素影响。一般来说，国有大型银行(如工商银行、建设银行等)的贷款利率相对较低，尤其是房贷业务。以房贷为例，首套房按揭贷款利率可能低至LPR+0个基点(即基准利率)，甚至有少数银行可能提供LPR-5个基点的优惠。对于个人消费贷款，各家银行差异较大，通常资质优良的客户可以获得更低的利率。建议您同时咨询多家银行，并根据自身情况和贷款需求进行比较选择。",
                "keywords": [
                    "贷款利率最低",
                    "最低利率",
                    "贷款利息",
                    "房贷利率",
                    "按揭利率",
                    "优惠利率"
                ],
                "category": "贷款服务"
            },
            {
                "id": current_max_id + 3,
                "question": "银行理财产品哪种收益最高?",
                "answer": "在银行理财产品中，一般来说风险与收益成正比。股票型理财产品的长期收益率通常高于其他类型，但风险也最高，历史年化收益可能达6%-10%；混合型产品次之，年化收益可能在4%-8%之间；债券型产品风险收益适中，年化收益约3%-5%；货币市场类和固定收益类产品风险最低，收益通常在2%-4%之间。此外，私人银行专属产品、结构性理财产品在特定市场环境下可能获得较高收益。投资前应根据个人风险承受能力选择适合的产品，不要单纯追求高收益而忽视风险。",
                "keywords": [
                    "理财产品收益",
                    "最高收益",
                    "高收益理财",
                    "理财收益率",
                    "投资回报",
                    "收益对比"
                ],
                "category": "理财投资"
            },
            {
                "id": current_max_id + 4,
                "question": "各银行大额存单利率有什么区别?",
                "answer": "各银行大额存单利率存在明显差异。一般而言，中小银行(如城商行、农商行)的大额存单利率高于国有大型银行，差距可达0.3%-0.7%。同一银行不同期限的大额存单，期限越长利率越高，如3年期通常比1年期高0.4%-0.8%。不同起存金额的利率也有差异，金额越大利率可能越优惠。此外，银行会根据资金状况不定期推出利率上浮的特惠大额存单。投资者可以通过银行官网、手机APP或咨询客户经理了解各银行最新的大额存单利率情况。",
                "keywords": [
                    "大额存单利率",
                    "各行利率",
                    "利率对比",
                    "存单收益",
                    "最高存款利率",
                    "大额存单对比"
                ],
                "category": "存款服务"
            },
            {
                "id": current_max_id + 5,
                "question": "信用卡分期手续费哪家银行最低?",
                "answer": "信用卡分期手续费率各银行差异较大，一般而言，招商银行、中信银行的信用卡分期手续费相对较低，部分分期活动的费率可低至0.3%/月。交通银行、平安银行等在特定活动期间也会提供较低费率。此外，很多银行针对新客户有首次分期免手续费的优惠。影响手续费的因素包括：分期期数(期数越长月费率可能越低)、客户等级(高端客户有优惠)、活动优惠(节假日特惠)等。建议在申请分期前，比较不同银行的分期费率和总费用，选择最划算的方案。",
                "keywords": [
                    "信用卡分期",
                    "手续费最低",
                    "分期费率",
                    "分期利息",
                    "分期手续费对比",
                    "信用卡费用"
                ],
                "category": "信用卡"
            }
        ]
        
        # 添加新问题到知识库
        for question in new_questions:
            knowledge_base.append(question)
        
        # 写回文件
        with open(knowledge_base_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, ensure_ascii=False, indent=4)
        
        logger.info(f"成功添加{len(new_questions)}个利率相关问题到知识库")
        return True
    
    except Exception as e:
        logger.error(f"添加利率问题失败: {e}")
        return False

if __name__ == "__main__":
    logger.info("开始修复知识库")
    main()
    # 添加利率相关问题
    add_rate_questions_to_knowledge_base()
    logger.info("处理完成")
    print("\n脚本执行完成，请按任意键退出...")
    input() 