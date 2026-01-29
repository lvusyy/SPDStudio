"""
SPDTools 常量定义
"""

# HID 设备配置
DEFAULT_VID = 0x0483
DEFAULT_PID = 0x1230

# SPD 数据大小
SPD_SIZE = 512
SPD_PAGE_SIZE = 256

# DDR4 SPD 字节偏移定义
class SPD_BYTES:
    # 基本信息 (0-127)
    BYTES_USED = 0          # SPD 使用的字节数
    REVISION = 1            # SPD 修订版本
    DRAM_TYPE = 2           # DRAM 设备类型 (0x0C = DDR4)
    MODULE_TYPE = 3         # 模组类型
    DENSITY_BANKS = 4       # 密度和 Bank 组
    ADDRESSING = 5          # 行列地址位数
    PACKAGE_TYPE = 6        # 封装类型
    OPTIONAL_FEATURES = 7   # 可选功能
    THERMAL_REFRESH = 8     # 热刷新选项
    OTHER_OPTIONAL = 9      # 其他可选功能
    SECONDARY_PACKAGE = 10  # 次要封装类型
    VOLTAGE = 11            # 模组标称电压
    MODULE_ORG = 12         # 模组组织
    BUS_WIDTH = 13          # 模组内存总线宽度
    THERMAL_SENSOR = 14     # 温度传感器

    # 时序参数
    TIMEBASES = 17          # 时间基准
    TCK_MIN = 18            # 最小时钟周期 (MTB)
    TCK_MAX = 19            # 最大时钟周期 (MTB)
    CAS_LATENCIES_1 = 20    # CAS 延迟支持 (第一字节)
    CAS_LATENCIES_2 = 21    # CAS 延迟支持 (第二字节)
    CAS_LATENCIES_3 = 22    # CAS 延迟支持 (第三字节)
    CAS_LATENCIES_4 = 23    # CAS 延迟支持 (第四字节)
    TAA_MIN = 24            # 最小 CAS 延迟时间 (tAA)
    TRCD_MIN = 25           # 最小 RAS 到 CAS 延迟 (tRCD)
    TRP_MIN = 26            # 最小行预充电时间 (tRP)
    TRAS_TRC_HIGH = 27      # tRAS 和 tRC 高位
    TRAS_MIN_LOW = 28       # 最小 Active 到 Precharge (tRAS) 低位
    TRC_MIN_LOW = 29        # 最小 Active 到 Active/Refresh (tRC) 低位
    TRFC1_LOW = 30          # 最小刷新恢复时间 (tRFC1) 低位
    TRFC1_HIGH = 31         # tRFC1 高位
    TRFC2_LOW = 32          # tRFC2 低位
    TRFC2_HIGH = 33         # tRFC2 高位
    TRFC4_LOW = 34          # tRFC4 低位
    TRFC4_HIGH = 35         # tRFC4 高位
    TFAW_HIGH = 36          # tFAW 高位
    TFAW_LOW = 37           # 最小 Four Activate Window (tFAW) 低位
    TRRD_S_MIN = 38         # 最小 tRRD_S
    TRRD_L_MIN = 39         # 最小 tRRD_L
    TCCD_L_MIN = 40         # 最小 tCCD_L
    TWR_MIN_HIGH = 41       # tWR 高位 (bits 11:8)
    TWR_MIN_LOW = 42        # tWR 低位 (bits 7:0)
    # tWTR_S / tWTR_L 为 12-bit：Byte 43 提供高位 nibbles，Byte 44/45 为低位
    TWTR_MIN_HIGH = 43      # tWTR_S/tWTR_L 高位 nibble 组合
    TWTR_S_MIN = 44         # 最小 tWTR_S (低 8 位)
    TWTR_L_MIN = 45         # 最小 tWTR_L (低 8 位)

    # 细粒度时序调整 (FTB)
    TCK_MIN_FTB = 125       # tCK Fine Offset
    TAA_MIN_FTB = 123       # tAA Fine Offset
    TRCD_MIN_FTB = 122      # tRCD Fine Offset
    TRP_MIN_FTB = 121       # tRP Fine Offset
    TRC_MIN_FTB = 120       # tRC Fine Offset

    # 制造商信息 (320-383)
    MANUFACTURER_ID_FIRST = 320   # 制造商 ID (第一字节)
    MANUFACTURER_ID_SECOND = 321  # 制造商 ID (第二字节)
    MANUFACTURING_LOCATION = 322  # 制造地点
    MANUFACTURING_YEAR = 323      # 制造年份
    MANUFACTURING_WEEK = 324      # 制造周
    SERIAL_NUMBER_1 = 325         # 序列号字节 1
    SERIAL_NUMBER_2 = 326         # 序列号字节 2
    SERIAL_NUMBER_3 = 327         # 序列号字节 3
    SERIAL_NUMBER_4 = 328         # 序列号字节 4
    PART_NUMBER_START = 329       # 部件号起始位置
    PART_NUMBER_END = 348         # 部件号结束位置 (20字符)
    REVISION_CODE = 349           # 修订代码

    # DRAM 制造商信息 (350-351，与模组制造商分离)
    DRAM_MANUFACTURER_ID_FIRST = 350   # DRAM 制造商 ID (第一字节)
    DRAM_MANUFACTURER_ID_SECOND = 351  # DRAM 制造商 ID (第二字节)

    # XMP 2.0 配置 (384-511)
    # 根据 XMP 2.0 规范
    # Byte 384-385: Intel XMP Identification String (0x0C, 0x4A/'J')
    XMP_HEADER = 384              # XMP 头部标识 (0x180)
    # Byte 386: XMP Organization / Profile Enable bits (bit0=Profile1, bit1=Profile2)
    XMP_PROFILE_ENABLED = 386     # Profile 启用状态
    # Byte 387: XMP Revision (e.g., 0x20 = XMP 2.0)
    XMP_REVISION = 387            # XMP 修订版本
    XMP_PROFILE1_START = 393      # XMP Profile 1 起始 (0x189)
    XMP_PROFILE2_START = 440      # XMP Profile 2 起始 (0x1B8)


