#!/usr/bin/env python3
"""
MV Skill CLI 入口
用于命令行调用和 Claude Code 集成
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional, List
import yaml

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.config import AVAILABLE_STYLES, DEFAULT_CONFIG, OUTPUT_DIR, CACHE_DIR
from scripts.storyboard_generator import StoryboardGenerator
from scripts.asset_manager import AssetManager
from scripts.music_generator import MusicGenerator
from scripts.preview_generator import PreviewGenerator
from scripts.renderer import Renderer
from scripts.exceptions import MVSkillError


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="MV Skill - 动感短视频生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成分镜脚本
  python cli.py generate --title "小宇宙觉醒" --theme "宇宙战士" --style anime-hype

  # 使用本地音乐
  python cli.py generate --title "我的MV" --theme "热血战斗" --music /path/to/music.mp3

  # 获取素材
  python cli.py fetch-assets --storyboard storyboard.yaml

  # 渲染视频
  python cli.py render --storyboard storyboard.yaml --assets assets.json
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成分镜脚本")
    gen_parser.add_argument("--title", required=True, help="MV 标题")
    gen_parser.add_argument("--theme", required=True, help="主题描述")
    gen_parser.add_argument(
        "--style",
        choices=AVAILABLE_STYLES,
        default=DEFAULT_CONFIG["style"],
        help="风格模板",
    )
    gen_parser.add_argument(
        "--duration",
        type=int,
        default=DEFAULT_CONFIG["duration"],
        help="时长（秒）",
    )
    gen_parser.add_argument("--lyrics", nargs="+", help="歌词列表")
    gen_parser.add_argument("--music", help="本地音乐文件路径")
    gen_parser.add_argument("--output", "-o", help="输出文件路径")

    # fetch-assets 命令
    fetch_parser = subparsers.add_parser("fetch-assets", help="获取素材")
    fetch_parser.add_argument("--storyboard", required=True, help="分镜脚本文件路径")
    fetch_parser.add_argument("--output", "-o", help="素材映射输出路径")

    # preview 命令
    preview_parser = subparsers.add_parser("preview", help="生成预览")
    preview_parser.add_argument("--storyboard", required=True, help="分镜脚本文件路径")
    preview_parser.add_argument("--assets", help="素材映射文件路径")

    # render 命令
    render_parser = subparsers.add_parser("render", help="渲染视频")
    render_parser.add_argument("--storyboard", required=True, help="分镜脚本文件路径")
    render_parser.add_argument("--assets", required=True, help="素材映射文件路径")
    render_parser.add_argument("--output", "-o", help="输出文件名")

    # full 命令（完整流程）
    full_parser = subparsers.add_parser("full", help="完整流程：生成 -> 素材 -> 渲染")
    full_parser.add_argument("--title", required=True, help="MV 标题")
    full_parser.add_argument("--theme", required=True, help="主题描述")
    full_parser.add_argument(
        "--style",
        choices=AVAILABLE_STYLES,
        default=DEFAULT_CONFIG["style"],
        help="风格模板",
    )
    full_parser.add_argument(
        "--duration",
        type=int,
        default=DEFAULT_CONFIG["duration"],
        help="时长（秒）",
    )
    full_parser.add_argument("--lyrics", nargs="+", help="歌词列表")
    full_parser.add_argument("--music", help="本地音乐文件路径")
    full_parser.add_argument("--search-music", help="搜索并下载音乐（关键词）")
    full_parser.add_argument("--skip-preview", action="store_true", help="跳过预览确认")

    # status 命令
    status_parser = subparsers.add_parser("status", help="检查环境状态")

    # medley 命令（歌曲串烧）
    medley_parser = subparsers.add_parser("medley", help="生成歌曲串烧短视频")
    medley_parser.add_argument("--theme", default="nostalgic", help="串烧主题 (nostalgic/anime-battle/emotional)")
    medley_parser.add_argument("--songs", nargs="+", help="歌曲关键词列表")
    medley_parser.add_argument("--title", help="串烧标题")
    medley_parser.add_argument(
        "--duration",
        type=int,
        default=45,
        help="总时长（秒）",
    )
    medley_parser.add_argument("--auto", action="store_true", help="自动选择歌曲")
    medley_parser.add_argument("--count", type=int, default=4, help="自动选择歌曲数量")
    medley_parser.add_argument("--skip-preview", action="store_true", help="跳过预览确认")

    return parser


def cmd_generate(args) -> dict:
    """生成分镜脚本"""
    print(f"[MV Skill] 生成分镜脚本...")
    print(f"  标题: {args.title}")
    print(f"  主题: {args.theme}")
    print(f"  风格: {args.style}")
    print(f"  时长: {args.duration}秒")

    # 初始化生成器
    generator = StoryboardGenerator(style=args.style)

    # 处理音乐
    music_info = None
    if args.music:
        print(f"  音乐: {args.music}")
        music_gen = MusicGenerator()
        music_info = music_gen.analyze_local_music(args.music)
        print(f"  检测到 BPM: {music_info['bpm']}")

    # 生成分镜
    storyboard = generator.generate(
        title=args.title,
        theme=args.theme,
        lyrics=args.lyrics,
        duration=args.duration,
    )

    # 如果有音乐，更新分镜
    if music_info:
        storyboard["music"]["source"] = "local"
        storyboard["music"]["file"] = music_info["file"]
        storyboard["music"]["bpm"] = music_info["bpm"]
        storyboard["music"]["beats"] = music_info["beats"]

        # 对齐节拍
        music_gen = MusicGenerator()
        storyboard["scenes"] = music_gen.align_scenes_to_beats(
            storyboard["scenes"],
            music_info["beats"],
        )

    # 输出
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = CACHE_DIR / f"{args.title}_storyboard.yaml"

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(storyboard, f, allow_unicode=True, default_flow_style=False)

    print(f"[MV Skill] 分镜脚本已保存: {output_path}")

    return storyboard


def cmd_fetch_assets(args) -> dict:
    """获取素材"""
    # 加载分镜脚本
    storyboard = load_storyboard(args.storyboard)
    title = storyboard.get("meta", {}).get("title", "mv")

    print(f"[MV Skill] 获取素材...")
    print(f"  分镜: {args.storyboard}")
    print(f"  场景数: {len(storyboard.get('scenes', []))}")

    # 加载风格配置
    style = storyboard.get("meta", {}).get("style", "anime-hype")
    style_config = load_style_config(style)

    # 初始化素材管理器
    asset_manager = AssetManager(style_config=style_config)

    # 获取所有素材
    assets = asset_manager.fetch_all_assets(storyboard)

    # 生成报告
    report = asset_manager.get_asset_report(assets)
    print(report)

    # 输出
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = CACHE_DIR / f"{title}_assets.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(assets, f, ensure_ascii=False, indent=2)

    print(f"[MV Skill] 素材映射已保存: {output_path}")

    return assets


def cmd_preview(args) -> str:
    """生成预览"""
    # 加载分镜脚本
    storyboard = load_storyboard(args.storyboard)

    # 加载素材映射
    assets = {}
    if args.assets:
        with open(args.assets, "r", encoding="utf-8") as f:
            assets = json.load(f)

    print(f"[MV Skill] 生成预览...")

    # 生成预览
    preview_gen = PreviewGenerator()
    preview = preview_gen.generate_storyboard_preview(storyboard, assets)

    print(preview)

    # 生成素材报告
    if assets:
        report = preview_gen.generate_asset_report(assets, storyboard)
        print(report)

    return preview


def cmd_render(args) -> str:
    """渲染视频"""
    # 加载分镜脚本
    storyboard = load_storyboard(args.storyboard)

    # 加载素材映射
    with open(args.assets, "r", encoding="utf-8") as f:
        assets = json.load(f)

    print(f"[MV Skill] 开始渲染...")

    # 渲染
    renderer = Renderer()
    output_path = renderer.render(storyboard, assets, args.output)

    print(f"[MV Skill] 渲染完成: {output_path}")

    return output_path


def cmd_full(args) -> str:
    """完整流程"""
    print("=" * 60)
    print(f"  MV Skill - 完整制作流程")
    print("=" * 60)

    # 0. 搜索并下载音乐（如果指定）
    if hasattr(args, 'search_music') and args.search_music:
        print(f"\n[Step 0/4] 搜索并下载音乐: {args.search_music}")
        from scripts.music_downloader import MusicDownloader
        downloader = MusicDownloader()
        music_path = downloader.search_and_download(args.search_music)
        if music_path:
            args.music = str(music_path)
            print(f"  音乐已下载: {music_path}")
        else:
            print("  ⚠️ 音乐搜索失败，将继续但无背景音乐")

    # 1. 生成分镜
    print("\n[Step 1/4] 生成分镜脚本")
    args.output = None
    storyboard = cmd_generate(args)

    # 2. 获取素材
    print("\n[Step 2/4] 获取素材")
    style = storyboard.get("meta", {}).get("style", "anime-hype")
    style_config = load_style_config(style)
    asset_manager = AssetManager(style_config=style_config)
    assets = asset_manager.fetch_all_assets(storyboard)

    # 3. 预览
    if not args.skip_preview:
        print("\n[Step 3/4] 生成预览")
        preview_gen = PreviewGenerator()
        preview = preview_gen.generate_storyboard_preview(storyboard, assets)
        print(preview)

        # 检查是否所有素材都获取成功
        failed = [k for k, v in assets.items() if not v]
        if failed:
            print(f"\n⚠️  以下场景素材获取失败: {failed}")
            print("请检查后重试，或手动提供素材")
            return None
    else:
        print("\n[Step 3/4] 跳过预览")

    # 4. 渲染
    print("\n[Step 4/4] 渲染视频")
    renderer = Renderer()
    output_path = renderer.render(storyboard, assets)

    print("\n" + "=" * 60)
    print(f"  制作完成!")
    print(f"  输出: {output_path}")
    print("=" * 60)

    return output_path


def cmd_status(args):
    """检查环境状态"""
    from scripts.config import (
        SUNO_API_KEY,
        PEXELS_API_KEY,
        PIXABAY_API_KEY,
        ZIMAGE_SKILL_DIR,
        MEDIA_DOWNLOADER_DIR,
        REMOTION_DIR,
    )

    print("MV Skill 环境状态")
    print("=" * 50)

    # 检查依赖 Skills
    print("\n依赖 Skills:")
    zimage_ok = (ZIMAGE_SKILL_DIR / "generate.py").exists()
    media_ok = (MEDIA_DOWNLOADER_DIR / "media_cli.py").exists()
    print(f"  zimage-skill:      {'✅' if zimage_ok else '❌'} {ZIMAGE_SKILL_DIR}")
    print(f"  media-downloader:  {'✅' if media_ok else '❌'} {MEDIA_DOWNLOADER_DIR}")

    # 检查 API Keys
    print("\nAPI Keys:")
    print(f"  SUNO_API_KEY:      {'✅ 已配置' if SUNO_API_KEY else '❌ 未配置'}")
    print(f"  PEXELS_API_KEY:    {'✅ 已配置' if PEXELS_API_KEY else '❌ 未配置'}")
    print(f"  PIXABAY_API_KEY:   {'✅ 已配置' if PIXABAY_API_KEY else '❌ 未配置'}")

    # 检查 Remotion
    print("\nRemotion:")
    remotion_init = (REMOTION_DIR / "package.json").exists()
    remotion_deps = (REMOTION_DIR / "node_modules").exists()
    print(f"  项目初始化:        {'✅' if remotion_init else '❌'}")
    print(f"  依赖安装:          {'✅' if remotion_deps else '❌'}")

    # 检查 Python 依赖
    print("\nPython 依赖:")
    try:
        import yaml
        print("  pyyaml:            ✅")
    except ImportError:
        print("  pyyaml:            ❌ pip install pyyaml")

    try:
        import PIL
        print("  pillow:            ✅")
    except ImportError:
        print("  pillow:            ❌ pip install pillow")

    try:
        import librosa
        print("  librosa:           ✅")
    except ImportError:
        print("  librosa:           ⚠️  可选 (pip install librosa)")

    # 检查系统工具
    print("\n系统工具:")
    import subprocess
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("  ffmpeg:            ✅")
    except:
        print("  ffmpeg:            ❌ brew install ffmpeg")

    try:
        subprocess.run(["node", "-v"], capture_output=True, check=True)
        print("  node:              ✅")
    except:
        print("  node:              ❌ 需要安装 Node.js")


def load_storyboard(path: str) -> dict:
    """加载分镜脚本"""
    p = Path(path)
    if not p.exists():
        raise MVSkillError(f"文件不存在: {path}")

    with open(p, "r", encoding="utf-8") as f:
        if p.suffix in [".yaml", ".yml"]:
            return yaml.safe_load(f)
        else:
            return json.load(f)


def load_style_config(style: str) -> dict:
    """加载风格配置"""
    from scripts.config import TEMPLATES_DIR

    template_path = TEMPLATES_DIR / style / "template.yaml"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def cmd_medley(args) -> str:
    """生成歌曲串烧"""
    from scripts.medley_generator import MedleyGenerator

    print("=" * 60)
    print("  MV Skill - 歌曲串烧生成")
    print("=" * 60)

    # 初始化生成器
    generator = MedleyGenerator(theme=args.theme)

    # 添加歌曲
    if args.auto:
        generator.auto_select_songs(count=args.count)
    elif args.songs:
        for song in args.songs:
            generator.add_song(song)
    else:
        print("❌ 请指定歌曲 (--songs) 或使用自动选择 (--auto)")
        return None

    # 生成分镜脚本
    storyboard = generator.generate(
        total_duration=args.duration,
        title=args.title,
    )

    # 保存分镜脚本
    title = storyboard["meta"]["title"]
    storyboard_path = CACHE_DIR / f"{title}_storyboard.yaml"
    with open(storyboard_path, "w", encoding="utf-8") as f:
        yaml.dump(storyboard, f, allow_unicode=True, default_flow_style=False)
    print(f"\n[MedleyGenerator] 分镜脚本已保存: {storyboard_path}")

    # 获取素材 - 根据场景类型选择不同的获取方式
    print("\n[Step] 获取素材...")
    style_config = load_medley_style_config(args.theme)

    # 检查是否使用视频混剪模式
    use_video_mix = style_config.get("use_video_mix", False)
    scenes = storyboard.get("scenes", [])

    if use_video_mix:
        # 使用视频素材获取器
        print("[Step] 使用视频混剪模式...")
        try:
            from scripts.video_asset_fetcher import VideoAssetFetcher
            video_fetcher = VideoAssetFetcher()
            assets = video_fetcher.fetch_videos_for_scenes(scenes)
        except Exception as e:
            print(f"[Warning] 视频获取失败，回退到程序化模式: {e}")
            # 回退到程序化模式
            assets = {scene["id"]: "programmatic" for scene in scenes}
    else:
        # 使用普通素材管理器
        asset_manager = AssetManager(style_config=style_config)
        assets = asset_manager.fetch_all_assets(storyboard)

    # 预览
    if not args.skip_preview:
        print("\n[Step] 生成预览...")
        preview_gen = PreviewGenerator()
        preview = preview_gen.generate_storyboard_preview(storyboard, assets)
        print(preview)

        failed = [k for k, v in assets.items() if not v]
        if failed:
            print(f"\n⚠️  以下场景素材获取失败: {failed}")

    # 渲染
    print("\n[Step] 渲染视频...")
    renderer = Renderer()
    output_path = renderer.render(storyboard, assets)

    print("\n" + "=" * 60)
    print("  串烧制作完成!")
    print(f"  输出: {output_path}")
    print("=" * 60)

    return output_path


def load_medley_style_config(theme: str) -> dict:
    """加载串烧主题配置"""
    from scripts.config import TEMPLATES_DIR

    template_path = TEMPLATES_DIR / "medley" / f"{theme}.yaml"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def main():
    """主入口"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "generate":
            cmd_generate(args)
        elif args.command == "fetch-assets":
            cmd_fetch_assets(args)
        elif args.command == "preview":
            cmd_preview(args)
        elif args.command == "render":
            cmd_render(args)
        elif args.command == "full":
            cmd_full(args)
        elif args.command == "status":
            cmd_status(args)
        elif args.command == "medley":
            cmd_medley(args)
        else:
            parser.print_help()
            return 1

        return 0

    except MVSkillError as e:
        print(f"\n❌ 错误: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消")
        return 130
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
