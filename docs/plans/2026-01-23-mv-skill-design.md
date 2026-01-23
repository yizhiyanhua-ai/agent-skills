# MV Skill 设计文档

> 基于 Remotion 的动感 MV 短视频生成器

## 概述

创建一个专门用于生成动感 MV 短视频的 Claude Code Skill，达到类似《圣斗士星矢》片头动画的商业化水准。

## 需求总结

| 维度 | 选择 |
|------|------|
| 使用场景 | 商业用途 |
| 制作流程 | 模板驱动 |
| 风格模板 | 2-3 个核心风格，可扩展 |
| 输出规格 | 9:16 竖屏，50-60 秒 |
| 音乐来源 | AI 生成（Suno） |
| 视觉素材 | 混合模式（素材库优先 + AI 生成兜底） |
| 交互方式 | 分镜预览 → 确认 → 渲染 |

## 依赖的 Skills

- `remotion-best-practices` - Remotion 视频制作最佳实践
- `zimage-skill` - AI 图像生成（ModelScope Z-Image-Turbo）
- `media-downloader` - 从 Pexels/Pixabay/YouTube 下载素材
- Suno API - AI 音乐生成

---

## 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        MV Skill 工作流                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  输入    │ -> │ 分镜生成  │ -> │  预览    │ -> │  渲染    │  │
│  │  阶段    │    │  阶段    │    │  阶段    │    │  阶段    │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │              │               │               │          │
│       v              v               v               v          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │ 主题描述  │   │ Storyboard│   │ 分镜预览图│   │ 最终视频  │    │
│  │ 风格选择  │   │   JSON   │   │ (静态)   │   │ (MP4)   │    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                        依赖的 Skills                             │
├──────────┬──────────┬──────────┬──────────────────────────────┤
│ zimage   │ media-   │ remotion │ Suno API                      │
│ -skill   │ downloader│ -best-   │ (音乐生成)                    │
│ (AI图像) │ (素材库) │ practices│                               │
└──────────┴──────────┴──────────┴──────────────────────────────┘
```

### 核心文件结构

```
mv-skill/
├── SKILL.md              # 技能说明文档
├── templates/            # MV 风格模板
│   ├── anime-hype/       # 热血动漫风
│   ├── cyberpunk/        # 赛博朋克风
│   └── lyric/            # 抒情风
├── schemas/              # 分镜脚本 Schema
│   └── storyboard.schema.json
├── scripts/              # 核心脚本
│   ├── cli.py                    # 主入口
│   ├── storyboard_generator.py   # 分镜生成
│   ├── music_generator.py        # Suno API 集成
│   ├── asset_manager.py          # 素材获取与管理
│   ├── preview_generator.py      # 分镜预览图生成
│   └── renderer.py               # Remotion 渲染调度
└── remotion/             # Remotion 项目
    ├── src/
    │   ├── compositions/       # 视频组合
    │   └── components/         # 可复用组件
    └── package.json
```

---

## 分镜脚本 Schema

```yaml
# storyboard.yaml 示例
meta:
  title: "星辰之战"
  style: "anime-hype"        # 模板风格
  duration: 55               # 总时长(秒)
  resolution: "1080x1920"    # 9:16 竖屏
  fps: 30

music:
  source: "suno"             # 音乐来源
  prompt: "epic anime battle, orchestral, intense drums, 120bpm"
  file: null                 # 生成后填充路径

scenes:
  - id: "intro"
    start: 0
    end: 5
    type: "title"            # 镜头类型：title/action/transition/lyrics
    content:
      text: "星辰之战"
      subtitle: "BATTLE OF STARS"
    visual:
      source: "auto"         # auto | ai | stock | user
      prompt: "cosmic explosion, stars forming, epic scale, anime style"
      stock_keywords: ["cosmic", "explosion", "stars"]
      quality_priority: "high"
      allow_ai_fallback: true
      file: null
    animation: "zoom-in"     # 预设动画
    transition: "flash"      # 转场效果

  - id: "verse1_shot1"
    start: 5
    end: 10
    type: "action"
    content:
      lyrics: "燃烧吧，小宇宙"
    visual:
      source: "auto"
      prompt: "anime warrior powering up, golden aura, dynamic pose"
      stock_keywords: ["warrior", "energy", "power"]
      quality_priority: "high"
      file: null
    animation: "shake"
    beat_sync: true          # 是否同步节拍
```

### 关键字段说明

| 字段 | 说明 |
|------|------|
| `type` | 镜头类型决定渲染逻辑（标题/动作/转场/歌词） |
| `visual.source` | 素材来源：auto（智能选择）、ai、stock、user |
| `animation` | 预设动画效果，映射到 Remotion 组件 |
| `beat_sync` | 标记需要与音乐节拍同步的镜头 |
| `transition` | 镜头间转场效果 |
| `quality_priority` | 素材质量优先级：high/medium/low |

### 预设动画效果

- `zoom-in` / `zoom-out` - 推拉镜头
- `pan-left` / `pan-right` - 横移
- `shake` - 震动（适合冲击感）
- `flash` - 闪白
- `ken-burns` - 缓慢推移（适合静态图）
- `speed-lines` - 速度线效果

---

## 风格模板系统

### 模板 1：热血动漫风 (anime-hype)

```yaml
name: "anime-hype"
description: "类似《圣斗士星矢》《火影忍者》OP 的热血风格"

