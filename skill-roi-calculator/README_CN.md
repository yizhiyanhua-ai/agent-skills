# Skill ROI 计算器

[🇬🇧 English](./README.md)

计算 Skill 的投资回报率（ROI），评估开发是否值得。

## 功能特点

- 计算开发成本（开发时间、专家时间、维护成本）
- 估算收益（节省时间、人力成本降低）
- 生成 ROI 分析报告
- 支持中英文输出

## 使用方法

```bash
# 完整 ROI 计算
python scripts/calculate_roi.py \
  --skill-name "contract-reviewer" \
  --dev-hours 4 \
  --hourly-rate 150 \
  --expert-hours 8 \
  --expert-rate 300 \
  --usage-count 156 \
  --time-saved 15 \
  --user-rate 200 \
  --period 3

# 输出 JSON 格式
python scripts/calculate_roi.py --json ...

# 英文输出
python scripts/calculate_roi.py --lang en ...
```

## ROI 评级标准

| ROI | 评级 | 建议 |
|-----|------|------|
| > 200% | ⭐⭐⭐⭐⭐ 优秀 | 强烈推荐，可推广到其他部门 |
| 100-200% | ⭐⭐⭐⭐ 良好 | 值得投入，建议持续优化 |
| 50-100% | ⭐⭐⭐ 一般 | 可以接受，需要提升使用率 |
| 0-50% | ⭐⭐ 较低 | 需要重新评估 |
| < 0% | ⭐ 亏损 | 建议停止投入 |

## 许可证

MIT
