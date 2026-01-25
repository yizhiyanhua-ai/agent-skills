#!/usr/bin/env python3
"""
部门分析工具
分析各部门的 Skill 推广优先级
"""

import argparse
import json

# 部门特征数据库
DEPARTMENT_PROFILES = {
    '技术': {
        'name_en': 'Engineering',
        'tech_acceptance': 5,  # 1-5
        'usage_potential': 5,
        'influence': 4,
        'difficulty': 1,
        'typical_size_ratio': 0.25,
        'use_cases': ['代码生成', '文档编写', '问题排查', '代码审查'],
        'risks': ['过度依赖', '安全顾虑'],
        'strategy': '可作为种子部门，强调效率提升'
    },
    '产品': {
        'name_en': 'Product',
        'tech_acceptance': 4,
        'usage_potential': 4,
        'influence': 4,
        'difficulty': 2,
        'typical_size_ratio': 0.10,
        'use_cases': ['需求分析', '竞品研究', '文档撰写', 'PRD 生成'],
        'risks': ['信息准确性'],
        'strategy': '与技术部门同步推广，强调协作效率'
    },
    '销售': {
        'name_en': 'Sales',
        'tech_acceptance': 3,
        'usage_potential': 4,
        'influence': 3,
        'difficulty': 3,
        'typical_size_ratio': 0.30,
        'use_cases': ['客户沟通', '方案撰写', '数据分析', '话术优化'],
        'risks': ['客户信息安全', '过度依赖模板'],
        'strategy': '用 ROI 数据说话，提供即用型 Skill'
    },
    '市场': {
        'name_en': 'Marketing',
        'tech_acceptance': 3,
        'usage_potential': 4,
        'influence': 3,
        'difficulty': 2,
        'typical_size_ratio': 0.15,
        'use_cases': ['内容创作', '数据分析', '活动策划', '社媒运营'],
        'risks': ['品牌一致性', '创意同质化'],
        'strategy': '强调创意辅助，提供内容生成 Skill'
    },
    '财务': {
        'name_en': 'Finance',
        'tech_acceptance': 2,
        'usage_potential': 3,
        'influence': 2,
        'difficulty': 4,
        'typical_size_ratio': 0.10,
        'use_cases': ['报表分析', '数据处理', '审计辅助', '预算编制'],
        'risks': ['数据准确性', '合规风险'],
        'strategy': '强调准确性和审核，从低风险场景开始'
    },
    'HR': {
        'name_en': 'Human Resources',
        'tech_acceptance': 2,
        'usage_potential': 3,
        'influence': 2,
        'difficulty': 3,
        'typical_size_ratio': 0.10,
        'use_cases': ['简历筛选', '培训材料', '政策解读', '员工沟通'],
        'risks': ['隐私问题', '人情味缺失'],
        'strategy': '提供简单易用的 Skill，强调辅助而非替代'
    },
    '客服': {
        'name_en': 'Customer Service',
        'tech_acceptance': 3,
        'usage_potential': 5,
        'influence': 2,
        'difficulty': 2,
        'typical_size_ratio': 0.15,
        'use_cases': ['问题解答', '工单处理', '知识库查询', '客户跟进'],
        'risks': ['回复机械化', '复杂问题处理'],
        'strategy': '高频使用场景，快速见效，适合早期推广'
    },
    '法务': {
        'name_en': 'Legal',
        'tech_acceptance': 2,
        'usage_potential': 4,
        'influence': 3,
        'difficulty': 4,
        'typical_size_ratio': 0.05,
        'use_cases': ['合同审查', '风险识别', '法规查询', '文书起草'],
        'risks': ['法律责任', '准确性要求高'],
        'strategy': '专家参与开发，强调人工审核'
    },
    '运营': {
        'name_en': 'Operations',
        'tech_acceptance': 3,
        'usage_potential': 4,
        'influence': 3,
        'difficulty': 2,
        'typical_size_ratio': 0.10,
        'use_cases': ['数据分析', '流程优化', '报告生成', '活动运营'],
        'risks': ['数据敏感性'],
        'strategy': '数据驱动，展示效率提升'
    }
}


def get_acceptance_level(score):
    """获取接受度等级"""
    if score >= 4:
        return '🟢 高'
    elif score >= 3:
        return '🟡 中'
    else:
        return '🔴 低'


