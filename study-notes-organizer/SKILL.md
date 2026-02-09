---
name: study-notes-organizer
description: 将课程录音、手写笔记、网页资料整理为结构化学习笔记。支持音频转录、OCR识别、知识点提取、思维导图生成。当用户提供学习材料并要求"整理笔记"、"生成学习笔记"、"制作复习资料"时触发。
argument-hint: "[学习材料路径或内容]"
---

# 学习笔记整理助手

将多种形式的学习材料（录音、手写笔记、网页文章）转换为结构化、可复习的学习笔记。

## 核心功能

| 功能 | 说明 | 适用场景 |
|------|------|----------|
| 音频转录 | 使用 Whisper 将课程录音转为文本 | MP3/M4A/WAV 格式录音 |
| OCR 识别 | 使用 Tesseract 识别手写笔记 | JPG/PNG 格式图片 |
| 网页提取 | 使用 WebFetch 提取在线文章 | 学习资料链接 |
| 知识提取 | 自动识别概念、方法、公式 | 所有文本内容 |
| 结构化输出 | 生成 Markdown 格式笔记 | 所有场景 |
| 复习材料 | 生成闪卡和思维导图 | 需要复习的内容 |

## 使用流程

### 场景一：处理课程录音

```
用户: "整理这个课程录音"
      [提供音频文件路径]

Step 1: 检查音频格式
        支持: MP3, M4A, WAV, FLAC

Step 2: 调用转录脚本
        python scripts/process_study_material.py --audio <音频文件>

Step 3: 提取知识点
        识别：核心概念、方法步骤、重点难点

Step 4: 生成结构化笔记
        输出格式：Markdown
```

### 场景二：处理手写笔记

```
用户: "整理这些手写笔记照片"
      [提供图片文件]

Step 1: OCR 识别
        tesseract <图片文件> output --lang chi_sim+eng

Step 2: 文本清理
        去除识别错误、格式化内容

Step 3: 知识点提取
        同场景一

Step 4: 生成笔记
```

### 场景三：处理网页文章

```
用户: "整理这篇文章 [URL]"

Step 1: 提取网页内容
        WebFetch <URL>

Step 2: 去噪处理
        移除广告、导航等无关内容

Step 3: 知识点提取

Step 4: 生成笔记
```

## 知识点提取规则

### 核心概念识别

**关键词触发**：
- 定义、概念、术语
- "什么是"、"指的是"
- 专业名词（首次出现）

**提取格式**：
```markdown
### 核心概念

**概念名称**：定义说明
- 关键特征：...
- 应用场景：...
- 示例：...
```

### 方法步骤识别

**关键词触发**：
- 步骤、流程、方法
- 第一步、首先、然后
- 数字序号（1. 2. 3.）

**提取格式**：
```markdown
### 方法步骤

1. **步骤一**：说明
2. **步骤二**：说明
3. **步骤三**：说明
```

### 公式定理识别

**识别模式**：
- 数学公式（包含 =、+、-、×、÷）
- 化学方程式（包含 →、↔）
- 物理公式（包含单位）

**提取格式**：
```markdown
### 公式定理

**公式名称**：`公式内容`
- 变量说明：...
- 应用场景：...
```

### 示例代码识别

**识别模式**：
- 代码块标记（```）
- 缩进的代码段
- 包含编程关键字

**提取格式**：
```markdown
### 示例代码

\`\`\`python
# 代码示例
def example():
    pass
\`\`\`

**说明**：...
```

## 输出格式

### 标准笔记模板

```markdown
---
主题: [课程/主题名称]
学科: [领域分类]
日期: [YYYY-MM-DD]
来源: [录音/手写/网页]
标签: [tag1, tag2, tag3]
---

# [主题名称] 学习笔记

## 核心摘要

[用 3-5 句话总结本次学习的核心内容]

**最重要的 3 个知识点**：
1. [知识点1]
2. [知识点2]
3. [知识点3]

## 详细内容

### 1. [主题模块1]

#### 1.1 核心概念

**概念名称**：定义说明
- 关键特征：...
- 应用场景：...

#### 1.2 方法步骤

1. 步骤一：...
2. 步骤二：...

#### 1.3 示例

[具体示例]

### 2. [主题模块2]

...

## 思维导图

\`\`\`mermaid
graph TD
    A[主题] --> B[子主题1]
    A --> C[子主题2]
    B --> D[知识点1.1]
    B --> E[知识点1.2]
\`\`\`

## 复习清单

### 概念理解
- [ ] Q: 什么是 XXX？
  - A: [答案]
  
- [ ] Q: XXX 的应用场景是什么？
  - A: [答案]

### 实践操作
- [ ] 能否独立完成 XXX 操作？
- [ ] 能否解释 XXX 的原理？

## 关联笔记

- [[前置知识：XXX]]
- [[延伸阅读：YYY]]
- [[实践项目：ZZZ]]

## 待深入研究

- [ ] 深入研究 XXX 的底层原理
- [ ] 阅读论文：[论文标题]
- [ ] 实践项目：[项目描述]

---

**原始材料**: [原始文件路径]  
**生成时间**: YYYY-MM-DD HH:MM  
**工具**: Claude Code (study-notes-organizer)
```

