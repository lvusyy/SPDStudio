"""
时序参数编辑对话框（带风险警告）
"""
import customtkinter as ctk
from ...utils.timing_validator import validate_timing, RiskLevel, RISK_COLORS
from ...utils.constants import Colors, MTB, FTB


class TimingEditDialog(ctk.CTkToplevel):
    """时序参数编辑对话框"""

    def __init__(
        self,
        parent,
        param_name: str,
        param_label: str,
        current_value_ns: float,
        on_save
    ):
        super().__init__(parent)

        self.param_name = param_name
        self.param_label = param_label
        self.current_value = current_value_ns
        self.on_save = on_save

        self.title(f"编辑 {param_label}")
        self.geometry("420x350")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._setup_ui()
        self._update_preview()

    def _setup_ui(self):
        """设置UI"""
        # 当前值显示
        ctk.CTkLabel(
            self,
            text=f"当前值: {self.current_value:.3f} ns",
            font=("Arial", 13)
        ).pack(pady=(20, 10))

        # 输入框
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(input_frame, text="新值 (ns):", width=80).pack(side="left")
        self.value_entry = ctk.CTkEntry(input_frame, width=140)
        self.value_entry.pack(side="left", padx=10)
        self.value_entry.insert(0, f"{self.current_value:.3f}")
        self.value_entry.select_range(0, "end")
        self.value_entry.focus()
        self.value_entry.bind("<KeyRelease>", self._on_value_change)
        self.value_entry.bind("<Return>", lambda e: self._save())

        # MTB/FTB 计算显示
        self.mtb_label = ctk.CTkLabel(
            self,
            text="MTB: - | FTB: -",
            font=("Consolas", 11),
            text_color=Colors.TEXT_SECONDARY
        )
        self.mtb_label.pack(pady=5)

        # 风险指示器
        self.risk_frame = ctk.CTkFrame(self, fg_color=Colors.CARD_BG, corner_radius=8)
        self.risk_frame.pack(fill="x", padx=20, pady=15)

        self.risk_indicator = ctk.CTkLabel(
            self.risk_frame,
            text="●",
            font=("Arial", 24)
        )
        self.risk_indicator.pack(side="left", padx=15, pady=15)

        self.risk_message = ctk.CTkLabel(
            self.risk_frame,
            text="",
            font=("Arial", 11),
            wraplength=280,
            justify="left"
        )
        self.risk_message.pack(side="left", fill="both", expand=True, pady=15, padx=(0, 15))

        # 按钮
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="取消",
            width=100,
            fg_color=Colors.SECONDARY,
            command=self.destroy
        ).pack(side="left")

        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="保存",
            width=100,
            command=self._save
        )
        self.save_btn.pack(side="right")

    def _on_value_change(self, event):
        """值变化回调"""
        self._update_preview()

    def _update_preview(self):
        """更新预览和风险提示"""
        try:
            value_ns = float(self.value_entry.get())
            value_ps = value_ns * 1000

            # 计算 MTB 和 FTB
            mtb_value = int(value_ps / MTB)
            ftb_value = int((value_ps - mtb_value * MTB) / FTB)

            # FTB 是有符号的，范围 -128 到 127
            if ftb_value > 127:
                ftb_value = ftb_value - 256
            elif ftb_value < -128:
                ftb_value = ftb_value + 256

            self.mtb_label.configure(text=f"MTB: {mtb_value} | FTB: {ftb_value}")

            # 验证并显示风险
            risk_level, message = validate_timing(self.param_name, value_ns)
            color = RISK_COLORS[risk_level]
            self.risk_indicator.configure(text_color=color)

            if risk_level == RiskLevel.SAFE:
                self.risk_message.configure(
                    text="✓ 参数在安全范围内",
                    text_color=color
                )
            else:
                self.risk_message.configure(text=message, text_color=color)

            self.save_btn.configure(state="normal")

        except ValueError:
            self.mtb_label.configure(text="MTB: - | FTB: -")
            self.risk_message.configure(
                text="请输入有效数值",
                text_color=Colors.TEXT_SECONDARY
            )
            self.save_btn.configure(state="disabled")

    def _save(self):
        """保存"""
        try:
            value_ns = float(self.value_entry.get())
            self.on_save(value_ns)
            self.destroy()
        except ValueError:
            pass
