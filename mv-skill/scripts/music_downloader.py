"""
音乐下载器
从歌曲宝等网站搜索和下载音乐
"""
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote

import requests

from .config import CACHE_DIR
from .exceptions import MusicGenerationError


class MusicDownloader:
    """音乐下载器"""

    def __init__(self):
        self.cache_dir = CACHE_DIR / "music"
        self.cache_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })

    def search_music(self, keyword: str, limit: int = 5) -> List[Dict]:
        """
        搜索音乐

        Args:
            keyword: 搜索关键词
            limit: 返回结果数量

        Returns:
            [{"id": "xxx", "title": "xxx", "artist": "xxx"}, ...]
        """
        try:
            url = f"https://www.gequbao.com/s/{quote(keyword)}"
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()

            # 解析搜索结果 - 匹配歌曲链接和标题
            results = []
            # 匹配 music-link 类的链接，然后找到内部的 span > span 标题
            pattern = r'<a href="/music/(\d+)"[^>]*class="music-link[^"]*"[^>]*>.*?music-title[^>]*>\s*<span>([^<]+)</span>'
            matches = re.findall(pattern, resp.text, re.DOTALL)

            seen_ids = set()
            for music_id, title in matches:
                if music_id in seen_ids:
                    continue
                seen_ids.add(music_id)

                # 解析歌曲名和歌手
                title = title.strip()
                parts = title.split(" - ")
                song_title = parts[0].strip() if parts else title
                artist = parts[1].strip() if len(parts) > 1 else "未知"

                results.append({
                    "id": music_id,
                    "title": song_title,
                    "artist": artist,
                })

                if len(results) >= limit:
                    break

            return results

        except Exception as e:
            print(f"[MusicDownloader] 搜索失败: {e}")
            return []

    def get_download_url(self, music_id: str) -> Optional[str]:
        """
        获取音乐下载链接

        Args:
            music_id: 音乐 ID

        Returns:
            下载 URL 或 None
        """
        try:
            # 获取音乐详情页
            url = f"https://www.gequbao.com/music/{music_id}"
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()

            # 从页面提取 play_id
            play_id_match = re.search(r'"play_id":"([^"]+)"', resp.text)
            if not play_id_match:
                return None

            play_id = play_id_match.group(1)

            # 调用 API 获取下载链接
            api_url = "https://www.gequbao.com/api/play-url"
            api_resp = self.session.post(
                api_url,
                data={"id": play_id},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
            api_resp.raise_for_status()

            data = api_resp.json()
            if data.get("code") == 1 and data.get("data", {}).get("url"):
                return data["data"]["url"]

            return None

        except Exception as e:
            print(f"[MusicDownloader] 获取下载链接失败: {e}")
            return None

    def download(self, music_id: str, filename: Optional[str] = None) -> Optional[Path]:
        """
        下载音乐

        Args:
            music_id: 音乐 ID
            filename: 保存的文件名（不含扩展名）

        Returns:
            下载的文件路径或 None
        """
        download_url = self.get_download_url(music_id)
        if not download_url:
            print(f"[MusicDownloader] 无法获取下载链接: {music_id}")
            return None

        try:
            # 下载文件
            resp = self.session.get(download_url, timeout=60, stream=True)
            resp.raise_for_status()

            # 确定文件名
            if not filename:
                filename = f"music_{music_id}"
            output_path = self.cache_dir / f"{filename}.mp3"

            # 保存文件
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"[MusicDownloader] 下载完成: {output_path}")
            return output_path

        except Exception as e:
            print(f"[MusicDownloader] 下载失败: {e}")
            return None

    def search_and_download(
        self,
        keyword: str,
        prefer_index: int = 0,
    ) -> Optional[Path]:
        """
        搜索并下载音乐

        Args:
            keyword: 搜索关键词
            prefer_index: 优先选择的结果索引

        Returns:
            下载的文件路径或 None
        """
        results = self.search_music(keyword)
        if not results:
            print(f"[MusicDownloader] 未找到: {keyword}")
            return None

        # 选择结果
        index = min(prefer_index, len(results) - 1)
        selected = results[index]

        print(f"[MusicDownloader] 选择: {selected['title']} - {selected['artist']}")

        # 下载
        filename = f"{selected['title']}_{selected['artist']}".replace("/", "_")
        return self.download(selected["id"], filename)


def search_and_download_music(keyword: str) -> Optional[Path]:
    """
    便捷函数：搜索并下载音乐

    Args:
        keyword: 搜索关键词

    Returns:
        下载的文件路径或 None
    """
    downloader = MusicDownloader()
    return downloader.search_and_download(keyword)
