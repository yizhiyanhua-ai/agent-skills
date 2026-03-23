"""
渲染器
调用 Remotion 将分镜脚本渲染为最终视频
"""
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional

from .config import REMOTION_DIR, OUTPUT_DIR, CACHE_DIR, TIMEOUTS
from .exceptions import RenderError


class Renderer:
    """Remotion 渲染器"""

    def __init__(self):
        self.remotion_dir = REMOTION_DIR
        self.output_dir = OUTPUT_DIR
        self.public_dir = REMOTION_DIR / "public"
        self.output_dir.mkdir(exist_ok=True)
        self.public_dir.mkdir(exist_ok=True)
        self._check_remotion()

    def _check_remotion(self):
        """检查 Remotion 环境"""
        package_json = self.remotion_dir / "package.json"
        node_modules = self.remotion_dir / "node_modules"

        if not package_json.exists():
            raise RenderError(
                f"Remotion 项目未初始化。请先运行：\n"
                f"  cd {self.remotion_dir} && npm install"
            )

        if not node_modules.exists():
            raise RenderError(
                f"Remotion 依赖未安装。请运行：\n"
                f"  cd {self.remotion_dir} && npm install"
            )

    def render(
        self,
        storyboard: Dict,
        assets: Dict[str, str],
        output_name: Optional[str] = None,
    ) -> str:
        """
        渲染视频

        Args:
            storyboard: 分镜脚本
            assets: {scene_id: asset_path} 素材映射
            output_name: 输出文件名（不含扩展名）

        Returns:
            输出视频路径
        """
        meta = storyboard.get("meta", {})
        title = meta.get("title", "mv_output")
        resolution = meta.get("resolution", "1080x1920")
        fps = meta.get("fps", 30)
        duration = meta.get("duration", 55)

        # 准备输出路径
        if not output_name:
            output_name = f"{title}_{resolution}"
        output_path = self.output_dir / f"{output_name}.mp4"

        # 更新分镜脚本中的素材路径
        storyboard_with_assets = self._inject_assets(storyboard, assets)

        # 写入临时配置文件
        config_path = CACHE_DIR / "render_config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(storyboard_with_assets, f, ensure_ascii=False, indent=2)

        # 解析分辨率
        width, height = resolution.split("x")

        # 调用 Remotion 渲染
        try:
            self._run_remotion_render(
                config_path=config_path,
                output_path=output_path,
                width=int(width),
                height=int(height),
                fps=fps,
                duration=duration,
            )
        except Exception as e:
            raise RenderError(f"渲染失败: {e}")

        if not output_path.exists():
            raise RenderError("渲染完成但输出文件不存在")

        return str(output_path)

    def _inject_assets(
        self,
        storyboard: Dict,
        assets: Dict[str, str],
    ) -> Dict:
        """将素材路径注入分镜脚本，并复制素材到 public 目录"""
        result = storyboard.copy()
        result["scenes"] = []

        # 创建素材子目录
        assets_dir = self.public_dir / "assets"
        assets_dir.mkdir(exist_ok=True)

        for scene in storyboard.get("scenes", []):
            scene_copy = scene.copy()
            scene_id = scene["id"]

            # DJ 场景是程序化生成的，不需要素材文件
            # video_mix 场景需要视频素材文件
            if scene.get("type") == "dj" or scene.get("visual", {}).get("source") == "programmatic":
                result["scenes"].append(scene_copy)
                continue

            # video_mix 场景需要视频文件
            if scene.get("type") == "video_mix":
                if scene_id in assets and assets[scene_id] and assets[scene_id] != "programmatic":
                    src_path = Path(assets[scene_id])
                    if src_path.exists():
                        # 复制视频素材到 public/assets 目录
                        dest_name = f"{scene_id}_{src_path.name}"
                        dest_path = assets_dir / dest_name
                        shutil.copy2(src_path, dest_path)

                        # 使用相对于 public 的路径
                        scene_copy["visual"] = scene.get("visual", {}).copy()
                        scene_copy["visual"]["file"] = f"assets/{dest_name}"
                result["scenes"].append(scene_copy)
                continue

            if scene_id in assets and assets[scene_id] and assets[scene_id] != "programmatic":
                src_path = Path(assets[scene_id])
                if src_path.exists():
                    # 复制素材到 public/assets 目录
                    dest_name = f"{scene_id}_{src_path.name}"
                    dest_path = assets_dir / dest_name
                    shutil.copy2(src_path, dest_path)

                    # 使用相对于 public 的路径
                    scene_copy["visual"] = scene.get("visual", {}).copy()
                    scene_copy["visual"]["file"] = f"assets/{dest_name}"

            result["scenes"].append(scene_copy)

        # 处理音乐文件
        if "music" in storyboard and storyboard["music"].get("file"):
            music_src = Path(storyboard["music"]["file"])
            if music_src.exists():
                music_dest = self.public_dir / music_src.name
                shutil.copy2(music_src, music_dest)
                result["music"] = storyboard["music"].copy()
                result["music"]["file"] = music_src.name

        return result

    def _run_remotion_render(
        self,
        config_path: Path,
        output_path: Path,
        width: int,
        height: int,
        fps: int,
        duration: int,
    ):
        """执行 Remotion 渲染命令"""
        # 计算帧数
        frame_count = duration * fps

        cmd = [
            "npx",
            "remotion",
            "render",
            "MVComposition",  # 组合名称
            str(output_path),
            "--props", str(config_path),
            "--width", str(width),
            "--height", str(height),
            "--fps", str(fps),
            "--frames", f"0-{frame_count - 1}",
            "--codec", "h264",
            "--crf", "18",  # 高质量
        ]

        print(f"[Renderer] 开始渲染...")
        print(f"[Renderer] 输出: {output_path}")
        print(f"[Renderer] 分辨率: {width}x{height} @ {fps}fps")
        print(f"[Renderer] 时长: {duration}秒 ({frame_count}帧)")

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.remotion_dir),
                capture_output=True,
                text=True,
                timeout=TIMEOUTS["total_render"],
            )

            if result.returncode != 0:
                print(f"[Renderer] 错误输出:\n{result.stderr}")
                raise RenderError(f"Remotion 渲染失败: {result.stderr[:500]}")

            print(f"[Renderer] 渲染完成!")

        except subprocess.TimeoutExpired:
            raise RenderError(f"渲染超时（{TIMEOUTS['total_render']}秒）")

    def preview_render(
        self,
        storyboard: Dict,
        assets: Dict[str, str],
        scene_id: str,
    ) -> str:
        """
        预览渲染单个场景

        Args:
            storyboard: 分镜脚本
            assets: 素材映射
            scene_id: 要预览的场景 ID

        Returns:
            预览图路径
        """
        # 找到指定场景
        scene = None
        for s in storyboard.get("scenes", []):
            if s["id"] == scene_id:
                scene = s
                break

        if not scene:
            raise RenderError(f"场景不存在: {scene_id}")

        # 渲染单帧
        meta = storyboard.get("meta", {})
        fps = meta.get("fps", 30)
        start_frame = int(scene["start"] * fps)

        preview_path = CACHE_DIR / f"preview_{scene_id}.png"

        # TODO: 实现单帧渲染
        # npx remotion still ...

        return str(preview_path)


def render_mv(
    storyboard: Dict,
    assets: Dict[str, str],
    output_name: Optional[str] = None,
) -> str:
    """
    便捷函数：渲染 MV

    Args:
        storyboard: 分镜脚本
        assets: 素材映射
        output_name: 输出文件名

    Returns:
        输出视频路径
    """
    renderer = Renderer()
    return renderer.render(storyboard, assets, output_name)
