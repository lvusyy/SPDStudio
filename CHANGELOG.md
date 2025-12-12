# Changelog

本文档记录 SPDStudio 的所有重要更改。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [v1.0.0] - 2024-12-13

### 新增功能

- **SPD 数据读取**: 支持从 DDR4 内存条读取完整的 512 字节 SPD 数据
- **SPD 数据写入**: 支持将修改后的 SPD 数据写入内存条
- **十六进制编辑器**:
  - 直观的 HEX 视图显示
  - 支持范围选择（鼠标拖拽）
  - 右键菜单支持多种复制格式（HEX、ASCII、C 数组、Python 列表）
  - 双击编辑单个字节
- **参数解析**: 自动解析并显示内存参数
  - 容量、速度等级
  - 时序参数 (tCL, tRCD, tRP, tRAS)
  - 模组类型 (UDIMM, RDIMM, SO-DIMM, LRDIMM)
- **XMP 2.0 支持**:
  - 完整解析 XMP Profile 1 和 Profile 2
  - 显示频率、电压、时序参数
- **制造商信息**: 支持查看和编辑
  - 制造商名称
  - 部件号
  - 序列号
  - 模组类型
- **数据导入/导出**: 支持 BIN 文件的导入和导出
- **自动备份**: 读取时自动保存备份文件

### 平台支持

- ✅ Windows 10/11 - 完全支持
- ⚠️ Linux - 实验性支持（需要配置 udev 规则）
- ❌ macOS - 暂不支持（需要 IOKit 框架适配）

### 兼容硬件

- USB SPD 读写器 (VID: 0x0483, PID: 0x1230)
- CH341A 兼容设备
- 其他兼容 HID 协议的 SPD 读写设备

---

## 版本计划

### v1.1.0 (计划中)
- [ ] DDR5 SPD 支持
- [ ] XMP 3.0 支持
- [ ] 批量读写功能

### v1.2.0 (计划中)
- [ ] macOS 平台支持
- [ ] 自定义设备 VID/PID 配置
- [ ] 多语言支持 (English)
