#!/usr/bin/env python3
"""
Skill ROI 计算器
计算 Skill 的投资回报率
"""

import argparse
import json

# 国际化
LANG = 'zh'

MESSAGES = {
    'zh': {
        'title': '📊 Skill ROI 分析报告',
        'cost_title': '💰 投入成本',
        'usage_title': '📈 使用数据',
        'benefit_title': '💵 产出价值',
        'roi_title': '📊 ROI 分析',
        'conclusion_title': '💡 结论与建议',
        'dev_cost': '开发成本',
        'expert_cost': '专家成本',
        'maint_cost': '维护成本',
        'total': '总计',
        'usage_count': '使用次数',
        'user_count': '使用人数',
        'time_saved_per': '每次节省',
        'total_time_saved': '总节省时间',
        'labor_saved': '人力成本节省',
        'roi': '投资回报率',
        'payback': '回本周期',
        'annual': '年化收益',
        'minutes': '分钟',
        'hours': '小时',
        'months': '个月',
        'times': '次',
        'people': '人',
        'excellent': '⭐⭐⭐⭐⭐ 优秀 - 强烈推荐，可推广到其他部门',
        'good': '⭐⭐⭐⭐ 良好 - 值得投入，建议持续优化',
        'average': '⭐⭐⭐ 一般 - 可以接受，需要提升使用率',
        'low': '⭐⭐ 较低 - 需要重新评估',
        'negative': '⭐ 亏损 - 建议停止投入',
    },
    'en': {
        'title': '📊 Skill ROI Analysis Report',
        'cost_title': '💰 Investment Cost',
        'usage_title': '📈 Usage Data',
        'benefit_title': '💵 Value Generated',
        'roi_title': '📊 ROI Analysis',
        'conclusion_title': '💡 Conclusion',
        'dev_cost': 'Development Cost',
        'expert_cost': 'Expert Cost',
        'maint_cost': 'Maintenance Cost',
        'total': 'Total',
        'usage_count': 'Usage Count',
        'user_count': 'User Count',
        'time_saved_per': 'Time Saved Per Use',
        'total_time_saved': 'Total Time Saved',
        'labor_saved': 'Labor Cost Saved',
        'roi': 'ROI',
        'payback': 'Payback Period',
        'annual': 'Annual Return',
        'minutes': 'minutes',
        'hours': 'hours',
        'months': 'months',
        'times': 'times',
        'people': 'people',
        'excellent': '⭐⭐⭐⭐⭐ Excellent - Highly recommended',
        'good': '⭐⭐⭐⭐ Good - Worth the investment',
        'average': '⭐⭐⭐ Average - Acceptable, needs improvement',
        'low': '⭐⭐ Low - Needs re-evaluation',
        'negative': '⭐ Negative - Consider stopping',
    }
}

def t(key):
    return MESSAGES.get(LANG, MESSAGES['en']).get(key, key)


def calculate_cost(dev_hours, hourly_rate, expert_hours=0, expert_rate=None):
    """计算开发成本"""
    if expert_rate is None:
        expert_rate = hourly_rate * 2  # 专家默认 2 倍时薪

    dev_cost = dev_hours * hourly_rate
    expert_cost = expert_hours * expert_rate
    maint_cost = (dev_cost + expert_cost) * 0.2  # 年维护成本 20%

    return {
        'dev_cost': dev_cost,
        'expert_cost': expert_cost,
        'maint_cost': maint_cost,
        'total_cost': dev_cost + expert_cost + maint_cost
    }


def calculate_benefit(usage_count, time_saved_minutes, user_hourly_rate, period_months=1):
    """计算收益"""
    total_minutes = usage_count * time_saved_minutes
    total_hours = total_minutes / 60
    labor_saved = total_hours * user_hourly_rate

    return {
        'usage_count': usage_count,
        'total_minutes': total_minutes,
        'total_hours': total_hours,
        'labor_saved': labor_saved,
        'monthly_benefit': labor_saved / period_months if period_months > 0 else labor_saved
    }


def calculate_roi(total_cost, total_benefit, period_months=1):
    """计算 ROI"""
    if total_cost == 0:
        return {'roi': float('inf'), 'payback_months': 0, 'annual_return': total_benefit * 12}

    roi = (total_benefit - total_cost) / total_cost * 100
    monthly_benefit = total_benefit / period_months if period_months > 0 else total_benefit
    payback_months = total_cost / monthly_benefit if monthly_benefit > 0 else float('inf')
    annual_return = monthly_benefit * 12

    return {
        'roi': roi,
        'payback_months': payback_months,
        'annual_return': annual_return
    }


