"""
XMP 配置文件编辑/创建对话框
"""
import customtkinter as ctk
from typing import Dict, Callable, Optional
from ...utils.constants import Colors, MTB
from ...utils.timing_validator import validate_timing, RiskLevel, RISK_COLORS


class XMPEditDialog(ctk.CTkToplevel):
    """XMP 配置文件编辑/创建对话框"""

    def __init__(
        self,
        parent,
        profile_num: int,
        existing_data: Optional[Dict] = None,
        template_data: Optional[Dict] = None,
        on_save: Callable[[int, Dict], None] = None
    ):
        """
        Args:
            profile_num: 配置文件编号 (1 或 2)
            existing_data: 现有数据 (None 表示创建新配置)
            on_save: 保存回调 callback(profile_num, data_dict)
        """
        super().__init__(parent)

        self.profile_num = profile_num
        self.existing_data = existing_data
        self.template_data = template_data if existing_data is None else None
        self.on_save = on_save
        self.is_create = existing_data is None

        title = f"创建 XMP Profile {profile_num}" if self.is_create else f"编辑 XMP Profile {profile_num}"
        self.title(title)
        self.geometry("560x780")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._setup_ui()
        # 记录初始值，用于判断哪些字段被用户修改
        self._original_values = self._get_values(include_change_keys=False) or {}
        self._update_preview()

    def _setup_ui(self):
        """设置UI"""
        seed = self.existing_data or self.template_data or {}

        # 头部
        header_text = "创建新的 XMP 配置文件" if self.is_create else "编辑 XMP 配置文件"
        ctk.CTkLabel(
            self,
            text=header_text,
            font=("Arial", 16, "bold")
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            self,
            text=f"Profile {self.profile_num}",
            font=("Arial", 12),
            text_color=Colors.HIGHLIGHT
        ).pack(pady=(0, 15))

        # 表单字段（滚动区域，避免参数变多后挤爆窗口）
        form = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30, pady=10)
        form.grid_columnconfigure(0, weight=1)

        self.fields = {}

        row = 0

        # 分组：基础参数
        row = self._add_section_title(form, "基础参数", row)

        # 频率 (MT/s)
        self._add_field(
            form, "frequency", "频率 (MT/s)",
            default=seed.get("frequency", 3200),
            min_val=1600, max_val=6000, row=row
        )
        row += 1

        # 电压 (V)
        self._add_field(
            form, "voltage", "电压 (V)",
            default=seed.get("voltage", 1.35),
            min_val=1.10, max_val=1.50, row=row, is_float=True
        )
        row += 1

        # CL
        self._add_field(
            form, "CL", "CAS Latency (CL)",
            default=seed.get("CL", 16),
            min_val=10, max_val=40, row=row
        )
        row += 1

        # tRCD
        self._add_field(
            form, "tRCD", "tRCD (cycles)",
            default=seed.get("tRCD", 18),
            min_val=10, max_val=80, row=row
        )
        row += 1

        # tRP
        self._add_field(
            form, "tRP", "tRP (cycles)",
            default=seed.get("tRP", 18),
            min_val=10, max_val=80, row=row
        )
        row += 1

        # tRAS
        self._add_field(
            form, "tRAS", "tRAS (cycles)",
            default=seed.get("tRAS", 36),
            min_val=20, max_val=200, row=row
        )
        row += 1

        # tRC
        default_trc = 0
        if seed:
            default_trc = int(seed.get("tRC", 0) or 0)
        if not default_trc:
            default_trc = 36 + 18  # 默认 tRC≈tRAS+tRP（仅用于新建时的占位）

        self._add_field(
            form, "tRC", "tRC (cycles)",
            default=default_trc,
            min_val=0, max_val=400, row=row
        )
        row += 1

        # 分组：高级时序
        row = self._add_section_title(form, "高级时序", row, pady_top=12)

        # 高级时序（很多内存会把这些留空为 0；因此 min_val 允许 0，用于保留原始状态）
        self._add_field(
            form, "tRFC1", "tRFC1 (cycles)",
            default=int(seed.get("tRFC1", 0) or 0),
            min_val=0, max_val=10000, row=row
        )
        row += 1
        self._add_field(
            form, "tRFC2", "tRFC2 (cycles)",
            default=int(seed.get("tRFC2", 0) or 0),
            min_val=0, max_val=10000, row=row
        )
        row += 1
        self._add_field(
            form, "tRFC4", "tRFC4 (cycles)",
            default=int(seed.get("tRFC4", 0) or 0),
            min_val=0, max_val=10000, row=row
        )
        row += 1
        self._add_field(
            form, "tFAW", "tFAW (cycles)",
            default=int(seed.get("tFAW", 0) or 0),
            min_val=0, max_val=256, row=row
        )
        row += 1
        self._add_field(
            form, "tRRD_S", "tRRD_S (cycles)",
            default=int(seed.get("tRRD_S", 0) or 0),
            min_val=0, max_val=64, row=row
        )
        row += 1
        self._add_field(
            form, "tRRD_L", "tRRD_L (cycles)",
            default=int(seed.get("tRRD_L", 0) or 0),
            min_val=0, max_val=128, row=row
        )
        row += 1
        self._add_field(
            form, "tWR", "tWR (cycles)",
            default=int(seed.get("tWR", 0) or 0),
            min_val=0, max_val=512, row=row
        )
        row += 1

        # 实验性字段：默认隐藏（部分工具/规格未明确列出，开启后才写入）
        self._experimental_field_keys = ["tCCD_L", "tWTR_S", "tWTR_L"]
        self._show_experimental_fields = ctk.BooleanVar(value=False)
        exp_toggle = ctk.CTkCheckBox(
            form,
            text="显示实验性字段（可能与台风/CPU‑Z 不一致）",
            variable=self._show_experimental_fields,
            command=self._toggle_experimental_fields,
        )
        exp_toggle.grid(row=row, column=0, sticky="w", pady=(10, 6))
        row += 1

        self._add_field(
            form, "tCCD_L", "tCCD_L (cycles) [实验]",
            default=int(seed.get("tCCD_L", 0) or 0),
            min_val=0, max_val=128, row=row, experimental=True
        )
        row += 1
        self._add_field(
            form, "tWTR_S", "tWTR_S (cycles) [实验]",
            default=int(seed.get("tWTR_S", 0) or 0),
            min_val=0, max_val=128, row=row, experimental=True
        )
        row += 1
        self._add_field(
            form, "tWTR_L", "tWTR_L (cycles) [实验]",
            default=int(seed.get("tWTR_L", 0) or 0),
            min_val=0, max_val=256, row=row, experimental=True
        )

        # 默认隐藏实验性字段
        self._toggle_experimental_fields()

        # 预览
        self.preview_frame = ctk.CTkFrame(self, fg_color=Colors.CARD_BG, corner_radius=8)
        self.preview_frame.pack(fill="x", padx=30, pady=15)

        ctk.CTkLabel(
            self.preview_frame,
            text="预览",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="",
            font=("Consolas", 14),
            text_color=Colors.HIGHLIGHT
        )
        self.preview_label.pack(anchor="w", padx=15, pady=(0, 10))

        # 风险指示
        self.risk_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 11),
            wraplength=400
        )
        self.risk_label.pack(pady=5)

        # 按钮
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="取消",
            width=100,
            fg_color=Colors.SECONDARY,
            command=self.destroy
        ).pack(side="left")

        save_text = "创建" if self.is_create else "保存"
        self.save_btn = ctk.CTkButton(
            btn_frame,
            text=save_text,
            width=100,
            command=self._save
        )
        self.save_btn.pack(side="right")

    def _add_section_title(self, parent, title: str, row: int, pady_top: int = 6) -> int:
        """添加分组标题"""
        ctk.CTkLabel(
            parent,
            text=title,
            font=("Arial", 13, "bold"),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
        ).grid(row=row, column=0, sticky="ew", pady=(pady_top, 6))
        return row + 1

    def _add_field(self, parent, key, label, default, min_val, max_val, row, is_float=False, experimental: bool = False):
        """添加输入字段"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.grid(row=row, column=0, sticky="ew", pady=4)

        # 统一列布局：label 左侧，右侧为 entry + hint，避免 hint 长度变化导致 entry 横向漂移
        field_frame.grid_columnconfigure(0, weight=0)
        field_frame.grid_columnconfigure(1, weight=1)  # spacer
        field_frame.grid_columnconfigure(2, weight=0)  # entry
        field_frame.grid_columnconfigure(3, weight=0)  # hint

        ctk.CTkLabel(
            field_frame,
            text=label,
            width=170,
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        entry = ctk.CTkEntry(field_frame, width=120)
        entry.grid(row=0, column=2, padx=(0, 10), sticky="e")
        entry.insert(0, f"{default:.2f}" if is_float else str(default))
        entry.bind("<KeyRelease>", lambda e: self._update_preview())

        hint = f"({min_val}-{max_val})"
        ctk.CTkLabel(
            field_frame,
            text=hint,
            font=("Arial", 10),
            text_color=Colors.TEXT_SECONDARY,
            width=90,
            anchor="e",
        ).grid(row=0, column=3, sticky="e")

        self.fields[key] = {
            "frame": field_frame,
            "entry": entry,
            "min": min_val,
            "max": max_val,
            "is_float": is_float,
            "experimental": experimental,
        }

    def _toggle_experimental_fields(self):
        show = bool(getattr(self, "_show_experimental_fields", None).get()) if hasattr(self, "_show_experimental_fields") else False
        for key in getattr(self, "_experimental_field_keys", []):
            field = self.fields.get(key)
            if not field:
                continue
            frame = field.get("frame")
            if not frame:
                continue
            if show:
                frame.grid()
            else:
                frame.grid_remove()

        # 初始化阶段 preview 组件尚未创建，避免触发异常
        if hasattr(self, "preview_label"):
            self._update_preview()

    def _get_values(self, include_change_keys: bool = True):
        """获取并验证所有字段值"""
        values = {}
        show_experimental = bool(getattr(self, "_show_experimental_fields", None).get()) if hasattr(self, "_show_experimental_fields") else False
        for key, field in self.fields.items():
            if include_change_keys and field.get("experimental") and not show_experimental:
                continue
            try:
                if field["is_float"]:
                    val = float(field["entry"].get())
                else:
                    val = int(field["entry"].get())
                val = max(field["min"], min(field["max"], val))
                values[key] = val
            except ValueError:
                return None

        # 标记被修改的字段（用于写入时尽量保留未改动的原始编码，避免“打开-保存”造成不必要漂移）
        if include_change_keys:
            changed_keys = []
            original = getattr(self, "_original_values", {}) or {}
            for key, val in values.items():
                if key not in original:
                    continue
                orig_val = original[key]
                if isinstance(val, float) or isinstance(orig_val, float):
                    if abs(float(val) - float(orig_val)) > 1e-6:
                        changed_keys.append(key)
                else:
                    if int(val) != int(orig_val):
                        changed_keys.append(key)

            values["__changed_keys"] = changed_keys
            values["__experimental_fields"] = show_experimental
        return values

    def _update_preview(self):
        """更新预览和风险提示"""
        values = self._get_values()
        if values:
            timing_str = f"CL{values['CL']}-{values['tRCD']}-{values['tRP']}-{values['tRAS']}"
            if values.get("tRC", 0):
                timing_str += f"-{values['tRC']}"
            preview = f"{values['frequency']} MT/s @ {values['voltage']:.2f}V ({timing_str})"
            self.preview_label.configure(text=preview)

            # 计算 tCK 并验证时序
            tck_ns = 2000 / values['frequency']
            taa_ns = values['CL'] * tck_ns
            risk, msg = validate_timing("tAA", taa_ns)

            if risk == RiskLevel.SAFE:
                self.risk_label.configure(
                    text="✓ 参数在合理范围内",
                    text_color=RISK_COLORS[risk]
                )
            else:
                # msg already contains emoji prefix from validate_timing
                display_msg = msg if len(msg) <= 80 else msg[:77] + "..."
                self.risk_label.configure(
                    text=display_msg,
                    text_color=RISK_COLORS[risk]
                )

            self.save_btn.configure(state="normal")
        else:
            self.preview_label.configure(text="请输入有效数值")
            self.save_btn.configure(state="disabled")

    def _save(self):
        """保存"""
        values = self._get_values()
        if values and self.on_save:
            self.on_save(self.profile_num, values)
        self.destroy()