## 辅助脚本

### scripts/process_study_material.py

**功能**：多模态学习材料处理

**使用方法**：
```bash
# 处理音频
python scripts/process_study_material.py --audio lecture.mp3

# 处理图片
python scripts/process_study_material.py --images notes_*.jpg

# 处理网页
python scripts/process_study_material.py --url https://example.com/article

# 组合处理
python scripts/process_study_material.py --audio lecture.mp3 --images notes_*.jpg --output notes.md
```

### scripts/generate_flashcards.py

**功能**：从笔记生成 Anki 闪卡

**使用方法**：
```bash
python scripts/generate_flashcards.py notes.md -o flashcards.txt
```

**输出格式**：Anki 导入格式（问题;答案;标签）

## 特殊场景处理

### 场景1：多次课程的连续笔记

```
用户: "这是第3次课的录音，请关联前2次的笔记"

处理方式:
1. Read 前2次笔记
2. 识别知识点延续关系
3. 在新笔记中添加"前置知识"引用
4. 更新知识图谱
```

### 场景2：考试复习模式

```
用户: "生成期末考试复习资料"

处理方式:
1. Read 本学期所有笔记
2. 提取标记为"重点"的内容
3. 生成考点清单
4. 生成模拟题
5. 生成复习时间表
```

## 依赖要求

**Python 包**：
```bash
pip install openai-whisper
pip install pytesseract
pip install Pillow
```

**系统工具**：
```bash
# macOS
brew install tesseract
brew install tesseract-lang  # 中文支持

# Ubuntu
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim
```

## 故障排查

### 问题1: OCR 识别率低

**症状**: 手写笔记识别错误多

**解决方案**:
1. 确保照片清晰、光线充足
2. 使用更高分辨率的图片
3. 手动校对识别结果
4. 标注"需人工校对"

### 问题2: 音频转录失败

**症状**: Whisper 转录报错

**解决方案**:
1. 检查 Whisper 是否正确安装
2. 检查音频文件格式
3. 尝试使用较小的模型（base/small）

### 问题3: 知识点提取不准确

**症状**: 提取的知识点不是重点

**解决方案**:
1. 手动标注重点内容
2. 使用"重要"、"核心"等关键词
3. 人工补充和调整

## 质量检查清单

生成笔记后，执行以下检查：

- [ ] **完整性**: 所有重要知识点都已记录
- [ ] **准确性**: 概念定义准确无误
- [ ] **结构化**: 层级清晰（2-3 层）
- [ ] **可复习**: 包含复习清单
- [ ] **可搜索**: 标签准确（便于检索）
- [ ] **可关联**: 标注了前置知识和延伸阅读

## 使用示例

### 示例1: 处理课程录音

```
用户: "整理这个 Python 课程录音 /path/to/lecture.mp3"

AI 执行:
1. python scripts/process_study_material.py --audio /path/to/lecture.mp3
2. 提取知识点（函数、类、模块）
3. 生成结构化笔记
4. 生成思维导图
5. Write Python_基础_学习笔记_2026-02-09.md
```

### 示例2: 处理手写笔记

```
用户: "整理这些数学笔记照片"
      [提供 3 张照片]

AI 执行:
1. OCR 识别 3 张照片
2. 合并识别结果
3. 提取公式和定理
4. 生成结构化笔记
5. 标注"需人工校对公式"
```

### 示例3: 综合整理

```
用户: "整理这周的学习材料"
      [提供录音 + 笔记照片 + 网页链接]

AI 执行:
1. 并行处理所有材料
2. 合并提取的知识点
3. 按主题分类整理
4. 生成综合笔记
5. 生成本周复习清单
```

## 参考资料

- 笔记方法论: [references/note_taking_methods.md](references/note_taking_methods.md)
- 笔记模板: [references/markdown_templates.md](references/markdown_templates.md)
- 处理脚本: [scripts/process_study_material.py](scripts/process_study_material.py)
- 闪卡生成: [scripts/generate_flashcards.py](scripts/generate_flashcards.py)

## 注意事项

1. **OCR 准确性**: 手写识别可能有误，生成后需人工校对
2. **公式处理**: 复杂数学公式建议保留原图
3. **代码格式**: 确保代码块语法高亮正确
4. **版权问题**: 网页内容仅供个人学习，不得商用
5. **隐私保护**: 笔记中的个人信息自动脱敏
