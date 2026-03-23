---
name: mv-skill
description: |
  Use this skill WHENEVER the user wants to create a music video, MV, short video, video clip, or animated video
  with music. This is the go-to skill for any video creation request involving music, style templates, or visual
  storytelling. It produces a commercial-quality MP4 (9:16 vertical, 50-60s) using Remotion + AI music generation.

  TRIGGER on phrases like:
  - 制作MV / 生成MV / 做一个音乐视频 / 帮我做个MV / 做视频 / 做一支MV
  - create a music video / make an MV / generate a music video / make a video clip
  - 热血风格视频 / 赛博朋克MV / 抒情MV / 动漫风视频
  - anime MV / cyberpunk video / lyric video / hype video
  - /mv

  DO NOT use this for: static image generation (use zimage-skill), plain screen recordings,
  or documentaries with no music.

  ALWAYS prefer this skill over manual Remotion coding when the user just wants a finished video.
dependencies:
  - remotion-best-practices
  - zimage-skill
  - media-downloader
---

# MV Skill - 动感短视频生成器

你只需描述主题和风格，这个 skill 会自动完成：AI 音乐生成、智能分镜规划、素材获取、Remotion 渲染，最终输出一个商业级 MP4 文件。

---

## 快速决策：什么时候用这个 Skill？

| 场景 | 用 mv-skill？ |
|------|:---:|
| 用户要做 MV / 音乐视频 / 动感短片 | YES |
| 用户有主题/歌词/风格偏好 | YES |
| 用户提供了本地音乐文件 | YES |
| 用户只要生成图片 | NO，用 zimage-skill |
| 用户要录屏 / 教程视频 | NO |
| 用户要纯文字动画 | NO |

---

## 功能特点

- **多风格模板** - 热血动漫、赛博朋克、抒情 MV
- **AI 音乐生成** - 集成 Suno，自动生成配乐；也支持本地 MP3
- **智能素材获取** - 素材库（Pexels/Pixabay）优先，AI 生成兜底
- **可视化分镜预览** - 渲染前确认每一个镜头，支持逐镜修改
- **短视频优化** - 9:16 竖屏，50-60 秒，适配抖音/Reels/Shorts

---

## Agent 行为步骤

当触发 mv-skill 时，agent 应按以下步骤执行：

1. **理解需求** - 提取用户描述中的：主题、风格、时长偏好、是否有本地音乐
2. **选择模板** - 根据风格关键词匹配最合适的模板（见下方模板表）
3. **生成分镜脚本** - 调用 `storyboard_generator.py` 生成场景列表
4. **获取/生成音乐** - 优先使用用户提供的音乐；否则调用 Suno API 生成；失败则使用占位音频
5. **获取素材** - 调用 `asset_manager.py` 从素材库下载图片/视频片段
6. **展示分镜预览** - 以文字表格形式展示各场景（场景名、时长、描述、素材）
7. **等待确认** - 询问用户是否确认，或需要修改哪个场景
8. **渲染输出** - 用户确认后调用 `renderer.py`，输出 MP4 到 `output/` 目录
9. **报告结果** - 告知输出文件路径，提示可以进一步修改

> 如果用户在初始描述中已经足够清晰，可以跳过第 7 步直接渲染，渲染完成后展示结果。

---

## 快速开始

### 最简用法

```
"帮我做一个热血风格的 MV，主题是宇宙战士"
```

### 指定更多细节

```
"制作一个赛博朋克风格的 MV
 主题：霓虹都市的孤独黑客
 歌词：在数据的海洋里漂流
 时长：55 秒"
```

### 使用本地音乐

```
"用我的音乐文件 /tmp/my_song.mp3 做一个抒情 MV，歌词是'代码里寻找诗意'"
```

---

## 可用风格模板

| 风格 | 模板 ID | 关键词 | 适合场景 |
|------|---------|--------|---------:|
| 热血动漫 | `anime-hype` | 热血、动漫、燃、战斗、励志 | 战斗、励志、运动 |
| 赛博朋克 | `cyberpunk` | 赛博、科技、霓虹、未来、黑客 | 科幻、电子音乐 |
| 抒情 MV | `lyric` | 抒情、唯美、治愈、情歌、慢歌 | 情歌、慢歌、叙事 |

---

## 工作流程示例

### 示例 1：热血动漫风