# XMP 2.0 Profile 内部字段偏移 (相对于 XMP_PROFILE*_START)
# 说明：XMP Profile 的时序单位同样基于 DDR4 的 MTB/FTB (MTB=125ps, FTB=1ps)。
class XMP_PROFILE_OFFSETS:
    # 基础字段
    VDD_VOLTAGE = 0          # VDD 电压编码 (带 bit7 启用位)
    CAS_LATENCIES_0 = 4      # CAS Latencies Supported (bitmap, byte 0, CL7..)
    CAS_LATENCIES_1 = 5      # CAS Latencies Supported (bitmap, byte 1)
    CAS_LATENCIES_2 = 6      # CAS Latencies Supported (bitmap, byte 2)
    TCK_MTB = 3              # tCKAVGmin (MTB, 125ps)

    # 时序 MTB 字段
    TAA_MTB = 8              # tAAmin (MTB)
    TRCD_MTB = 9             # tRCDmin (MTB)
    TRP_MTB = 10             # tRPmin (MTB)
    TRAS_TRC_HIGH = 11       # tRAS/tRC 高位 nibble 组合
    TRAS_MTB_LOW = 12        # tRAS 低 8 位 (MTB)
    TRC_MTB_LOW = 13         # tRC 低 8 位 (MTB)

    # 进阶时序 (MTB, 与 DDR4 SPD Timing 字段布局基本一致)
    TRFC1_LOW = 14           # tRFC1 低位 (MTB)
    TRFC1_HIGH = 15          # tRFC1 高位 (MTB)
    TRFC2_LOW = 16           # tRFC2 低位 (MTB)
    TRFC2_HIGH = 17          # tRFC2 高位 (MTB)
    TRFC4_LOW = 18           # tRFC4 低位 (MTB)
    TRFC4_HIGH = 19          # tRFC4 高位 (MTB)

    TFAW_HIGH = 20           # tFAW 高位 (bits 11:8 in low nibble)
    TFAW_LOW = 21            # tFAW 低位
    TRRD_S_MIN = 22          # tRRD_S (MTB)
    TRRD_L_MIN = 23          # tRRD_L (MTB)
    TCCD_L_MIN = 24          # tCCD_L (MTB)
    TWR_HIGH = 25            # tWR 高位 (bits 11:8 in low nibble)
    TWR_LOW = 26             # tWR 低位
    TWTR_S_MIN = 27          # tWTR_S (MTB)
    TWTR_L_MIN = 28          # tWTR_L (MTB)

    # 细粒度时序调整 (FTB, signed int8, 1ps)
    # 这些偏移在实际 SPD 数据中位于 profile 尾部 (示例：0x1AB..0x1AF)。
    TRC_FTB = 34             # tRC Fine Offset
    TRP_FTB = 35             # tRP Fine Offset
    TRCD_FTB = 36            # tRCD Fine Offset
    TAA_FTB = 37             # tAA Fine Offset
    TCK_FTB = 38             # tCK Fine Offset

