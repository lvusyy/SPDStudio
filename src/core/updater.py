"""
GitHub Release 更新检查器
"""
import json
import threading
import webbrowser
import urllib.request
import platform
from dataclasses import dataclass
from typing import Optional, Callable, Tuple

from ..utils.version import __version__, __version_info__, GITHUB_API_URL, GITHUB_RELEASES_URL


@dataclass
class ReleaseInfo:
    """GitHub Release 信息"""
    version: Tuple[int, ...]
    tag_name: str
    body: str  # Release notes
    html_url: str
    download_url: Optional[str]
    is_newer: bool


class UpdateChecker:
    """更新检查器"""

    def __init__(self):
        self.current_version = __version__
        self.current_version_info = __version_info__

    def parse_version(self, version_str: str) -> Tuple[int, ...]:
        """解析版本字符串 'v1.2.3' 或 '1.2.3' 为元组 (1, 2, 3)"""
        clean = version_str.lstrip('vV').strip()
        parts = clean.split('.')
        try:
            return tuple(int(p) for p in parts[:3])
        except (ValueError, IndexError):
            return (0, 0, 0)

    def is_newer_version(self, remote_version: str) -> bool:
        """比较远程版本是否比当前版本新"""
        try:
            remote = self.parse_version(remote_version)
            return remote > self.current_version_info
        except (ValueError, IndexError):
            return False

    def check_for_updates(
        self,
        callback: Callable[[Optional[ReleaseInfo], Optional[str]], None],
        timeout: int = 10
    ):
        """异步检查更新"""
        def _check():
            try:
                req = urllib.request.Request(
                    GITHUB_API_URL,
                    headers={
                        "Accept": "application/vnd.github.v3+json",
                        "User-Agent": f"SPDStudio/{self.current_version}"
                    }
                )
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    data = json.loads(response.read().decode('utf-8'))

                tag_name = data.get("tag_name", "")
                is_newer = self.is_newer_version(tag_name)

                # 查找平台特定的下载 URL
                download_url = None
                system = platform.system().lower()
                for asset in data.get("assets", []):
                    name = asset.get("name", "").lower()
                    if system == "windows" and ("windows" in name or ".exe" in name):
                        download_url = asset.get("browser_download_url")
                        break
                    elif system == "linux" and "linux" in name:
                        download_url = asset.get("browser_download_url")
                        break

                release = ReleaseInfo(
                    version=self.parse_version(tag_name),
                    tag_name=tag_name,
                    body=data.get("body", ""),
                    html_url=data.get("html_url", GITHUB_RELEASES_URL),
                    download_url=download_url,
                    is_newer=is_newer
                )
                callback(release, None)
            except Exception as e:
                callback(None, str(e))

        threading.Thread(target=_check, daemon=True).start()

    @staticmethod
    def open_releases_page():
        """在浏览器中打开 GitHub releases 页面"""
        webbrowser.open(GITHUB_RELEASES_URL)
