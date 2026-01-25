#!/usr/bin/env python3
"""
知识模式提取脚本
从对话记录、文档或描述中提取可复用的知识模式
"""

import argparse
import json
import sys
from pathlib import Path
from collections import Counter

# 国际化支持
LANG = 'zh'

MESSAGES = {
    'zh': {
        'title': '📋 知识提取报告',
        'source': '来源',
        'count': '分析数量',
        'patterns_found': '🔍 发现的可复用模式',
        'pattern': '模式',
        'frequency': '出现',
        'times': '次',
        'percent': '占比',
        'trigger': '触发场景',
        'key_points': '核心要点',
        'example': '示例',
        'suggested_skills': '💡 建议生成的 Skill',
        'coverage': '📊 知识覆盖度',
        'extracted': '已提取',
        'patterns': '个模式',
        'coverage_rate': '覆盖场景',
        'suggest_more': '建议补充',
        'no_patterns': '未发现明显的可复用模式',
        'analyzing': '正在分析...',
        'done': '分析完成',
    },
    'en': {
        'title': '📋 Knowledge Extraction Report',
        'source': 'Source',
        'count': 'Analyzed',
        'patterns_found': '🔍 Reusable Patterns Found',
        'pattern': 'Pattern',
        'frequency': 'Frequency',
        'times': 'times',
        'percent': 'ratio',
        'trigger': 'Trigger',
        'key_points': 'Key Points',
        'example': 'Example',
        'suggested_skills': '💡 Suggested Skills',
        'coverage': '📊 Knowledge Coverage',
        'extracted': 'Extracted',
        'patterns': 'patterns',
        'coverage_rate': 'Coverage',
        'suggest_more': 'Need more data on',
        'no_patterns': 'No obvious reusable patterns found',
        'analyzing': 'Analyzing...',
        'done': 'Done',
    }
}

def t(key):
    """获取翻译文本"""
    return MESSAGES.get(LANG, MESSAGES['en']).get(key, key)


# 模式识别规则
PATTERN_RULES = {
    'conversation': {
        'opening': {
            'name_zh': '开场白模式',
            'name_en': 'Opening Pattern',
            'keywords': ['你好', '您好', '请问', '了解', '需求', '挑战', '问题', 'hello', 'hi', 'how can'],
            'description': '对话开始时的标准话术'
        },
        'diagnosis': {
            'name_zh': '问题诊断模式',
            'name_en': 'Diagnosis Pattern',
            'keywords': ['什么情况', '具体', '详细', '能说说', '遇到', '发生', 'what happened', 'tell me more'],
            'description': '深入了解问题的提问方式'
        },
        'objection': {
            'name_zh': '异议处理模式',
            'name_en': 'Objection Handling',
            'keywords': ['理解', '确实', '但是', '不过', '其实', '算一下', 'understand', 'however', 'actually'],
            'description': '处理客户异议的话术'
        },
        'closing': {
            'name_zh': '促成/收尾模式',
            'name_en': 'Closing Pattern',
            'keywords': ['这样吧', '建议', '如果', '现在', '优惠', '限时', 'suggest', 'recommend', 'special offer'],
            'description': '促成交易或结束对话的话术'
        },
        'empathy': {
            'name_zh': '共情模式',
            'name_en': 'Empathy Pattern',
            'keywords': ['理解您', '明白', '感受', '确实不容易', '换位思考', 'understand', 'feel', 'appreciate'],
            'description': '表达理解和共情的话术'
        }
    },
    'document': {
        'checklist': {
            'name_zh': '检查清单模式',
            'name_en': 'Checklist Pattern',
            'keywords': ['检查', '确认', '核实', '是否', '必须', 'check', 'verify', 'must', 'required'],
            'description': '需要逐项检查的清单'
        },
        'template': {
            'name_zh': '模板模式',
            'name_en': 'Template Pattern',
            'keywords': ['模板', '格式', '标准', '范例', '示例', 'template', 'format', 'standard', 'example'],
            'description': '可复用的文档模板'
        },
        'decision': {
            'name_zh': '决策树模式',
            'name_en': 'Decision Tree Pattern',
            'keywords': ['如果', '那么', '否则', '情况', '分类', 'if', 'then', 'else', 'case', 'category'],
            'description': '基于条件的决策逻辑'
        },
        'procedure': {
            'name_zh': '流程步骤模式',
            'name_en': 'Procedure Pattern',
            'keywords': ['第一步', '然后', '接下来', '最后', '步骤', 'step', 'first', 'then', 'next', 'finally'],
            'description': '标准操作流程'
        }
    }
}


def analyze_text(text, material_type='conversation'):
    """分析文本，提取模式"""
    rules = PATTERN_RULES.get(material_type, PATTERN_RULES['conversation'])

    # 按段落分割
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    total_paragraphs = len(paragraphs)

    # 统计每种模式的出现次数
    pattern_counts = Counter()
    pattern_examples = {}

    for para in paragraphs:
        para_lower = para.lower()
        for pattern_id, pattern_info in rules.items():
            for keyword in pattern_info['keywords']:
                if keyword.lower() in para_lower:
                    pattern_counts[pattern_id] += 1
                    if pattern_id not in pattern_examples:
                        pattern_examples[pattern_id] = para[:100] + ('...' if len(para) > 100 else '')
                    break

    return pattern_counts, pattern_examples, total_paragraphs, rules