visual_style:
  color_palette:
    primary: "#FF4500"       # 热血橙红
    secondary: "#FFD700"     # 金色光芒
    accent: "#1E90FF"        # 能量蓝
    background: "#0D0D0D"    # 深黑底

  ai_prompt_suffix: "anime style, dynamic lighting, vibrant colors, cel-shaded"
  stock_keywords: ["anime", "particles", "energy", "explosion"]

rhythm:
  bpm_range: [120, 160]
  scene_duration:
    min: 2
    max: 5
    avg: 3
  beat_sync_ratio: 0.7

animations:
  preferred: ["zoom-in", "shake", "flash", "speed-lines"]
  intensity: "high"

transitions:
  preferred: ["flash", "wipe-diagonal", "impact-frame"]
  duration: 0.3

structure:
  sections:
    - type: "intro"
      duration: 5
      description: "标题展示，宇宙/能量背景"
    - type: "buildup"
      duration: 15
      description: "角色/场景快速切换"
    - type: "climax"
      duration: 20
      description: "高潮段落，密集剪辑，特效叠加"
    - type: "bridge"
      duration: 10
      description: "情感段落，节奏稍缓"
    - type: "finale"
      duration: 5
      description: "终结pose，标题再现"
```

### 模板概览

| 模板 | 色调 | 节奏 | 典型动画 | 转场风格 |
|------|------|------|---------|---------|
| **anime-hype** | 橙红/金/蓝 | 120-160 BPM | shake、speed-lines | flash、冲击帧 |
| **cyberpunk** | 霓虹粉/青 | 100-130 BPM | 故障效果、扫描线 | 数据流、像素化 |
| **lyric** | 柔和渐变 | 70-100 BPM | ken-burns、淡入淡出 | 溶解、模糊过渡 |

---

## 工作流程详解

### 阶段 1：输入收集

```
用户输入示例：
"帮我做一个热血风格的 MV，主题是宇宙战士觉醒，歌词是'燃烧吧小宇宙，奇迹终将降临'"
```

解析提取：
- 风格：anime-hype
- 主题：宇宙战士觉醒
- 关键歌词：燃烧吧小宇宙，奇迹终将降临
- 时长：默认 55 秒

### 阶段 2：并行生成

```
┌─────────────────────────────────────────────────┐
│              并行执行（提升效率）                  │
├─────────────────┬───────────────────────────────┤
│  ┌───────────┐  │  ┌───────────────────────┐   │
│  │ Suno API  │  │  │    分镜脚本生成        │   │
│  │ 生成音乐   │  │  │  (基于模板 + 主题)    │   │
│  └─────┬─────┘  │  └───────────┬───────────┘   │
│        │        │              │               │
│        v        │              v               │
│  ┌───────────┐  │  ┌───────────────────────┐   │
│  │ 节拍分析   │─────>│    节拍对齐优化       │   │
│  │ (BPM检测) │  │  │  (调整镜头切点)       │   │
│  └───────────┘  │  └───────────────────────┘   │
└─────────────────┴───────────────────────────────┘
```

### 阶段 3：分镜预览

```
┌──────────────────────────────────────────────────────────┐
│  分镜预览板 - 星辰之战                                     │
├──────────┬──────────┬──────────┬──────────┬──────────────┤
│ Scene 1  │ Scene 2  │ Scene 3  │ Scene 4  │ Scene 5      │
│ 0:00-0:05│ 0:05-0:10│ 0:10-0:15│ 0:15-0:20│ 0:20-0:25    │
│ ┌──────┐ │ ┌──────┐ │ ┌──────┐ │ ┌──────┐ │ ┌──────┐     │
│ │ 标题 │ │ │战士  │ │ │ 能量 │ │ │ 爆发 │ │ │ 对决 │     │
│ │ 展示 │ │ │ 登场 │ │ │ 聚集 │ │ │ 瞬间 │ │ │ 场面 │     │
│ └──────┘ │ └──────┘ │ └──────┘ │ └──────┘ │ └──────┘     │
│ zoom-in  │ shake    │ pan-left │ flash    │ zoom-out     │
│ [Pexels] │ [AI生成] │ [Pexels] │ [AI生成] │ [Pixabay]    │
└──────────┴──────────┴──────────┴──────────┴──────────────┘

用户操作：
  [✓ 确认全部]  [✎ 修改 Scene 3]  [↻ 重新生成 Scene 4]  [+ 插入镜头]
