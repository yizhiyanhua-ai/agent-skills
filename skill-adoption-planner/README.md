# Skill Adoption Planner

[🇨🇳 中文](./README_CN.md)

Plan Skill rollout strategies within organizations, identify seed users, create phased plans, and prepare for resistance.

## Features

- Analyze department characteristics and tech acceptance
- Prioritize departments for rollout
- Identify key roles (seed users, influencers, resistors)
- Generate phased adoption plans
- Predict and address common resistance

## Usage

```bash
# Analyze departments
python scripts/analyze_departments.py \
  --departments "技术,产品,销售,市场,财务,HR"

# With company size for headcount estimates
python scripts/analyze_departments.py \
  --departments "技术,产品,销售" \
  --total-size 200

# Output as JSON
python scripts/analyze_departments.py --json ...
```

## Supported Departments

| Department | Tech Acceptance | Best Strategy |
|------------|-----------------|---------------|
| Engineering | High | Seed department, emphasize efficiency |
| Product | High | Sync with engineering, collaboration focus |
| Sales | Medium | ROI-driven, ready-to-use Skills |
| Marketing | Medium | Creative assistance, content generation |
| Finance | Low | Accuracy focus, start with low-risk scenarios |
| HR | Low | Simple tools, emphasize assistance not replacement |
| Customer Service | Medium | High-frequency use cases, quick wins |
| Legal | Low | Expert involvement, human review required |
| Operations | Medium | Data-driven, show efficiency gains |

## License

MIT