def generate_report(source_name, pattern_counts, pattern_examples, total_count, rules):
    """生成知识提取报告"""
    lines = []
    lines.append(t('title'))
    lines.append('━' * 40)
    lines.append(f"{t('source')}：{source_name}")
    lines.append(f"{t('count')}：{total_count} 条记录")
    lines.append('')

    if not pattern_counts:
        lines.append(t('no_patterns'))
        return '\n'.join(lines)

    lines.append(f"{t('patterns_found')}：")
    lines.append('')

    # 按出现次数排序
    sorted_patterns = pattern_counts.most_common()

    for i, (pattern_id, count) in enumerate(sorted_patterns, 1):
        pattern_info = rules.get(pattern_id, {})
        name = pattern_info.get(f'name_{LANG}', pattern_info.get('name_en', pattern_id))
        percent = round(count / total_count * 100) if total_count > 0 else 0

        lines.append(f"{i}. **{name}**（{t('frequency')} {count} {t('times')}，{t('percent')} {percent}%）")
        lines.append(f"   - {t('trigger')}：{pattern_info.get('description', '')}")
        if pattern_id in pattern_examples:
            lines.append(f"   - {t('example')}：「{pattern_examples[pattern_id]}」")
        lines.append('')

    # 建议生成的 Skill
    lines.append(f"{t('suggested_skills')}：")
    for pattern_id, count in sorted_patterns[:3]:
        pattern_info = rules.get(pattern_id, {})
        name = pattern_info.get(f'name_{LANG}', pattern_info.get('name_en', pattern_id))
        lines.append(f"- {pattern_id}-skill（{name}助手）")

    lines.append('')
    lines.append(f"{t('coverage')}：")
    lines.append(f"- {t('extracted')}：{len(pattern_counts)} {t('patterns')}")
    coverage = round(sum(pattern_counts.values()) / total_count * 100) if total_count > 0 else 0
    lines.append(f"- {t('coverage_rate')}：{coverage}%")

    return '\n'.join(lines)


def generate_skill_draft(pattern_counts, pattern_examples, rules, skill_name='extracted-knowledge'):
    """生成 Skill 草稿"""
    sorted_patterns = pattern_counts.most_common()

    lines = []
    lines.append('---')
    lines.append(f'name: {skill_name}')
    lines.append(f'description: 从经验中提取的知识模式，包含 {len(sorted_patterns)} 种可复用模式。')
    lines.append('---')
    lines.append('')
    lines.append(f'# {skill_name}')
    lines.append('')
    lines.append('## 使用场景')
    lines.append('')
    lines.append('当遇到以下场景时使用此 Skill：')
    for pattern_id, _ in sorted_patterns[:3]:
        pattern_info = rules.get(pattern_id, {})
        lines.append(f'- {pattern_info.get("description", pattern_id)}')
    lines.append('')
    lines.append('## 核心模式')
    lines.append('')

    for i, (pattern_id, _count) in enumerate(sorted_patterns, 1):
        pattern_info = rules.get(pattern_id, {})
        name = pattern_info.get(f'name_{LANG}', pattern_info.get('name_en', pattern_id))

        lines.append(f'### 模式 {i}：{name}')
        lines.append('')
        lines.append(f'**触发条件**：{pattern_info.get("description", "")}')
        lines.append('')
        lines.append('**执行步骤**：')
        lines.append('1. [根据实际情况填写]')
        lines.append('2. [根据实际情况填写]')
        lines.append('')
        if pattern_id in pattern_examples:
            lines.append('**示例**：')
            lines.append(f'> {pattern_examples[pattern_id]}')
            lines.append('')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='知识模式提取工具')
    parser.add_argument('--input', '-i', help='输入文件路径')
    parser.add_argument('--text', '-t', help='直接输入文本')
    parser.add_argument('--type', choices=['conversation', 'document', 'description'],
                        default='conversation', help='材料类型')
    parser.add_argument('--source', '-s', default='用户提供的材料', help='来源描述')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--skill-name', default='extracted-knowledge', help='生成的 Skill 名称')
    parser.add_argument('--lang', choices=['zh', 'en'], default='zh', help='输出语言')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')

    args = parser.parse_args()

    global LANG
    LANG = args.lang

    # 获取输入文本
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
        source = args.source or Path(args.input).name
    elif args.text:
        text = args.text
        source = args.source
    else:
        # 从 stdin 读取
        text = sys.stdin.read()
        source = args.source

    if not text.strip():
        print("错误：没有输入内容" if LANG == 'zh' else "Error: No input content")
        sys.exit(1)

    # 分析文本
    print(t('analyzing'), file=sys.stderr)
    pattern_counts, pattern_examples, total_count, rules = analyze_text(text, args.type)

    if args.json:
        # JSON 输出
        result = {
            'source': source,
            'total_count': total_count,
            'patterns': [
                {
                    'id': pid,
                    'name': rules.get(pid, {}).get(f'name_{LANG}', pid),
                    'count': count,
                    'percent': round(count / total_count * 100) if total_count > 0 else 0,
                    'example': pattern_examples.get(pid, '')
                }
                for pid, count in pattern_counts.most_common()
            ]
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 生成报告
        report = generate_report(source, pattern_counts, pattern_examples, total_count, rules)
        print(report)
        print()

        # 生成 Skill 草稿
        if pattern_counts:
            print('=' * 40)
            print('📝 Skill 草稿：')
            print('=' * 40)
            print()
            skill_draft = generate_skill_draft(pattern_counts, pattern_examples, rules, args.skill_name)
            print(skill_draft)

    # 保存输出
    if args.output and not args.json:
        report = generate_report(source, pattern_counts, pattern_examples, total_count, rules)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n{t('done')}：{args.output}", file=sys.stderr)


if __name__ == '__main__':
    main()
