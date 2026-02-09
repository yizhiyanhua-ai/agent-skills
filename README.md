# Agent Skills Collection

这是一个精选的 Claude Agent Skills 集合，包含 5 个实用的技能包，帮助你在日常工作和生活中提升效率。

## 📦 技能列表

### 1. Meeting Minutes Secretary (会议纪要秘书)
自动整理会议记录，生成结构化的会议纪要。

**功能特点：**
- 从原始会议记录中提取关键信息
- 生成标准化的会议纪要格式
- 自动识别行动项和决策事项
- 支持多种会议记录格式

**使用场景：**
- 团队例会记录整理
- 项目讨论会纪要生成
- 客户沟通记录归档

📁 [查看详情](./meeting-minutes-secretary/)

---

### 2. Study Notes Organizer (学习笔记整理器)
智能整理学习笔记，构建知识体系。

**功能特点：**
- 自动提取笔记中的核心概念
- 生成知识点关联图谱
- 按主题分类整理笔记
- 生成复习清单

**使用场景：**
- 课程学习笔记整理
- 技术文档阅读笔记
- 读书笔记归纳总结

📁 [查看详情](./study-notes-organizer/)

---

### 3. Email Reply Assistant (邮件回复助手)
快速生成专业的邮件回复。

**功能特点：**
- 分析邮件内容和语气
- 生成符合场景的回复模板
- 支持多种语气风格（正式/友好/简洁）
- 自动检查礼貌用语

**使用场景：**
- 商务邮件回复
- 客户咨询回复
- 团队协作沟通

📁 [查看详情](./email-reply-assistant/)

---

### 4. Family Budget Manager (家庭预算管理器)
帮助家庭进行财务规划和预算管理。

**功能特点：**
- 记录和分类家庭支出
- 生成月度/年度财务报告
- 预算超支预警
- 消费趋势分析

**使用场景：**
- 家庭月度预算规划
- 消费记录追踪
- 财务健康度分析

📁 [查看详情](./family-budget-manager/)

---

### 5. Photo Organizer (照片整理器)
智能整理和分类照片，构建个人相册。

**功能特点：**
- 按时间/地点/事件自动分类
- 生成照片索引和标签
- 识别重复照片
- 创建相册目录结构

**使用场景：**
- 旅行照片整理
- 家庭相册归档
- 工作照片分类管理

📁 [查看详情](./photo-organizer/)

---

## 🚀 快速开始

### 安装方法

每个 Skill 都包含完整的目录结构：

```
skill-name/
├── SKILL.md          # Skill 定义文件
├── scripts/          # 辅助脚本
└── references/       # 参考文档
```

### 使用步骤

1. **选择需要的 Skill**
   ```bash
   cd skill-name
   ```

2. **查看 Skill 说明**
   ```bash
   cat SKILL.md
   ```

3. **在 Claude Code 中使用**
   - 将 Skill 目录复制到你的项目的 `.claude/skills/` 目录下
   - 在 Claude Code 中通过自然语言调用 Skill

### 示例

```bash
# 复制 Skill 到你的项目
cp -r meeting-minutes-secretary /path/to/your/project/.claude/skills/

# 在 Claude Code 中使用
"帮我整理这份会议记录"
```

---

## 📖 Skill 结构说明

每个 Skill 遵循标准的 Agent Skills 规范：

### SKILL.md
定义 Skill 的核心功能、使用方法和配置参数。

### scripts/
包含 Skill 运行所需的辅助脚本（如数据处理、格式转换等）。

### references/
存放参考文档、示例数据和模板文件。

---

## 🤝 贡献指南

欢迎贡献新的 Skills 或改进现有 Skills！

### 贡献步骤

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/new-skill`)
3. 提交更改 (`git commit -m 'feat: add new skill'`)
4. 推送到分支 (`git push origin feature/new-skill`)
5. 创建 Pull Request

### Skill 开发规范

- 遵循 [Agent Skills 标准](https://agentskills.io)
- 提供清晰的 SKILL.md 说明文档
- 包含使用示例和测试用例
- 确保脚本具有可执行权限

---

## 📝 许可证

本项目采用 MIT 许可证。详见 [LICENSE](./LICENSE) 文件。

---

## 🔗 相关资源

- [Agent Skills 官方网站](https://agentskills.io)
- [Claude Code 文档](https://claude.ai/docs)
- [一只烟花 AI 社区](https://github.com/yizhiyanhua-ai)

---

## 📧 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 [Issue](https://github.com/yizhiyanhua-ai/agent-skills/issues)
- 加入社区讨论

---

**Made with ❤️ by 一只烟花 AI 社区**
