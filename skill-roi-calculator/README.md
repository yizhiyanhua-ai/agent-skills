# Skill ROI Calculator

[🇨🇳 中文](./README_CN.md)

Calculate the Return on Investment (ROI) for Skills to evaluate whether development is worthwhile.

## Features

- Calculate development costs (developer time, expert time, maintenance)
- Estimate benefits (time saved, labor cost reduction)
- Generate ROI analysis reports
- Support both Chinese and English output

## Usage

```bash
# Full ROI calculation
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

# Output as JSON
python scripts/calculate_roi.py --json ...

# English output
python scripts/calculate_roi.py --lang en ...
```

## ROI Rating Scale

| ROI | Rating | Recommendation |
|-----|--------|----------------|
| > 200% | Excellent | Highly recommended, expand to other departments |
| 100-200% | Good | Worth the investment, continue optimizing |
| 50-100% | Average | Acceptable, needs usage improvement |
| 0-50% | Low | Needs re-evaluation |
| < 0% | Negative | Consider stopping investment |

## License

MIT
