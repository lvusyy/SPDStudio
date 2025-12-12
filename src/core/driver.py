"""
SPD 硬件驱动层
负责与 HID 设备通信，读写 SPD 数据
"""

import hid
import time
from typing import Optional, Callable, List
from datetime import datetime

from ..utils.constants import DEFAULT_VID, DEFAULT_PID, SPD_SIZE, SPD_PAGE_SIZE


class SPDDriver:
    """SPD 读写器硬件驱动"""

    def __init__(self, vid: int = DEFAULT_VID, pid: int = DEFAULT_PID, debug: bool = False):
        self.vid = vid
        self.pid = pid
        self.device: Optional[hid.device] = None
        self.stop_flag = False
        self.debug = debug
        self._debug_log: List[str] = []

    def _log_debug(self, message: str):
        """记录调试日志"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}"
        self._debug_log.append(log_entry)
        if self.debug:
            print(log_entry)

    def get_debug_log(self) -> str:
        """获取调试日志"""
        return "\n".join(self._debug_log)

    def clear_debug_log(self):
        """清除调试日志"""
        self._debug_log.clear()

    def enable_debug(self, enabled: bool = True):
        """启用/禁用调试模式"""
        self.debug = enabled

    @staticmethod
    def enumerate_devices() -> List[dict]:
        """枚举所有 HID 设备"""
        try:
            return hid.enumerate()
        except Exception as e:
            return []

    @staticmethod
    def find_spd_devices(vid: int = DEFAULT_VID, pid: int = DEFAULT_PID) -> List[dict]:
        """查找 SPD 读写器设备"""
        try:
            return hid.enumerate(vid, pid)
        except Exception:
            return []

    def connect(self, log_callback: Optional[Callable[[str], None]] = None) -> bool:
        """连接到 HID 设备"""
        self._log_debug(f"尝试连接设备 VID=0x{self.vid:04X}, PID=0x{self.pid:04X}")

        # 先枚举检查设备是否存在
        devices = self.find_spd_devices(self.vid, self.pid)
        self._log_debug(f"找到 {len(devices)} 个匹配设备")

        if not devices:
            self._log_debug("错误: 未找到匹配的 HID 设备")
            if log_callback:
                log_callback("未找到 SPD 读写器设备，请检查连接")

            # 列出所有 HID 设备帮助调试
            all_devices = self.enumerate_devices()
            self._log_debug(f"系统中共有 {len(all_devices)} 个 HID 设备:")
            for i, dev in enumerate(all_devices[:10]):  # 只显示前10个
                self._log_debug(f"  [{i}] VID=0x{dev.get('vendor_id', 0):04X}, "
                              f"PID=0x{dev.get('product_id', 0):04X}, "
                              f"Product={dev.get('product_string', 'N/A')}")
            return False

        # 显示找到的设备信息
        for dev in devices:
            self._log_debug(f"找到设备: {dev.get('product_string', 'Unknown')} "
                          f"(Path: {dev.get('path', 'N/A')})")

        try:
            self.device = hid.device()
            self._log_debug("创建 HID device 对象成功")

            self.device.open(self.vid, self.pid)
            self._log_debug("设备打开成功")

            # 获取设备信息
            manufacturer = self.device.get_manufacturer_string() or "Unknown"
            product = self.device.get_product_string() or "Unknown"
            self._log_debug(f"制造商: {manufacturer}, 产品: {product}")

            if log_callback:
                log_callback(f"已连接: {product}")

            # 发送测试命令
            self._log_debug("发送测试命令 BT-VER0010")
            test_resp = self.send_cmd("BT-VER0010", delay=0.1)
            self._log_debug(f"测试命令响应: {repr(test_resp)}")

            if test_resp:
                if log_callback:
                    log_callback(f"设备响应: {test_resp[:50]}..." if len(test_resp) > 50 else f"设备响应: {test_resp}")
            else:
                self._log_debug("警告: 设备未响应测试命令")
                if log_callback:
                    log_callback("警告: 设备连接但未响应，可能需要重新插拔")

            return True

        except Exception as e:
            self._log_debug(f"连接异常: {type(e).__name__}: {str(e)}")
            if log_callback:
                log_callback(f"连接失败: {str(e)}")
            self.device = None
            return False

    def disconnect(self) -> None:
        """断开设备连接"""
        if self.device:
            self._log_debug("断开设备连接")
            try:
                self.device.close()
            except Exception as e:
                self._log_debug(f"断开连接时出错: {e}")
            self.device = None

    def is_connected(self) -> bool:
        """检查设备是否已连接"""
        return self.device is not None

    def send_cmd(self, cmd_str: str, delay: float = 0.02) -> Optional[str]:
        """
        发送命令到设备并读取响应

        Args:
            cmd_str: 命令字符串
            delay: 等待响应的延时（秒）

        Returns:
            响应字符串，失败返回 None
        """
        if not self.device:
            self._log_debug(f"发送命令失败: 设备未连接 (cmd={cmd_str})")
            return None

        # 构造数据包: ReportID(0) + 64 bytes data
        data = [0x00] * 65
        for i, char in enumerate(cmd_str):
            if i + 1 < len(data):
                data[i + 1] = ord(char)

        try:
            self._log_debug(f"TX: {cmd_str}")
            bytes_written = self.device.write(data)
            self._log_debug(f"写入 {bytes_written} 字节")

            time.sleep(delay)

            response = self.device.read(64, timeout_ms=1000)
            if response:
                resp_str = "".join([chr(x) for x in response if 32 <= x <= 126])
                self._log_debug(f"RX: {resp_str}")
                return resp_str
            else:
                self._log_debug("RX: (无响应/超时)")
                return None

        except Exception as e:
            self._log_debug(f"IO 错误: {type(e).__name__}: {str(e)}")
            return None

    def read_spd(
        self,
        progress_callback: Optional[Callable[[float], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[List[int]]:
        """
        读取完整的 512 字节 SPD 数据

        Args:
            progress_callback: 进度回调函数，参数为 0-1 的进度值
            log_callback: 日志回调函数

        Returns:
            512 字节的数据列表，失败返回 None
        """
        self.stop_flag = False
        full_data = [0] * SPD_SIZE
        read_errors = 0

        self._log_debug("开始读取 SPD 数据")

        # 1. 激活与初始化
        self._log_debug("发送激活命令")
        resp = self.send_cmd("BT-VER0010")
        if not resp:
            self._log_debug("激活命令无响应")
            if log_callback:
                log_callback("错误: 设备无响应")
            return None
        time.sleep(0.1)

        # 2. 读取 Page 0 (0-255)
        if log_callback:
            log_callback("正在读取 Page 0...")
        self._log_debug("切换到 Page 0")
        self.send_cmd("BT-I2C2WR360001")
        time.sleep(0.2)

        for offset in range(0, SPD_PAGE_SIZE, 8):
            if self.stop_flag:
                self._log_debug("操作被用户取消")
                return None

            block = self._read_block(0x50, offset, log_callback)

            # 检查是否全为0（可能是读取失败）
            if all(b == 0 for b in block):
                read_errors += 1
                self._log_debug(f"警告: Offset 0x{offset:02X} 读取全零")

            for i, b in enumerate(block):
                full_data[offset + i] = b

            if progress_callback:
                progress_callback((offset + 8) / SPD_SIZE)

        # 3. 读取 Page 1 (256-511)
        if log_callback:
            log_callback("正在读取 Page 1...")
        self._log_debug("切换到 Page 1")
        self.send_cmd("BT-I2C2WR370001")
        time.sleep(0.4)

        for offset in range(0, SPD_PAGE_SIZE, 8):
            if self.stop_flag:
                self._log_debug("操作被用户取消")
                return None

            block = self._read_block(0x50, offset, log_callback)

            for i, b in enumerate(block):
                full_data[SPD_PAGE_SIZE + offset + i] = b

            if progress_callback:
                progress_callback((SPD_PAGE_SIZE + offset + 8) / SPD_SIZE)

        self._log_debug(f"读取完成，共 {read_errors} 个潜在错误")

        # 基本验证
        if all(b == 0 for b in full_data[:256]):
            self._log_debug("错误: 读取的数据全为零")
            if log_callback:
                log_callback("警告: 读取的数据异常（全零），请检查内存条是否正确安装")
            return None

        return full_data

    def _read_block(
        self,
        addr: int,
        offset: int,
        log_callback: Optional[Callable[[str], None]] = None
    ) -> List[int]:
        """
        读取 8 字节数据块

        Args:
            addr: I2C 地址
            offset: 页内偏移
            log_callback: 日志回调

        Returns:
            8 字节数据列表
        """
        cmd = f"BT-I2C2RD{addr:02X}{offset:02X}08"

        for retry in range(3):  # 重试 3 次
            resp = self.send_cmd(cmd)

            if resp and resp.startswith(":"):
                try:
                    parts = resp[1:].strip().split()
                    hex_parts = [p for p in parts if len(p) == 2][:8]
                    if len(hex_parts) == 8:
                        result = [int(x, 16) for x in hex_parts]
                        return result
                    else:
                        self._log_debug(f"解析失败: 只找到 {len(hex_parts)} 个十六进制值")
                except Exception as e:
                    self._log_debug(f"解析异常: {e}, 响应: {repr(resp)}")
            else:
                self._log_debug(f"无效响应 (重试 {retry+1}/3): {repr(resp)}")

            time.sleep(0.05)

        self._log_debug(f"读取块失败: addr=0x{addr:02X}, offset=0x{offset:02X}")
        if log_callback:
            log_callback(f"警告: 读取 0x{offset:02X} 失败，使用默认值")
        return [0] * 8

    def write_spd(
        self,
        data: List[int],
        progress_callback: Optional[Callable[[float], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        写入 SPD 数据到内存条

        Args:
            data: 512 字节数据列表
            progress_callback: 进度回调函数
            log_callback: 日志回调函数

        Returns:
            是否写入成功
        """
        self.stop_flag = False
        self._log_debug("开始写入 SPD 数据")

        if len(data) != SPD_SIZE:
            self._log_debug(f"错误: 数据长度 {len(data)} != {SPD_SIZE}")
            if log_callback:
                log_callback(f"错误: 数据长度必须是 {SPD_SIZE} 字节")
            return False

        # 1. 激活
        self._log_debug("发送激活命令")
        self.send_cmd("BT-VER0010")
        time.sleep(0.1)

        # 2. 写入 Page 0 (0-255)
        if log_callback:
            log_callback("正在写入 Page 0...")
        self._log_debug("切换到 Page 0")
        self.send_cmd("BT-I2C2WR360001")
        time.sleep(0.2)

        for offset in range(0, SPD_PAGE_SIZE, 8):
            if self.stop_flag:
                self._log_debug("写入被用户取消")
                return False
            chunk = data[offset:offset + 8]
            if not self._write_block(0x50, offset, chunk):
                self._log_debug(f"写入失败: offset=0x{offset:02X}")
                if log_callback:
                    log_callback(f"写入失败: Offset {hex(offset)}")
                return False
            if progress_callback:
                progress_callback((offset + 8) / SPD_SIZE)

        # 3. 写入 Page 1 (256-511)
        if log_callback:
            log_callback("正在写入 Page 1...")
        self._log_debug("切换到 Page 1")
        self.send_cmd("BT-I2C2WR370001")
        time.sleep(0.4)

        for offset in range(0, SPD_PAGE_SIZE, 8):
            if self.stop_flag:
                self._log_debug("写入被用户取消")
                return False
            chunk = data[SPD_PAGE_SIZE + offset:SPD_PAGE_SIZE + offset + 8]
            if not self._write_block(0x50, offset, chunk):
                self._log_debug(f"写入失败: offset=0x{SPD_PAGE_SIZE + offset:02X}")
                if log_callback:
                    log_callback(f"写入失败: Offset {hex(SPD_PAGE_SIZE + offset)}")
                return False
            if progress_callback:
                progress_callback((SPD_PAGE_SIZE + offset + 8) / SPD_SIZE)

        self._log_debug("写入完成")
        if log_callback:
            log_callback("写入完成，请重启电脑！")
        return True

    def _write_block(self, addr: int, offset: int, data_bytes: List[int]) -> bool:
        """
        写入 8 字节数据块

        Args:
            addr: I2C 地址
            offset: 页内偏移
            data_bytes: 8 字节数据

        Returns:
            是否写入成功
        """
        data_hex = "".join(f"{b:02X}" for b in data_bytes)
        cmd = f"BT-I2C2WR{addr:02X}{offset:02X}08{data_hex}"
        resp = self.send_cmd(cmd, delay=0.1)
        # 写入通常返回 :00 表示成功
        return True

    def stop(self) -> None:
        """停止当前操作"""
        self._log_debug("停止操作请求")
        self.stop_flag = True

    def verify_spd(
        self,
        data: List[int],
        log_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        验证写入的数据（回读对比）

        Args:
            data: 预期数据
            log_callback: 日志回调

        Returns:
            验证是否通过
        """
        self._log_debug("开始验证数据")
        if log_callback:
            log_callback("正在验证数据...")

        read_data = self.read_spd(log_callback=log_callback)
        if not read_data:
            self._log_debug("验证失败: 无法读取数据")
            if log_callback:
                log_callback("验证失败: 无法读取数据")
            return False

        mismatches = []
        for i, (expected, actual) in enumerate(zip(data, read_data)):
            if expected != actual:
                mismatches.append((i, expected, actual))

        if mismatches:
            self._log_debug(f"验证失败: {len(mismatches)} 字节不匹配")
            if log_callback:
                log_callback(f"验证失败: {len(mismatches)} 字节不匹配")
                for offset, expected, actual in mismatches[:5]:
                    log_callback(f"  Offset {offset:03X}: 预期 {expected:02X}, 实际 {actual:02X}")
                if len(mismatches) > 5:
                    log_callback(f"  ... 还有 {len(mismatches) - 5} 处不匹配")
            return False

        self._log_debug("验证通过")
        if log_callback:
            log_callback("验证通过！")
        return True

    def export_debug_log(self, filepath: str) -> bool:
        """导出调试日志到文件"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("SPD Tools Debug Log\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(self.get_debug_log())
            return True
        except Exception:
            return False