```

### 阶段 4：用户调整（可选）

- 替换素材：指定某个场景使用自己的图片
- 修改提示词：调整 AI 生成的画面描述
- 调整时长：拉长或缩短某个镜头
- 重新排序：拖拽调整场景顺序

### 阶段 5：最终渲染

```bash
1. 下载/生成所有素材文件
2. 调用 Remotion 渲染
3. 输出：output/星辰之战_1080x1920.mp4
```

---

## 技术实现细节

### 素材获取策略（质量优先）

```python
class AssetManager:
    def fetch_asset(self, scene: dict, style: dict) -> str:
        """
        质量优先的素材获取策略：
        1. 先从素材库搜索高质量匹配
        2. 评估匹配度，不满意再用 AI 生成
        3. AI 生成作为兜底方案
        """
        keywords = self._build_keywords(scene, style)

        # 第一步：素材库搜索
        stock_results = self.downloader.search(
            keywords=keywords,
            media_type=self._get_media_type(scene),
            min_resolution="1080p",
            orientation="portrait"
        )

        if stock_results and stock_results[0]["relevance"] > 0.7:
            return self.downloader.download(stock_results[0])

        # 第二步：AI 生成兜底
        if scene.get("allow_ai_fallback", True):
            prompt = scene["visual"]["prompt"] + style["ai_prompt_suffix"]
            return self.zimage.generate(prompt)

        # 第三步：降低标准使用素材库
        if stock_results:
            return self.downloader.download(stock_results[0])

        raise AssetNotFoundError(f"无法获取素材: {keywords}")
```

### 素材质量配置

```yaml
quality_requirements:
  image:
    min_width: 1080
    min_height: 1920
    formats: ["jpg", "png", "webp"]

  video:
    min_width: 1080
    min_height: 1920
    min_fps: 24
    max_duration: 30
    formats: ["mp4", "mov"]

  search_strategy:
    sources_priority:
      - "pexels"
      - "pixabay"
      - "ai_generate"
    max_search_attempts: 3
```

### Remotion 组件架构

```
remotion/src/
├── Root.tsx
├── compositions/
│   └── MVComposition.tsx
├── components/
│   ├── scenes/
│   │   ├── TitleScene.tsx
│   │   ├── ActionScene.tsx
│   │   ├── LyricScene.tsx
│   │   └── TransitionScene.tsx
│   ├── animations/
│   │   ├── ZoomIn.tsx
│   │   ├── Shake.tsx
│   │   ├── SpeedLines.tsx
│   │   └── KenBurns.tsx
│   └── effects/
│       ├── GlitchEffect.tsx
│       ├── ParticleEffect.tsx
│       └── FlashEffect.tsx
└── utils/
    ├── beatSync.ts
    └── styleLoader.ts
```

---

## 错误处理

### 错误处理策略

| 错误类型 | 处理方式 | 用户提示 |
|---------|---------|---------|
| Suno API 失败 | 提示用户上传本地音乐 | "音乐生成失败，请上传本地 MP3 文件" |
| 素材搜索无结果 | 放宽关键词 → AI 生成 → 请求用户提供 | "未找到合适素材，已使用 AI 生成替代" |
| AI 图像生成失败 | 重试 2 次 → 使用素材库兜底 | "AI 生成失败，已从素材库获取替代图片" |
| Remotion 渲染崩溃 | 定位问题场景，隔离渲染 | "Scene 3 渲染失败，请检查素材格式" |
| API 配额用尽 | 提示配置 API Key | "Pexels 配额已用尽，请配置 PEXELS_API_KEY" |

### 断点续传

```yaml
# .mv-skill/session/{title}_{date}.yaml
session_id: "abc123"
status: "preview_generated"
progress:
  music: "completed"
  storyboard: "completed"
  assets:
    scene_1: "downloaded"
    scene_2: "downloaded"
    scene_3: "pending"
  render: "pending"
```

### 超时配置

```yaml
timeouts:
  music_generation: 180
  image_generation: 60
  asset_download: 30
  render_per_scene: 60
  total_render: 600
```

---

## 环境配置

### 必需依赖

```bash
# Remotion
cd ~/.claude/skills/mv-skill/remotion && npm install

# Python
pip install requests librosa pydub pyyaml
```

### API Keys

```bash
export SUNO_API_KEY="your_key"      # AI 音乐生成
export PEXELS_API_KEY="your_key"    # 高质量素材（推荐）
export PIXABAY_API_KEY="your_key"   # 备用素材源
```

---

## 使用示例

### 基础用法

```
"帮我做一个热血风格的 MV，主题是宇宙战士"
```

### 完整参数

```
"制作一个赛博朋克风格的 MV
 主题：霓虹都市的孤独黑客
 歌词：在数据的海洋里漂流
 时长：55 秒"
```

### 调整分镜

```
"修改 Scene 3，换成我自己的图片 hero.png"
"Scene 4 重新生成，要更有冲击力"
```

---

## 后续扩展

- [ ] 新增更多风格模板
- [ ] 支持 16:9 横屏输出
- [ ] 支持更长时长（完整 MV）
- [ ] 支持自定义动画效果
- [ ] 支持多语言歌词
