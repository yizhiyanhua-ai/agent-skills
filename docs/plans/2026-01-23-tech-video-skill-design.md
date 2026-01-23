# Tech Video Skill 设计文档

**日期**: 2026-01-23
**状态**: 设计完成，待实现

## 概述

**tech-video-skill** 是一个基于 Manim 的 AI 技术解说视频生成器，专注于 AI 领域内容（Agent、大模型、产品分析等）。采用半自动辅助模式：AI 生成脚本和动画框架，用户可调整后渲染。

### 核心特性

| 维度 | 选择 |
|------|------|
| 领域 | AI（Agent、大模型、产品分析） |
| 自动化 | 半自动辅助 |
| 格式 | 横屏 16:9，5-15 分钟 |
| 风格 | 多风格可配置 |
| 配音 | 多模式（TTS/字幕/预留音轨） |
| Manim | 自动选择版本 |
| 组件 | 动态生成，不预置 |
| 流程 | 实时迭代预览 |

## 核心架构

### 工作流

```
用户描述 → 结构化脚本(YAML) → 逐场景 Manim 代码 → 实时预览 → 调整 → 最终渲染
     ↑                              ↓
     └──────── 迭代修改 ←───────────┘
```

### 目录结构

```
tech-video-skill/
├── SKILL.md                 # 入口文档
├── schemas/
│   └── script.schema.json   # 脚本结构定义
├── styles/                  # 风格模板
│   ├── 3b1b-classic/        # 3Blue1Brown 经典风格
│   ├── tech-modern/         # 科技感现代风
│   └── whiteboard/          # 手绘白板风
├── scripts/
│   ├── script_generator.py  # 脚本生成器
│   ├── manim_generator.py   # Manim 代码生成器
│   ├── preview_server.py    # 实时预览服务
│   └── renderer.py          # 最终渲染器
├── components/              # 可复用动画组件（按需生成）
└── .sessions/               # 会话状态
```

### 输出目录

- 默认：当前工作目录下
- 可指定：用户可通过参数指定任意输出目录

## 脚本结构

视频内容用 YAML 格式描述，便于 AI 生成和用户编辑：

```yaml
# script.yaml 示例
meta:
  title: "理解 Transformer 注意力机制"
  duration: 480  # 目标时长（秒）
  style: "3b1b-classic"
  output_dir: "./my-videos"  # 可选，默认当前目录
  voice:
    mode: "tts"  # tts | subtitle | none
    engine: "edge-tts"
    voice_id: "zh-CN-YunxiNeural"

scenes:
  - id: "intro"
    title: "开场"
    duration: 30
    narration: "今天我们来聊聊 Transformer 中最核心的概念..."
    animations:
      - type: "title_card"
        text: "注意力机制"
      - type: "fade_in"
        elements: ["subtitle"]

  - id: "qkv_explain"
    title: "Q、K、V 的含义"
    duration: 90
    narration: "Query、Key、Value 这三个向量..."
    animations:
      - type: "vector_space"
        vectors: ["Q", "K", "V"]
        show_labels: true
      - type: "matrix_multiply"
        left: "Q"
        right: "K^T"
```

## 风格模板系统

每个风格定义颜色、字体、动画参数：

```
styles/
├── 3b1b-classic/
│   ├── config.yaml      # 颜色、字体配置
│   ├── animations.py    # 风格特定动画
│   └── preview.png      # 风格预览图
├── tech-modern/
└── whiteboard/
```

**3b1b-classic 配置示例**：

```yaml
colors:
  background: "#1e1e1e"
  primary: "#58c4dd"
  secondary: "#83c167"
  text: "#ffffff"
fonts:
  title: "CMU Serif"
  body: "Source Sans Pro"
  math: "CMU Math"
animation:
  default_run_time: 1.0
  fade_duration: 0.5
```

