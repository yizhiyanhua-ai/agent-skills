---
name: mv-skill
description: |
  基于 Remotion 的动感 MV 短视频生成器。支持多种风格模板，
  AI 音乐生成，自动分镜，可视化预览，商业级输出质量。
  触发方式: "制作MV", "生成MV", "做一个音乐视频", "/mv"
dependencies:
  - remotion-best-practices
  - zimage-skill
  - media-downloader
---

# MV Skill - 动感短视频生成器

只需描述你的想法，即可生成商业级 MV 短视频。

## 功能特点

- **多风格模板** - 热血动漫、赛博朋克、抒情 MV
- **AI 音乐生成** - 集成 Suno，自动生成配乐
- **智能素材获取** - 素材库优先，AI 生成兜底
- **可视化预览** - 确认分镜后再渲染
- **短视频优化** - 9:16 竖屏，50-60 秒

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

## 可用风格模板

| 风格 | 关键词 | 适合场景 |
|------|--------|---------|
| `anime-hype` | 热血、动漫、燃 | 战斗、励志、运动 |
| `cyberpunk` | 赛博、科技、霓虹 | 科幻、电子音乐 |
| `lyric` | 抒情、唯美、治愈 | 情歌、慢歌 |

## 工作流程

1. **输入** - 描述主题和风格
2. **生成** - AI 生成音乐 + 分镜脚本
3. **预览** - 查看分镜预览图
4. **调整** - 修改不满意的镜头（可选）
5. **渲染** - 输出最终 MP4

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
# ~/.zshrc 或 ~/.bashrc
export SUNO_API_KEY="your_key"      # AI 音乐生成
export PEXELS_API_KEY="your_key"    # 高质量素材（推荐）
export PIXABAY_API_KEY="your_key"   # 备用素材源
```

## 使用示例

### 示例 1：热血动漫风

```
用户: "做一个圣斗士星矢风格的 MV，主题是小宇宙觉醒"

AI: 正在生成分镜预览...

┌─────────────────────────────────────┐
│ 分镜预览 - 小宇宙觉醒               │
├─────┬─────┬─────┬─────┬─────┬─────┤
│ 标题 │ 战士 │ 聚能 │ 爆发 │ 升华 │ 终结 │
│ 5s  │ 10s │ 15s │ 15s │ 5s  │ 5s  │
└─────┴─────┴─────┴─────┴─────┴─────┘

确认开始渲染？[确认/修改 Scene X/重新生成]

用户: "确认"

AI: 渲染完成！输出: output/小宇宙觉醒_1080x1920.mp4
```

### 示例 2：自定义调整

```
用户: "修改 Scene 3，换成我自己的图片 hero.png"

AI: 已更新 Scene 3 素材为 hero.png，预览已刷新。
```

### 示例 3：使用本地音乐

```
用户: "使用这个音乐文件 /path/to/music.mp3 制作 MV"

AI: 已检测音乐 BPM: 128，时长: 58秒，正在生成匹配的分镜...
```

## 输出位置

```
~/.claude/skills/mv-skill/output/
└── {标题}_{分辨率}.mp4
```

## 常见问题

**Q: 音乐生成失败怎么办？**
A: 可以上传本地 MP3 文件代替："使用这个音乐文件 /path/to/music.mp3"

**Q: 素材质量不满意？**
A: 在预览阶段说"Scene 2 换一张"或提供自己的素材

**Q: 渲染太慢？**
A: 首次渲染需要下载依赖，后续会快很多

**Q: 如何添加自定义歌词？**
A: 在描述中包含歌词，如"歌词：燃烧吧小宇宙"

## 技术架构

```
mv-skill/
├── SKILL.md              # 本文档
├── templates/            # MV 风格模板
│   ├── anime-hype/       # 热血动漫风
│   ├── cyberpunk/        # 赛博朋克风
│   └── lyric/            # 抒情风
├── schemas/              # 分镜脚本 Schema
├── scripts/              # 核心脚本
└── remotion/             # Remotion 项目
```

## 依赖的 Skills

- `remotion-best-practices` - Remotion 视频制作知识库
- `zimage-skill` - AI 图像生成
- `media-downloader` - 素材库下载
