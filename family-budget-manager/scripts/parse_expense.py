#!/usr/bin/env python3
"""
消费记录解析脚本
功能：从文本描述中提取金额、类别、日期、备注等信息
"""

import re
import argparse
from datetime import datetime
from typing import Dict, Optional, List

# 分类关键词库
CATEGORY_KEYWORDS = {
    '餐饮': ['餐厅', '外卖', '超市', '菜市场', '水果', '零食', '饮料', '咖啡', '奶茶', '早餐', '午餐', '晚餐', '买菜', '食堂'],
    '交通': ['打车', '滴滴', '出租车', '公交', '地铁', '加油', '停车', '高速', '火车', '飞机', '共享单车'],
    '购物': ['淘宝', '京东', '拼多多', '衣服', '鞋子', '化妆品', '电子产品', '家电', '手机', '电脑', '买了'],
    '娱乐': ['电影', 'KTV', '游戏', '旅游', '景点', '酒店', '健身', '运动', '唱歌', '玩'],
    '教育': ['培训', '课程', '书籍', '学费', '考试', '证书', '买书', '报名'],
    '医疗': ['药店', '医院', '挂号', '体检', '药品', '保健品', '看病', '配药'],
    '住房': ['房租', '物业', '水费', '电费', '燃气', '宽带', '维修', '家具'],
}

# 金额提取正则表达式
AMOUNT_PATTERNS = [
    r'(\d+(?:\.\d{1,2})?)\s*元',  # 50元, 50.5元
    r'¥\s*(\d+(?:\.\d{1,2})?)',   # ¥50, ¥50.5
    r'(\d+(?:\.\d{1,2})?)\s*块',  # 50块
    r'花了?\s*(\d+(?:\.\d{1,2})?)',  # 花了50, 花50
]


def extract_amount(text: str) -> Optional[float]:
    """从文本中提取金额"""
    for pattern in AMOUNT_PATTERNS:
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                continue
    return None


def classify_expense(text: str) -> str:
    """基于关键词自动分类"""
    text_lower = text.lower()
    
    # 统计每个类别的匹配分数
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            scores[category] = score
    
    # 返回得分最高的类别
    if scores:
        return max(scores, key=scores.get)
    
    return '其他'


def extract_date(text: str) -> str:
    """从文本中提取日期，默认为今天"""
    # 尝试匹配日期格式
    date_patterns = [
        r'(\d{4})-(\d{1,2})-(\d{1,2})',  # 2026-02-09
        r'(\d{1,2})月(\d{1,2})日',        # 2月9日
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                if '-' in pattern:
                    year, month, day = match.groups()
                    return f"{year}-{int(month):02d}-{int(day):02d}"
                else:
                    month, day = match.groups()
                    year = datetime.now().year
                    return f"{year}-{int(month):02d}-{int(day):02d}"
            except (ValueError, IndexError):
                continue
    
    # 处理相对日期
    if '今天' in text or '今日' in text:
        return datetime.now().strftime('%Y-%m-%d')
    elif '昨天' in text:
        from datetime import timedelta
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime('%Y-%m-%d')
    
    # 默认返回今天
    return datetime.now().strftime('%Y-%m-%d')


def extract_note(text: str, amount: float, category: str) -> str:
    """提取备注信息（去除金额和日期后的剩余文本）"""
    # 移除金额相关文本
    note = text
    for pattern in AMOUNT_PATTERNS:
        note = re.sub(pattern, '', note)
    
    # 移除日期相关文本
    note = re.sub(r'\d{4}-\d{1,2}-\d{1,2}', '', note)
    note = re.sub(r'\d{1,2}月\d{1,2}日', '', note)
    note = re.sub(r'今天|昨天|今日', '', note)
    
    # 清理多余空格和标点
    note = re.sub(r'\s+', ' ', note).strip()
    note = note.strip('，。、')
    
    return note if note else category


def parse_expense(text: str) -> Dict:
    """解析消费记录文本"""
    amount = extract_amount(text)
    if amount is None:
        return {
            'success': False,
            'error': '未能识别金额，请确保文本中包含金额信息（如"50元"、"¥50"）'
        }
    
    category = classify_expense(text)
    date = extract_date(text)
    note = extract_note(text, amount, category)
    
    return {
        'success': True,
        'date': date,
        'amount': amount,
        'category': category,
        'note': note,
        'payment_method': '未指定',
        'record_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def parse_batch(texts: List[str]) -> List[Dict]:
    """批量解析消费记录"""
    results = []
    for text in texts:
        result = parse_expense(text)
        if result['success']:
            results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(description='解析消费记录文本')
    parser.add_argument('text', help='消费记录文本（如"今天打车花了50块"）')
    parser.add_argument('--batch', action='store_true', help='批量模式（从stdin读取多行）')
    
    args = parser.parse_args()
    
    if args.batch:
        import sys
        texts = [line.strip() for line in sys.stdin if line.strip()]
        results = parse_batch(texts)
        for result in results:
            print(f"日期: {result['date']}, 金额: ¥{result['amount']:.2f}, "
                  f"类别: {result['category']}, 备注: {result['note']}")
    else:
        result = parse_expense(args.text)
        if result['success']:
            print(f"✅ 解析成功")
            print(f"日期: {result['date']}")
            print(f"金额: ¥{result['amount']:.2f}")
            print(f"类别: {result['category']}")
            print(f"备注: {result['note']}")
            print(f"记录时间: {result['record_time']}")
        else:
            print(f"❌ 解析失败: {result['error']}")


if __name__ == '__main__':
    main()
