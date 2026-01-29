"""
XMP 选项卡
展示和编辑 XMP 配置
"""

import customtkinter as ctk
from typing import Dict, Any, Tuple, Optional
import math

from ..widgets.editable_field import EditableField
from ..widgets.xmp_edit_dialog import XMPEditDialog
from ...core.model import SPDDataModel, DataChangeEvent
from ...core.parser import DDR4Parser
from ...utils.constants import Colors, SPD_BYTES, XMP_PROFILE_OFFSETS, MTB, FTB


class XMPTab(ctk.CTkFrame):
    """XMP 选项卡"""

    def __init__(self, master, data_model: SPDDataModel, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.data_model = data_model
        self.profile_cards: Dict[int, Dict[str, Any]] = {}
        self._refresh_job: Optional[str] = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._setup_ui()
        self.data_model.add_observer(self._on_data_changed)

    def _setup_ui(self):
        """设置UI"""
        # 头部：XMP 状态
        header_frame = ctk.CTkFrame(self, fg_color=Colors.CARD_BG, corner_radius=10)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        header_inner = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_inner.pack(fill="x", padx=15, pady=12)

        ctk.CTkLabel(
            header_inner,
            text="XMP 状态",
            font=("Arial", 14, "bold")
        ).pack(side="left")

        self.xmp_status_label = ctk.CTkLabel(
            header_inner,
            text="未知",
            font=("Arial", 12),
            text_color=Colors.TEXT_SECONDARY
        )
        self.xmp_status_label.pack(side="left", padx=(20, 0))

        self.xmp_version_label = ctk.CTkLabel(
            header_inner,
            text="",
            font=("Arial", 11),
            text_color=Colors.TEXT_SECONDARY
        )
        self.xmp_version_label.pack(side="right")

        # Profile 容器
        self.profiles_container = ctk.CTkFrame(self, fg_color="transparent")
        self.profiles_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.profiles_container.grid_columnconfigure(0, weight=1)
        self.profiles_container.grid_columnconfigure(1, weight=1)

        # 无 XMP 提示
        self.no_xmp_label = ctk.CTkLabel(
            self.profiles_container,
            text="此内存不支持 XMP 或未检测到 XMP 配置",
            font=("Arial", 12),
            text_color=Colors.TEXT_SECONDARY
        )
        self.no_xmp_label.grid(row=0, column=0, columnspan=2, pady=50)

        # Profile 卡片（固定创建，刷新时只更新内容，避免频繁 destroy 导致 CustomTkinter 内部回调崩溃）
        self.profile_cards[1] = self._build_profile_card(1)
        self.profile_cards[2] = self._build_profile_card(2)

        self.profile_cards[1]["frame"].grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.profile_cards[2]["frame"].grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # 初始隐藏，等解析到支持 XMP 后再显示
        self.profile_cards[1]["frame"].grid_remove()
        self.profile_cards[2]["frame"].grid_remove()

    def _build_profile_card(self, profile_num: int) -> Dict[str, Any]:
        """创建 Profile 显示卡片（固定复用）"""
        frame = ctk.CTkFrame(self.profiles_container, fg_color=Colors.CARD_BG, corner_radius=10)

        # 标题
        title_frame = ctk.CTkFrame(frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(12, 8))

        ctk.CTkLabel(
            title_frame,
            text=f"Profile {profile_num}",
            font=("Arial", 14, "bold")
        ).pack(side="left")

        # 频率标签
        freq_label = ctk.CTkLabel(
            title_frame,
            text="-",
            font=("Arial", 12, "bold"),
            text_color=Colors.HIGHLIGHT
        )
        freq_label.pack(side="right", padx=(0, 10))

        # 编辑按钮 / 创建按钮（二选一显示）
        edit_btn = ctk.CTkButton(
            title_frame,
            text="编辑",
            width=60,
            height=24,
            font=("Arial", 10),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.HIGHLIGHT,
            command=lambda p=profile_num: self._on_edit_profile_by_num(p)
        )
        edit_btn.pack(side="right")

        create_btn = ctk.CTkButton(
            title_frame,
            text="创建",
            width=60,
            height=24,
            font=("Arial", 10),
            fg_color=Colors.SUCCESS,
            hover_color=Colors.HIGHLIGHT,
            command=lambda p=profile_num: self._on_create_profile(p)
        )
        # 默认先隐藏，等刷新时决定显示哪个
        create_btn.pack_forget()

        # 分隔线
        separator = ctk.CTkFrame(frame, height=1, fg_color=Colors.SECONDARY)
        separator.pack(fill="x", padx=15)

        # 内容
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=10)
        content_frame.grid_columnconfigure(1, weight=1)

        value_labels: Dict[str, ctk.CTkLabel] = {}
        rows = [
            ("frequency", "频率:"),
            ("voltage", "电压:"),
            ("timings", "时序:"),
        ]

        for i, (key, label_text) in enumerate(rows):
            ctk.CTkLabel(
                content_frame,
                text=label_text,
                font=("Arial", 11),
                text_color=Colors.TEXT_SECONDARY
            ).grid(row=i, column=0, sticky="w", pady=3)

            value_label = ctk.CTkLabel(
                content_frame,
                text="-",
                font=("Arial", 11),
                text_color=Colors.TEXT
            )
            value_label.grid(row=i, column=1, sticky="w", padx=(10, 0), pady=3)
            value_labels[key] = value_label

        return {
            "frame": frame,
            "freq_label": freq_label,
            "edit_btn": edit_btn,
            "create_btn": create_btn,
            "value_labels": value_labels,
            "data": None,
        }

    def _on_data_changed(self, event: DataChangeEvent):
        """数据变更回调"""
        # 写入/批量修改会触发大量 BYTE_CHANGED 事件，这里做一次合并刷新，避免 UI 抖动或内部回调竞态
        if self._refresh_job:
            try:
                self.after_cancel(self._refresh_job)
            except Exception:
                pass
        self._refresh_job = self.after(50, self._run_scheduled_refresh)

    def _run_scheduled_refresh(self):
        self._refresh_job = None
        if not self.winfo_exists():
            return
        self.refresh()

    def _on_edit_profile_by_num(self, profile_num: int):
        card = self.profile_cards.get(profile_num)
        if not card:
            return
        profile_data = card.get("data")
        if not profile_data:
            return
        self._on_edit_profile(profile_num, profile_data)

    def refresh(self):
        """刷新显示"""
        # 默认先隐藏 Profile 卡片，等确认支持 XMP 再显示
        if 1 in self.profile_cards:
            self.profile_cards[1]["frame"].grid_remove()
        if 2 in self.profile_cards:
            self.profile_cards[2]["frame"].grid_remove()

        if not self.data_model.has_data:
            self._show_no_xmp()
            return

        parser = DDR4Parser(self.data_model.data)
        info = parser.to_dict()

        if "error" in info:
            self._show_no_xmp()
            return

        xmp = info.get("xmp", {})

        if not xmp.get("supported"):
            self._show_no_xmp()
            return

        # 显示 XMP 支持
        self.no_xmp_label.grid_remove()

        self.xmp_status_label.configure(
            text="支持",
            text_color=Colors.SUCCESS
        )
        self.xmp_version_label.configure(
            text=f"XMP {xmp.get('version', '-')}"
        )

        profiles = xmp.get("profiles", [])
        profiles_by_num: Dict[int, Dict[str, Any]] = {}
        for profile in profiles:
            num = int(profile.get("profile_num", 0) or 0)
            if num in (1, 2):
                profiles_by_num[num] = profile

        # Profile 1/2 都显示出来：存在则可编辑，不存在则可创建
        for profile_num in (1, 2):
            card = self.profile_cards.get(profile_num)
            if not card:
                continue

            profile_data = profiles_by_num.get(profile_num)
            card["data"] = profile_data

            frame = card["frame"]
            freq_label = card["freq_label"]
            edit_btn = card["edit_btn"]
            create_btn = card["create_btn"]
            value_labels = card["value_labels"]

            if profile_data:
                freq = profile_data.get("frequency", 0)
                freq_label.configure(text=f"{freq} MT/s" if freq else "-")
                value_labels["frequency"].configure(text=f"{profile_data.get('frequency', '-')} MT/s")
                value_labels["voltage"].configure(text=f"{profile_data.get('voltage', 0):.3f}V")
                value_labels["timings"].configure(text=profile_data.get("timings", "-"))

                create_btn.pack_forget()
                if not edit_btn.winfo_ismapped():
                    edit_btn.pack(side="right")
            else:
                freq_label.configure(text="-")
                value_labels["frequency"].configure(text="-")
                value_labels["voltage"].configure(text="-")
                value_labels["timings"].configure(text="(未启用)")

                edit_btn.pack_forget()
                if not create_btn.winfo_ismapped():
                    create_btn.pack(side="right")

            frame.grid()

    def _show_no_xmp(self):
        """显示无 XMP 状态"""
        self.xmp_status_label.configure(
            text="不支持",
            text_color=Colors.TEXT_SECONDARY
        )
        self.xmp_version_label.configure(text="")
        self.no_xmp_label.configure(text="未检测到 XMP 配置（可手动创建）")
        self.no_xmp_label.grid(row=1, column=0, columnspan=2, pady=(15, 5))

        # 有 SPD 数据时，允许用户手动创建 Profile（不会自动添加）
        if self.data_model.has_data:
            for profile_num in (1, 2):
                card = self.profile_cards.get(profile_num)
                if not card:
                    continue

                card["data"] = None
                card["freq_label"].configure(text="-")
                card["value_labels"]["frequency"].configure(text="-")
                card["value_labels"]["voltage"].configure(text="-")
                card["value_labels"]["timings"].configure(text="(未启用)")

                card["edit_btn"].pack_forget()
                if not card["create_btn"].winfo_ismapped():
                    card["create_btn"].pack(side="right")

                card["frame"].grid()

    def _on_edit_profile(self, profile_num: int, profile_data: Dict):
        """编辑 XMP Profile"""
        if not self.data_model.has_data:
            return

        # 打开编辑对话框
        XMPEditDialog(
            self.winfo_toplevel(),
            profile_num=profile_num,
            existing_data=profile_data,
            on_save=lambda pnum, data: self._write_xmp_profile(pnum, data)
        )

    def _on_create_profile(self, profile_num: int):
        """创建新的 XMP Profile"""
        if not self.data_model.has_data:
            return

        template_data = None
        if profile_num == 2:
            template_data = (self.profile_cards.get(1) or {}).get("data")

        # 打开编辑对话框 (existing_data=None 表示创建新配置)
        XMPEditDialog(
            self.winfo_toplevel(),
            profile_num=profile_num,
            existing_data=None,
            template_data=template_data,
            on_save=lambda pnum, data: self._write_xmp_profile(pnum, data, is_new=True)
        )

    def _write_xmp_profile(self, profile_num: int, data: Dict, is_new: bool = False):
        """写入 XMP Profile 到 SPD 数据"""
        changed_keys = set(data.get("__changed_keys", []) or [])
        if not is_new and not changed_keys:
            return
        # 如果是新建 Profile，先初始化 XMP 头部
        if is_new:
            # 检查是否已有 XMP 头部
            xmp_header = self.data_model.get_byte(SPD_BYTES.XMP_HEADER)
            if xmp_header != 0x0C:
                # 初始化 XMP 头部
                self.data_model.set_byte(SPD_BYTES.XMP_HEADER, 0x0C)
                self.data_model.set_byte(SPD_BYTES.XMP_HEADER + 1, 0x4A)  # 'J'
                self.data_model.set_byte(SPD_BYTES.XMP_REVISION, 0x20)  # XMP 2.0

        # 计算 Profile 偏移
        profile_offset = SPD_BYTES.XMP_PROFILE1_START if profile_num == 1 else SPD_BYTES.XMP_PROFILE2_START

        # 新建 Profile2 时，优先以 Profile1 作为模板拷贝一份，避免遗漏/破坏未建模字段
        if is_new and profile_num == 2:
            try:
                p1_voltage = self.data_model.get_byte(SPD_BYTES.XMP_PROFILE1_START)
                if (p1_voltage & 0x80) != 0 and p1_voltage not in (0x00, 0xFF):
                    profile_len = SPD_BYTES.XMP_PROFILE2_START - SPD_BYTES.XMP_PROFILE1_START  # 47 bytes
                    for i in range(max(0, int(profile_len))):
                        self.data_model.set_byte(
                            SPD_BYTES.XMP_PROFILE2_START + i,
                            self.data_model.get_byte(SPD_BYTES.XMP_PROFILE1_START + i),
                        )
            except Exception:
                # 模板拷贝失败不影响后续写入（仍按用户输入写入关键字段）
                pass

        def _signed_byte_to_u8(value: int) -> int:
            return value & 0xFF

        def _u8_to_signed(value: int) -> int:
            return value if value < 128 else value - 256

        def _ceil_div(numerator: int, denominator: int) -> int:
            if denominator <= 0:
                return 0
            return (numerator + denominator - 1) // denominator

        def _encode_time_ps_to_mtb_ftb_u8(time_ps: int) -> Tuple[int, int]:
            """
            将 ps 编码为 (MTB, FTB) 形式：time = mtb*125ps + ftb*1ps

            注意：XMP 的 FTB 为 signed int8，但这里优先生成 0..124 的正值，避免不必要的负值。
            """
            if time_ps <= 0:
                return 0, 0

            mtb_value = time_ps // MTB
            ftb_value = int(time_ps - mtb_value * MTB)

            if mtb_value > 0xFF:
                # 超出 1 字节 MTB 可表示范围，回退到最大可表示值
                return 0xFF, 0

            # ftb_value 理论上在 0..124；仍做保护
            if ftb_value > 127:
                ftb_value = 127
            elif ftb_value < -128:
                ftb_value = -128

            return int(mtb_value), _signed_byte_to_u8(ftb_value)

        def _encode_time_ps_to_mtb12_ftb_u8(time_ps: int) -> Tuple[int, int]:
            """
            将 ps 编码为 (12-bit MTB, FTB) 形式：time = mtb12*125ps + ftb*1ps
            """
            if time_ps <= 0:
                return 0, 0

            mtb_value = time_ps // MTB
            ftb_value = int(time_ps - mtb_value * MTB)

            if mtb_value > 0xFFF:
                return 0xFFF, 0

            if ftb_value > 127:
                ftb_value = 127
            elif ftb_value < -128:
                ftb_value = -128

            return int(mtb_value), _signed_byte_to_u8(ftb_value)

        def _encode_cycles_to_mtb(cycles: int, tck_ps: int, max_mtb: int) -> int:
            """
            将 cycles 编码为 MTB 整数（无 FTB）

            目标：尽量保持解析回来的 cycles 不变（ceil(time/tCK)）。
            """
            if cycles <= 0 or tck_ps <= 0:
                return 0

            # 找到能保证 ceil((mtb*MTB)/tCK) >= cycles 的最小 mtb
            time_min_ps = (cycles - 1) * tck_ps + 1  # strictly greater than (cycles-1)*tCK
            mtb_value = int(math.ceil(time_min_ps / MTB))
            mtb_value = max(0, min(int(max_mtb), mtb_value))

            # 如果由于 clamp 导致 cycles 不够，向上补齐
            while mtb_value < max_mtb and _ceil_div(mtb_value * MTB, tck_ps) < cycles:
                mtb_value += 1

            # 尽量向下收敛，保持 cycles 不变（减小编码值）
            while mtb_value > 0 and _ceil_div((mtb_value - 1) * MTB, tck_ps) == cycles:
                mtb_value -= 1

            return int(mtb_value)

        # 频率 -> tCK (MTB+FTB)
        freq_mt_s = int(data.get("frequency", 3200))
        frequency_changed = is_new or ("frequency" in changed_keys)

        # “只改其它字段”时，优先使用 SPD 中已有的 tCK（避免吸附/取整造成不必要漂移）
        current_tck_mtb = self.data_model.get_byte(profile_offset + XMP_PROFILE_OFFSETS.TCK_MTB)
        current_tck_ftb_raw = self.data_model.get_byte(profile_offset + XMP_PROFILE_OFFSETS.TCK_FTB)
        current_tck_ftb = _u8_to_signed(current_tck_ftb_raw)
        current_tck_ps = current_tck_mtb * MTB + current_tck_ftb * FTB

        if frequency_changed or current_tck_ps <= 0:
            tck_ps_exact = 2000000 / max(1, freq_mt_s)  # 2000000 ps / MT/s

            # XMP 的 tCK/时序以 1ps 为分辨率，选取最接近目标频点的整数 ps
            tck_ps_floor = max(1, int(tck_ps_exact // 1))
            tck_ps_ceil = max(1, tck_ps_floor if abs(tck_ps_exact - tck_ps_floor) < 1e-9 else tck_ps_floor + 1)

            def _freq_error(ps: int) -> float:
                return abs((2000000 / ps) - freq_mt_s)

            tck_ps = tck_ps_floor if _freq_error(tck_ps_floor) <= _freq_error(tck_ps_ceil) else tck_ps_ceil
            tck_mtb = int(tck_ps // MTB)
            tck_ftb = int(tck_ps - tck_mtb * MTB)  # 0..124
        else:
            tck_ps = int(current_tck_ps)
            tck_mtb = int(current_tck_mtb)
            tck_ftb = int(current_tck_ftb)

        # 电压编码: bit7 = enabled, bits6:0 为 10mV 步进
        voltage = data.get("voltage", 1.350)
        voltage_code = int(round((voltage - 1.0) * 100))  # 10mV steps from 1.00V
        voltage_code = max(0, min(0x7F, voltage_code))
        voltage_byte = 0x80 | (voltage_code & 0x7F)  # Set bit 7 (enabled) + voltage

        # CL/tRCD/tRP/tRAS 时序 (从对话框获取的是周期数)
        cl = data.get("CL", 16)
        trcd_cycles = data.get("tRCD", 18)
        trp_cycles = data.get("tRP", 18)
        tras_cycles = data.get("tRAS", 38)
        trc_cycles_input = int(data.get("tRC", 0) or 0)

        # 转换为 MTB/FTB：time(ps) = cycles * tCK(ps)
        taa_ps = int(cl * tck_ps)
        trcd_ps = int(trcd_cycles * tck_ps)
        trp_ps = int(trp_cycles * tck_ps)
        tras_ps = int(tras_cycles * tck_ps)

        taa_mtb, taa_ftb_u8 = _encode_time_ps_to_mtb_ftb_u8(taa_ps)
        trcd_mtb, trcd_ftb_u8 = _encode_time_ps_to_mtb_ftb_u8(trcd_ps)
        trp_mtb, trp_ftb_u8 = _encode_time_ps_to_mtb_ftb_u8(trp_ps)

        tras_mtb = int(tras_ps // MTB)
        if tras_mtb > 0xFFF:
            tras_mtb = 0xFFF

        # 写入 Profile 数据 (根据 XMP 2.0 规范)
        # Offset +0: 电压
        if is_new or ("voltage" in changed_keys):
            self.data_model.set_byte(profile_offset + XMP_PROFILE_OFFSETS.VDD_VOLTAGE, voltage_byte)

        # Offset +3: tCK (MTB)
        if frequency_changed:
            self.data_model.set_byte(profile_offset + XMP_PROFILE_OFFSETS.TCK_MTB, tck_mtb)
            # Offset +38: tCK (FTB, signed)
            self.data_model.set_byte(profile_offset + XMP_PROFILE_OFFSETS.TCK_FTB, _signed_byte_to_u8(tck_ftb))

        # Offset +8/+34: tAA (MTB/FTB)
        if frequency_changed or ("CL" in changed_keys):
            self.data_model.set_byte(profile_offset + XMP_PROFILE_OFFSETS.TAA_MTB, taa_mtb)
            self.data_model.set_byte(profile_offset + XMP_PROFILE_OFFSETS.TAA_FTB, taa_ftb_u8)

        # Offset +9/+35: tRCD (MTB/FTB)
        if frequency_changed or ("tRCD" in changed_keys):
            self.data_model.set_byte(profile_offset + XMP_PROFILE_OFFSETS.TRCD_MTB, trcd_mtb)
            self.data_model.set_byte(profile_offset + XMP_PROFILE_OFFSETS.TRCD_FTB, trcd_ftb_u8)

        # Offset +10/+36: tRP (MTB/FTB)
        if frequency_changed or ("tRP" in changed_keys):
            self.data_model.set_byte(profile_offset + XMP_PROFILE_OFFSETS.TRP_MTB, trp_mtb)
            self.data_model.set_byte(profile_offset + XMP_PROFILE_OFFSETS.TRP_FTB, trp_ftb_u8)

        # Offset +11-13: tRAS/tRC (12-bit: upper 4 bits in byte 11, lower 8 bits in byte 12/13)
        # Byte11: [tRC upper nibble | tRAS upper nibble]
        tras_upper = (tras_mtb >> 8) & 0x0F

        should_write_tras = is_new or frequency_changed or ("tRAS" in changed_keys)
        should_write_trc = is_new or frequency_changed or ("tRC" in changed_keys)

        # tRC：对现有 Profile，若用户输入 0 则保留原值；否则写入用户指定值
        if should_write_trc and (trc_cycles_input > 0 or is_new):
            trc_cycles = trc_cycles_input if trc_cycles_input > 0 else int(tras_cycles + trp_cycles)
            trc_ps = int(trc_cycles * tck_ps)
            trc_mtb, trc_ftb_u8 = _encode_time_ps_to_mtb12_ftb_u8(trc_ps)
            trc_upper = (trc_mtb >> 8) & 0x0F
            new_byte11 = (trc_upper << 4) | tras_upper
            self.data_model.set_byte(profile_offset + XMP_PROFILE_OFFSETS.TRAS_TRC_HIGH, new_byte11)
            self.data_model.set_byte(profile_offset + XMP_PROFILE_OFFSETS.TRC_MTB_LOW, trc_mtb & 0xFF)
            self.data_model.set_byte(profile_offset + XMP_PROFILE_OFFSETS.TRC_FTB, trc_ftb_u8)
        elif should_write_tras:
            # 保留 tRC nibble，只更新 tRAS nibble
            existing_byte11 = self.data_model.get_byte(profile_offset + XMP_PROFILE_OFFSETS.TRAS_TRC_HIGH)
            new_byte11 = (existing_byte11 & 0xF0) | tras_upper
            if existing_byte11 != new_byte11:
                self.data_model.set_byte(profile_offset + XMP_PROFILE_OFFSETS.TRAS_TRC_HIGH, new_byte11)

        if should_write_tras:
            self.data_model.set_byte(profile_offset + XMP_PROFILE_OFFSETS.TRAS_MTB_LOW, tras_mtb & 0xFF)

        # 确保所选 CL 在 XMP Profile 的 CAS Latencies bitmap 中标记为支持（不清除其它位）
        if is_new or frequency_changed or ("CL" in changed_keys):
            cl_bit = int(cl) - 7
            if 0 <= cl_bit < 24:
                cas_offsets = [
                    XMP_PROFILE_OFFSETS.CAS_LATENCIES_0,
                    XMP_PROFILE_OFFSETS.CAS_LATENCIES_1,
                    XMP_PROFILE_OFFSETS.CAS_LATENCIES_2,
                ]
                byte_idx = cl_bit // 8
                bit_idx = cl_bit % 8
                cas_off = cas_offsets[byte_idx]
                current = self.data_model.get_byte(profile_offset + cas_off)
                self.data_model.set_byte(profile_offset + cas_off, current | (1 << bit_idx))

        # ===== 进阶时序（0 表示保留现状；新建时 0 则保持为 0） =====
        def _maybe_write_u8(key: str, rel_offset: int, max_mtb: int = 0xFF, force: bool = False):
            if not force:
                return
            value_cycles = int(data.get(key, 0) or 0)
            if value_cycles <= 0 and not is_new:
                return
            mtb_value = _encode_cycles_to_mtb(value_cycles, tck_ps, max_mtb) if value_cycles > 0 else 0
            self.data_model.set_byte(profile_offset + rel_offset, mtb_value & 0xFF)

        def _maybe_write_u12(key: str, rel_offset_high: int, rel_offset_low: int, preserve_high_nibble: bool = True, force: bool = False):
            if not force:
                return
            value_cycles = int(data.get(key, 0) or 0)
            if value_cycles <= 0 and not is_new:
                return
            mtb_value = _encode_cycles_to_mtb(value_cycles, tck_ps, 0xFFF) if value_cycles > 0 else 0
            high_nibble = (mtb_value >> 8) & 0x0F
            if preserve_high_nibble:
                existing = self.data_model.get_byte(profile_offset + rel_offset_high)
                new_high = (existing & 0xF0) | high_nibble
            else:
                new_high = high_nibble
            self.data_model.set_byte(profile_offset + rel_offset_high, new_high)
            self.data_model.set_byte(profile_offset + rel_offset_low, mtb_value & 0xFF)

        def _maybe_write_u16(key: str, rel_offset_low: int, rel_offset_high: int, force: bool = False):
            if not force:
                return
            value_cycles = int(data.get(key, 0) or 0)
            if value_cycles <= 0 and not is_new:
                return
            mtb_value = _encode_cycles_to_mtb(value_cycles, tck_ps, 0xFFFF) if value_cycles > 0 else 0
            self.data_model.set_byte(profile_offset + rel_offset_low, mtb_value & 0xFF)
            self.data_model.set_byte(profile_offset + rel_offset_high, (mtb_value >> 8) & 0xFF)

        # tRFC1/2/4 (u16 MTB)
        _maybe_write_u16("tRFC1", XMP_PROFILE_OFFSETS.TRFC1_LOW, XMP_PROFILE_OFFSETS.TRFC1_HIGH, force=(is_new or frequency_changed or ("tRFC1" in changed_keys)))
        _maybe_write_u16("tRFC2", XMP_PROFILE_OFFSETS.TRFC2_LOW, XMP_PROFILE_OFFSETS.TRFC2_HIGH, force=(is_new or frequency_changed or ("tRFC2" in changed_keys)))
        _maybe_write_u16("tRFC4", XMP_PROFILE_OFFSETS.TRFC4_LOW, XMP_PROFILE_OFFSETS.TRFC4_HIGH, force=(is_new or frequency_changed or ("tRFC4" in changed_keys)))

        # tFAW (u12 MTB)
        _maybe_write_u12("tFAW", XMP_PROFILE_OFFSETS.TFAW_HIGH, XMP_PROFILE_OFFSETS.TFAW_LOW, preserve_high_nibble=True, force=(is_new or frequency_changed or ("tFAW" in changed_keys)))

        # tRRD_S/L (u8 MTB)
        _maybe_write_u8("tRRD_S", XMP_PROFILE_OFFSETS.TRRD_S_MIN, force=(is_new or frequency_changed or ("tRRD_S" in changed_keys)))
        _maybe_write_u8("tRRD_L", XMP_PROFILE_OFFSETS.TRRD_L_MIN, force=(is_new or frequency_changed or ("tRRD_L" in changed_keys)))

        # 实验性字段：仅在对话框显式开启时才写入，默认完全不触碰（避免与外部工具解析冲突）
        if bool(data.get("__experimental_fields")):
            _maybe_write_u8("tCCD_L", XMP_PROFILE_OFFSETS.TCCD_L_MIN, force=("tCCD_L" in changed_keys))
            _maybe_write_u8("tWTR_S", XMP_PROFILE_OFFSETS.TWTR_S_MIN, force=("tWTR_S" in changed_keys))
            _maybe_write_u8("tWTR_L", XMP_PROFILE_OFFSETS.TWTR_L_MIN, force=("tWTR_L" in changed_keys))

        # tWR (u12 MTB)
        _maybe_write_u12("tWR", XMP_PROFILE_OFFSETS.TWR_HIGH, XMP_PROFILE_OFFSETS.TWR_LOW, preserve_high_nibble=True, force=(is_new or frequency_changed or ("tWR" in changed_keys)))

        # 启用 Profile (设置 Profile 启用位)
        profile_enabled = self.data_model.get_byte(SPD_BYTES.XMP_PROFILE_ENABLED)
        if profile_num == 1:
            profile_enabled |= 0x01
        else:
            profile_enabled |= 0x02
        self.data_model.set_byte(SPD_BYTES.XMP_PROFILE_ENABLED, profile_enabled)

        # Refresh will be triggered automatically by data model observer
