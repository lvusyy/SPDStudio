"""
更新通知对话框
"""
import customtkinter as ctk
from ...utils.constants import Colors
from ...core.updater import ReleaseInfo, UpdateChecker


class UpdateDialog(ctk.CTkToplevel):
    """更新通知对话框"""

    def __init__(self, parent, release: ReleaseInfo, current_version: str):
        super().__init__(parent)

        self.release = release
        self.current_version = current_version

        self.title("发现新版本")
        self.geometry("450x380")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        # 头部
        ctk.CTkLabel(
            self,
            text="🎉 发现新版本!",
            font=("Arial", 18, "bold"),
            text_color=Colors.SUCCESS
        ).pack(pady=(25, 10))

        # 版本对比
        version_frame = ctk.CTkFrame(self, fg_color=Colors.CARD_BG, corner_radius=8)
        version_frame.pack(fill="x", padx=30, pady=15)

        ctk.CTkLabel(
            version_frame,
            text=f"当前版本: v{self.current_version}",
            font=("Arial", 12)
        ).pack(anchor="w", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            version_frame,
            text=f"最新版本: {self.release.tag_name}",
            font=("Arial", 12, "bold"),
            text_color=Colors.HIGHLIGHT
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # 更新内容
        ctk.CTkLabel(
            self,
            text="更新内容:",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=30, pady=(10, 5))

        notes_frame = ctk.CTkTextbox(self, height=140, font=("Arial", 11), wrap="word")
        notes_frame.pack(fill="x", padx=30, pady=(0, 15))
        notes_frame.insert("1.0", self.release.body or "暂无更新说明")
        notes_frame.configure(state="disabled")

        # 按钮
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=15)

        ctk.CTkButton(
            btn_frame,
            text="稍后提醒",
            width=100,
            fg_color=Colors.SECONDARY,
            command=self.destroy
        ).pack(side="left")

        ctk.CTkButton(
            btn_frame,
            text="前往下载",
            width=120,
            fg_color=Colors.SUCCESS,
            command=self._open_download
        ).pack(side="right")

    def _open_download(self):
        """打开下载页面"""
        UpdateChecker.open_releases_page()
        self.destroy()