```
用户: "做一个圣斗士星矢风格的 MV，主题是小宇宙觉醒"

AI: 正在生成分镜预览...

┌─────────────────────────────────────────────┐
│ 分镜预览 - 小宇宙觉醒                         │
├────────┬──────┬────────────────────────────┤
│ 场景   │ 时长 │ 描述                         │
├────────┼──────┼────────────────────────────┤
│ 标题   │ 5s   │ 片名特效，粒子爆炸            │
│ 战士登场│ 10s  │ 主角剪影，逆光慢镜头          │
│ 蓄力   │ 15s  │ 能量聚集，环境震动            │
│ 爆发   │ 15s  │ 全力爆发，高速剪辑            │
│ 升华   │ 10s  │ 胜利定格，慢动作             │
│ 结尾   │ 5s   │ 片尾 Logo                  │
└────────┴──────┴────────────────────────────┘

确认开始渲染？[确认 / 修改 Scene X / 重新生成]

用户: "确认"

AI: 渲染完成！
输出: ~/.claude/skills/mv-skill/output/小宇宙觉醒_1080x1920.mp4
```

### 示例 2：逐镜修改

```
用户: "修改 Scene 3，换成我自己的图片 hero.png"

AI: 已更新 Scene 3 素材为 hero.png，预览已刷新。是否重新渲染？
```

### 示例 3：使用本地音乐

```
用户: "使用这个音乐文件 /path/to/music.mp3 制作 MV"

AI: 已检测音乐 BPM: 128，时长: 58秒，正在生成匹配的分镜...
```

---

## 首次配置

### 必需依赖

```bash
# 安装 Remotion 依赖
cd ~/.claude/skills/mv-skill/remotion && npm install

# 安装 Python 依赖
pip install requests librosa pydub pyyaml pillow
```

### API Keys（按需配置）

```bash
# 写入 ~/.zshrc 或 ~/.bashrc
export SUNO_API_KEY="your_key"      # AI 音乐生成（可选）
export PEXELS_API_KEY="your_key"    # 高质量素材（推荐）
export PIXABAY_API_KEY="your_key"   # 备用素材源（可选）
```

---

## 输出位置

```
~/.claude/skills/mv-skill/output/
└── {标题}_{分辨率}.mp4
```

---

## 常见问题

**Q: 音乐生成失败怎么办？**
A: 上传本地 MP3 文件代替：`"使用这个音乐文件 /path/to/music.mp3"`

**Q: 素材质量不满意？**
A: 在预览阶段说 `"Scene 2 换一张"` 或提供自己的素材路径

**Q: 渲染太慢？**
A: 首次渲染需要下载 npm 依赖（约 1-2 分钟），后续会快很多

**Q: 如何添加自定义歌词？**
A: 在描述中包含歌词，如 `"歌词：燃烧吧小宇宙"`

**Q: 支持横屏吗？**
A: 当前默认 9:16 竖屏（1080x1920）；如需横屏请在描述中说明

---

## 技术架构

```
mv-skill/
├── SKILL.md              # 本文档
├── evals/                # 测试用例
│   └── evals.json
├── templates/            # MV 风格模板
│   ├── anime-hype/       # 热血动漫风（template.yaml + 素材配置）
│   ├── cyberpunk/        # 赛博朋克风
│   └── lyric/            # 抒情风
├── schemas/              # 分镜脚本 JSON Schema
├── scripts/              # 核心 Python 脚本
│   ├── cli.py            # 入口：解析用户输入，协调各模块
│   ├── storyboard_generator.py  # 生成分镜脚本
│   ├── asset_manager.py  # 素材获取（素材库 + AI 生成）
│   ├── music_generator.py       # Suno AI 音乐生成
│   ├── music_analyzer.py        # 本地音乐 BPM/时长分析
│   └── renderer.py       # 调用 Remotion 渲染输出 MP4
└── remotion/             # Remotion 项目（TypeScript/React）
    ├── src/
    │   ├── Root.tsx       # 注册所有 Composition
    │   ├── compositions/  # 各风格 Composition
    │   └── components/    # 可复用场景组件
    └── package.json
```

### 数据流

```
用户描述
  → cli.py（参数解析）
  → storyboard_generator.py（生成分镜 JSON）
  → asset_manager.py（素材获取）+ music_generator.py（音乐生成）
  → [用户确认分镜]
  → renderer.py → Remotion CLI
  → output/*.mp4
```

---

## 依赖的 Skills

- `remotion-best-practices` - Remotion 视频制作知识库
- `zimage-skill` - AI 图像生成（素材兜底）
- `media-downloader` - 素材库下载（Pexels/Pixabay）