## 工作流程详解

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户输入                                  │
│  "做一个讲解 Transformer 注意力机制的视频"                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: 脚本生成                                                │
│  - AI 分析主题，生成结构化脚本 (YAML)                             │
│  - 输出: script.yaml                                            │
│  - 用户可编辑脚本内容、调整场景顺序                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: 逐场景代码生成 + 实时预览                               │
│  - 按场景生成 Manim 代码                                         │
│  - 每个场景生成后立即预览（静态帧或短动画）                        │
│  - 用户可以：                                                    │
│    • "这个场景 OK" → 继续下一个                                  │
│    • "调整一下..." → 修改后重新生成                              │
│    • "跳过预览" → 批量生成所有场景                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: 最终渲染                                                │
│  - 合并所有场景                                                  │
│  - 添加配音/字幕（根据配置）                                      │
│  - 输出: {title}_{resolution}.mp4                               │
└─────────────────────────────────────────────────────────────────┘
```

### 交互命令

| 命令 | 作用 |
|------|------|
| `预览 scene-id` | 预览指定场景 |
| `修改 scene-id` | 进入场景编辑模式 |
| `重新生成 scene-id` | 重新生成指定场景 |
| `跳过预览` | 批量生成剩余场景 |
| `渲染` | 开始最终渲染 |
| `导出脚本` | 导出当前脚本为 YAML |
| `切换风格 style-name` | 更换视觉风格 |

### 会话状态管理

```
.sessions/
└── {session-id}/
    ├── script.yaml          # 当前脚本
    ├── scenes/              # 生成的场景代码
    │   ├── intro.py
    │   ├── qkv_explain.py
    │   └── ...
    ├── previews/            # 预览图/视频
    └── state.json           # 会话状态
```

## Manim 代码生成策略

### 双版本支持策略

| 场景类型 | 推荐版本 | 原因 |
|----------|----------|------|
| 简单图形、文字动画 | ManimCE | 稳定、文档完善 |
| 复杂 3D、实时交互 | ManimGL | 性能更好、支持实时预览 |
| 混合场景 | ManimCE 优先 | 兼容性更好 |

### 代码生成模板

```python
# scene_intro.py - 自动生成
from manim import *
from tech_video_skill.styles import load_style

