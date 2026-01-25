# Skill 知识提取器

[🇬🇧 English](./README.md)

从对话记录、文档或工作经验中提取可复用的知识模式，帮助创建 Skill。

## 功能特点

- 分析对话记录（销售通话、客服聊天）
- 从工作文档和笔记中提取模式
- 自动生成 Skill 草稿
- 支持中英文双语

## 使用方法

```bash
# 分析对话文件
python scripts/extract_patterns.py --input chat.txt --type conversation

# 分析文档
python scripts/extract_patterns.py --input notes.md --type document

# 输出 JSON 格式
python scripts/extract_patterns.py --input data.txt --json
```

## 支持的模式类型

- **开场白模式** - 标准问候和介绍
- **问题诊断模式** - 发现问题的提问方式
- **异议处理模式** - 应对客户顾虑的话术
- **促成模式** - 成交技巧
- **检查清单模式** - 核查项目
- **模板模式** - 可复用的文档结构
- **决策树模式** - 条件判断逻辑
- **流程步骤模式** - 分步骤工作流

## 许可证

MIT