def calculate_priority_score(profile):
    """计算优先级分数"""
    # 权重：接受度 40%，使用潜力 30%，影响力 20%，难度（反向）10%
    score = (
        profile['tech_acceptance'] * 0.4 +
        profile['usage_potential'] * 0.3 +
        profile['influence'] * 0.2 +
        (6 - profile['difficulty']) * 0.1
    )
    return score


def analyze_departments(dept_list, total_size=None):
    """分析部门列表"""
    results = []

    for dept_name in dept_list:
        dept_name = dept_name.strip()
        profile = DEPARTMENT_PROFILES.get(dept_name)

        if profile:
            priority_score = calculate_priority_score(profile)
            size = int(total_size * profile['typical_size_ratio']) if total_size else None

            results.append({
                'name': dept_name,
                'name_en': profile['name_en'],
                'priority_score': priority_score,
                'tech_acceptance': profile['tech_acceptance'],
                'acceptance_level': get_acceptance_level(profile['tech_acceptance']),
                'usage_potential': profile['usage_potential'],
                'influence': profile['influence'],
                'difficulty': profile['difficulty'],
                'size': size,
                'use_cases': profile['use_cases'],
                'risks': profile['risks'],
                'strategy': profile['strategy']
            })
        else:
            # 未知部门，使用默认值
            results.append({
                'name': dept_name,
                'name_en': dept_name,
                'priority_score': 3.0,
                'tech_acceptance': 3,
                'acceptance_level': '🟡 中',
                'usage_potential': 3,
                'influence': 3,
                'difficulty': 3,
                'size': None,
                'use_cases': ['待分析'],
                'risks': ['待评估'],
                'strategy': '需要进一步了解部门特点'
            })

    # 按优先级排序
    results.sort(key=lambda x: x['priority_score'], reverse=True)

    # 添加排名
    for i, r in enumerate(results, 1):
        r['rank'] = i

    return results


def generate_report(results, total_size=None):
    """生成分析报告"""
    lines = []
    lines.append('📊 部门推广优先级分析')
    lines.append('━' * 40)
    if total_size:
        lines.append(f'企业规模：{total_size} 人')
    lines.append('')

    lines.append('📋 优先级排序：')
    lines.append('')

    for r in results:
        size_str = f"（{r['size']}人）" if r['size'] else ''
        lines.append(f"{r['rank']}. {r['acceptance_level']} **{r['name']}**{size_str}")
        lines.append(f"   - 使用场景：{', '.join(r['use_cases'][:3])}")
        lines.append(f"   - 推广策略：{r['strategy']}")
        lines.append(f"   - 潜在风险：{', '.join(r['risks'])}")
        lines.append('')

    # 推广建议
    lines.append('💡 推广建议：')
    lines.append('')

    high_priority = [r for r in results if r['tech_acceptance'] >= 4]
    medium_priority = [r for r in results if r['tech_acceptance'] == 3]
    low_priority = [r for r in results if r['tech_acceptance'] < 3]

    if high_priority:
        names = ', '.join([r['name'] for r in high_priority])
        lines.append(f"🟢 **第一批（种子部门）**：{names}")
        lines.append("   建议：作为试点部门，快速验证 Skill 效果")
        lines.append('')

    if medium_priority:
        names = ', '.join([r['name'] for r in medium_priority])
        lines.append(f"🟡 **第二批（扩展部门）**：{names}")
        lines.append("   建议：在种子部门成功后推广，需要案例支撑")
        lines.append('')

    if low_priority:
        names = ', '.join([r['name'] for r in low_priority])
        lines.append(f"🔴 **第三批（后期部门）**：{names}")
        lines.append("   建议：需要领导推动和充分培训")
        lines.append('')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='部门推广优先级分析')
    parser.add_argument('--departments', '-d', required=True,
                        help='部门列表，逗号分隔（如：技术,产品,销售）')
    parser.add_argument('--total-size', '-s', type=int, help='企业总人数')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')

    args = parser.parse_args()

    dept_list = args.departments.split(',')
    results = analyze_departments(dept_list, args.total_size)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        report = generate_report(results, args.total_size)
        print(report)


if __name__ == '__main__':
    main()