class SceneIntro(Scene):
    """开场动画 - 自动生成于 2026-01-23"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.style = load_style("3b1b-classic")

    def construct(self):
        # 标题卡片
        title = Text("注意力机制", font_size=72)
        title.set_color(self.style.colors.primary)

        subtitle = Text("Transformer 的核心", font_size=36)
        subtitle.set_color(self.style.colors.secondary)
        subtitle.next_to(title, DOWN)

        # 动画序列
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle), run_time=0.8)
        self.wait(1)
```

### AI 动态生成组件

不预置组件库，而是让 AI 根据内容动态生成。AI 会参考：

1. **Manim 官方文档** - 基础 API 和动画类型
2. **3b1b/videos 仓库** - 高质量动画实现参考
3. **AI 领域可视化惯例** - 神经网络、数据流等常见表示方法

## 配音系统

### 配音模式

| 模式 | 说明 | 实现 |
|------|------|------|
| `tts` | AI 语音合成 | Edge TTS / OpenAI TTS |
| `subtitle` | 纯字幕显示 | Manim Text 动画 |
| `none` | 预留音轨 | 导出时间轴 JSON，用户自行录制 |

**TTS 配置示例**：

```yaml
voice:
  mode: "tts"
  engine: "edge-tts"        # edge-tts | openai
  voice_id: "zh-CN-YunxiNeural"
  speed: 1.0
  output_format: "mp3"
```

**时间轴导出格式**（mode: none）：

```json
{
  "scenes": [
    {"id": "intro", "start": 0, "end": 30, "narration": "今天我们来聊聊..."},
    {"id": "qkv_explain", "start": 30, "end": 120, "narration": "Query、Key、Value..."}
  ]
}
```

## 最终渲染流程

```
┌─────────────────────────────────────────────────────────────┐
│  渲染准备                                                    │
│  - 验证所有场景代码已生成                                     │
│  - 检查风格配置完整性                                         │
│  - 确认输出目录可写                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  场景渲染（可并行）                                          │
│  - 每个场景独立渲染为视频片段                                 │
│  - 输出: .sessions/{id}/renders/scene_*.mp4                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  音频处理                                                    │
│  - TTS 模式: 生成语音并对齐                                   │
│  - Subtitle 模式: 跳过                                       │
│  - None 模式: 导出时间轴                                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  合成输出                                                    │
│  - FFmpeg 合并视频片段                                       │
│  - 混合音频轨道                                              │
│  - 输出: {output_dir}/{title}_1920x1080.mp4                 │
└─────────────────────────────────────────────────────────────┘
```

### 输出规格

| 参数 | 默认值 |
|------|--------|
| 分辨率 | 1920x1080 (16:9) |
| 帧率 | 60fps |
| 编码 | H.264 |
| 音频 | AAC 192kbps |

## 依赖与配置

### 系统依赖

```bash
# Python 环境（推荐 3.10+）
pip install manim manimgl pyyaml edge-tts ffmpeg-python

# 或使用 ManimCE
pip install manim

# FFmpeg（视频合成必需）
brew install ffmpeg  # macOS
```

### Skill 依赖

```yaml
dependencies:
  - zimage-skill      # AI 图像生成（可选）
```

### 首次配置流程

```
用户: "/tech-video" 或 "做一个讲解 xxx 的技术视频"

AI: 检测到首次使用，正在检查环境...

┌─────────────────────────────────────────────────────────────┐
│  环境检查                                                    │
│  ✓ Python 3.10.12                                           │
│  ✗ Manim 未安装                                              │
│  ✓ FFmpeg 5.1.2                                             │
│                                                             │
│  需要安装: pip install manim pyyaml edge-tts                 │
│  是否自动安装？[Y/n]                                         │
└─────────────────────────────────────────────────────────────┘
```

## 使用示例

```
用户: "做一个讲解 AI Agent 工作原理的技术视频"

AI: 正在分析主题，生成视频脚本...

┌─────────────────────────────────────────────────────────────┐
│  📝 脚本生成完成                                             │
│                                                             │
│  标题: AI Agent 工作原理                                     │
│  预计时长: 8 分钟                                            │
│  风格: 3b1b-classic                                         │
│  场景数: 6                                                   │
│                                                             │
│  场景列表:                                                   │
│  1. intro (30s) - 开场：什么是 AI Agent                      │
│  2. perception (90s) - 感知：Agent 如何理解环境              │
│  3. reasoning (120s) - 推理：LLM 作为大脑                    │
│  4. action (90s) - 行动：工具调用与执行                      │
│  5. memory (90s) - 记忆：上下文与长期记忆                    │
│  6. outro (30s) - 总结与展望                                 │
│                                                             │
│  [查看完整脚本] [修改脚本] [开始生成]                         │
└─────────────────────────────────────────────────────────────┘

用户: "开始生成"

AI: 正在生成场景 1/6: intro...

┌─────────────────────────────────────────────────────────────┐
│  🎬 场景预览: intro                                          │
│                                                             │
│  [预览图/动画]                                               │
│                                                             │
│  ✓ 标题动画: "AI Agent 工作原理"                             │
│  ✓ 副标题淡入: "从感知到行动"                                │
│                                                             │
│  [OK] [重新生成] [修改]                                      │
└─────────────────────────────────────────────────────────────┘

用户: "OK"

AI: 正在生成场景 2/6: perception...
```

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| Manim 未安装 | 提示安装命令，询问是否自动安装 |
| 渲染失败 | 显示错误日志，提供修复建议 |
| 脚本格式错误 | 高亮错误位置，提供修正示例 |
| 风格模板缺失 | 回退到默认风格，提示用户 |
| FFmpeg 缺失 | 提示安装，无法合成时导出单独场景 |

## SKILL.md 入口文档

```markdown
---
name: tech-video-skill
description: |
  基于 Manim 的 AI 技术解说视频生成器。支持多种视觉风格，
  半自动脚本生成，实时预览，高质量渲染输出。
  触发方式: "做技术视频", "讲解视频", "tech video", "/tech-video"
dependencies:
  - zimage-skill
---

# Tech Video Skill - AI 技术解说视频生成器

用自然语言描述你想讲解的 AI 技术概念，自动生成高质量的 Manim 动画视频。

## 功能特点

- **AI 领域专注** - 针对 Agent、大模型、产品分析等内容优化
- **多风格模板** - 3b1b 经典、科技现代、手绘白板
- **半自动流程** - AI 生成初稿，用户可调整
- **实时预览** - 逐场景预览，快速迭代
- **多配音模式** - TTS / 字幕 / 预留音轨

## 快速开始

"做一个讲解 Transformer 注意力机制的技术视频"

## 可用风格

| 风格 | 说明 |
|------|------|
| `3b1b-classic` | 深色背景，流畅几何动画 |
| `tech-modern` | 明亮科技感，数据流效果 |
| `whiteboard` | 手绘白板风格 |

## 输出规格

- 分辨率: 1920x1080 (16:9)
- 帧率: 60fps
- 格式: MP4 (H.264)
```

## 技术选型总结

| 模块 | 技术选型 |
|------|----------|
| 脚本格式 | YAML 结构化脚本 |
| 动画引擎 | Manim (CE/GL 自动选择) |
| 配音 | Edge TTS / OpenAI TTS |
| 视频合成 | FFmpeg |
| 风格系统 | YAML 配置 + Python 动画模块 |