# DDR4 类型标识
DDR4_TYPE = 0x0C

# 模组类型映射
MODULE_TYPES = {
    0x01: "RDIMM",
    0x02: "UDIMM",
    0x03: "SO-DIMM",
    0x04: "LRDIMM",
    0x05: "Mini-RDIMM",
    0x06: "Mini-UDIMM",
    0x08: "72b-SO-RDIMM",
    0x09: "72b-SO-UDIMM",
    0x0C: "16b-SO-DIMM",
    0x0D: "32b-SO-DIMM",
}

# Bank 组数映射
BANK_GROUPS = {
    0b00: 4,
    0b01: 2,
}

# 密度映射 (Gb)
DENSITY_MAP = {
    0b0000: 0.256,
    0b0001: 0.512,
    0b0010: 1,
    0b0011: 2,
    0b0100: 4,
    0b0101: 8,
    0b0110: 16,
    0b0111: 32,
    0b1000: 12,
    0b1001: 24,
}

# 设备宽度映射
DEVICE_WIDTH = {
    0b000: 4,
    0b001: 8,
    0b010: 16,
    0b011: 32,
}

# 行地址位数映射
ROW_BITS = {
    0b000: 12,
    0b001: 13,
    0b010: 14,
    0b011: 15,
    0b100: 16,
    0b101: 17,
    0b110: 18,
}

# 列地址位数映射
COL_BITS = {
    0b000: 9,
    0b001: 10,
    0b010: 11,
    0b011: 12,
}

# 时间基准 (ps)
MTB = 125    # Medium Time Base = 125ps
FTB = 1      # Fine Time Base = 1ps

# 频率速度等级映射 (tCK -> MT/s)
# tCK ranges based on JEDEC standard:
# DDR4-3200: 625ps (1600MHz), DDR4-2933: 682ps (1466.5MHz), DDR4-2666: 750ps (1333MHz)
SPEED_GRADES = {
    (625, 682): 3200,    # DDR4-3200: tCK = 625ps
    (682, 750): 2933,    # DDR4-2933: tCK = 682ps (added - was missing!)
    (750, 833): 2666,    # DDR4-2666: tCK = 750ps
    (833, 938): 2400,    # DDR4-2400: tCK = 833ps
    (938, 1071): 2133,   # DDR4-2133: tCK = 938ps
    (1071, 1250): 1866,  # DDR4-1866: tCK = 1071ps
    (1250, 1500): 1600,  # DDR4-1600: tCK = 1250ps
}

# XMP 标识
XMP_MAGIC = 0x0C

# Package Type (Byte 6, bit 7)
PACKAGE_TYPES = {
    0: "Monolithic",
    1: "3DS (Non-Monolithic)"
}

# Die Count (Byte 6, bits 6:4)
DIE_COUNTS = {
    0: 1, 1: 2, 2: 3, 3: 4,
    4: 5, 5: 6, 6: 7, 7: 8
}

# Signal Loading (Byte 6, bits 1:0)
SIGNAL_LOADING = {
    0: "Not specified",
    1: "Multi-load stack",
    2: "Single-load stack (3DS)",
    3: "Reserved"
}

# Banks per bank group (DDR4 always has 4 banks per group)
BANKS_PER_GROUP = 4

# UI 颜色主题
class Colors:
    PRIMARY = "#1f538d"
    SECONDARY = "#444444"
    SUCCESS = "#27ae60"
    WARNING = "#f39c12"
    DANGER = "#c0392b"
    DANGER_HOVER = "#e74c3c"
    BACKGROUND = "#2b2b2b"
    CARD_BG = "#363636"
    TEXT = "#ffffff"
    TEXT_SECONDARY = "#aaaaaa"
    MODIFIED = "#f1c40f"
    HIGHLIGHT = "#3498db"