def get_rating(roi):
    """根据 ROI 获取评级"""
    if roi > 200:
        return t('excellent')
    elif roi > 100:
        return t('good')
    elif roi > 50:
        return t('average')
    elif roi > 0:
        return t('low')
    else:
        return t('negative')


def format_currency(amount):
    """格式化货币"""
    return f"¥{amount:,.0f}"


def generate_report(skill_name, cost_data, benefit_data, roi_data, period_months, time_saved_per):
    """生成报告"""
    lines = []
    lines.append(t('title'))
    lines.append('━' * 40)
    lines.append(f"Skill：{skill_name}")
    lines.append(f"分析周期：{period_months} 个月")
    lines.append('')

    # 成本部分
    lines.append(f"{t('cost_title')}：")
    lines.append(f"- {t('dev_cost')}：{format_currency(cost_data['dev_cost'])}")
    if cost_data['expert_cost'] > 0:
        lines.append(f"- {t('expert_cost')}：{format_currency(cost_data['expert_cost'])}")
    lines.append(f"- {t('maint_cost')}：{format_currency(cost_data['maint_cost'])}")
    lines.append(f"- {t('total')}：{format_currency(cost_data['total_cost'])}")
    lines.append('')

    # 使用数据
    lines.append(f"{t('usage_title')}：")
    lines.append(f"- {t('usage_count')}：{benefit_data['usage_count']} {t('times')}")
    lines.append(f"- {t('time_saved_per')}：{time_saved_per} {t('minutes')}")
    lines.append(f"- {t('total_time_saved')}：{benefit_data['total_hours']:.1f} {t('hours')}")
    lines.append('')

    # 收益部分
    lines.append(f"{t('benefit_title')}：")
    lines.append(f"- {t('labor_saved')}：{format_currency(benefit_data['labor_saved'])}")
    lines.append('')

    # ROI 分析
    lines.append(f"{t('roi_title')}：")
    lines.append(f"- {t('roi')}：{roi_data['roi']:.0f}%")
    if roi_data['payback_months'] != float('inf'):
        lines.append(f"- {t('payback')}：{roi_data['payback_months']:.1f} {t('months')}")
    lines.append(f"- {t('annual')}：{format_currency(roi_data['annual_return'])}")
    lines.append('')

    # 结论
    lines.append(f"{t('conclusion_title')}：")
    lines.append(get_rating(roi_data['roi']))

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Skill ROI 计算器')
    parser.add_argument('--skill-name', '-n', default='unnamed-skill', help='Skill 名称')
    parser.add_argument('--dev-hours', type=float, default=0, help='开发时间（小时）')
    parser.add_argument('--hourly-rate', type=float, default=150, help='开发者时薪')
    parser.add_argument('--expert-hours', type=float, default=0, help='专家参与时间（小时）')
    parser.add_argument('--expert-rate', type=float, help='专家时薪（默认为开发者 2 倍）')
    parser.add_argument('--usage-count', type=int, default=0, help='使用次数')
    parser.add_argument('--time-saved', type=float, default=0, help='每次节省时间（分钟）')
    parser.add_argument('--user-rate', type=float, default=100, help='用户平均时薪')
    parser.add_argument('--period', type=int, default=1, help='统计周期（月）')
    parser.add_argument('--lang', choices=['zh', 'en'], default='zh', help='输出语言')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')

    args = parser.parse_args()

    global LANG
    LANG = args.lang

    # 计算成本
    cost_data = calculate_cost(
        args.dev_hours,
        args.hourly_rate,
        args.expert_hours,
        args.expert_rate
    )

    # 计算收益
    benefit_data = calculate_benefit(
        args.usage_count,
        args.time_saved,
        args.user_rate,
        args.period
    )

    # 计算 ROI
    roi_data = calculate_roi(
        cost_data['total_cost'],
        benefit_data['labor_saved'],
        args.period
    )

    if args.json:
        result = {
            'skill_name': args.skill_name,
            'period_months': args.period,
            'cost': cost_data,
            'benefit': benefit_data,
            'roi': roi_data,
            'rating': get_rating(roi_data['roi'])
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        report = generate_report(
            args.skill_name,
            cost_data,
            benefit_data,
            roi_data,
            args.period,
            args.time_saved
        )
        print(report)


if __name__ == '__main__':
    main()
