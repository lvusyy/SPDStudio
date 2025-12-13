# SPDStudio v1.1.0 Release Notes

## 🎉 Major Features

### 1. Serial Number Quick Entry Tools
**Three convenient ways to set serial numbers:**
- **随机生成 (Random)**: Generate completely random 4-byte serial numbers
- **全零序列 (All Zeros)**: Quickly fill with `0x00000000`
- **Custom Input**: Keep the traditional hex input method

Perfect for batch memory module production and testing scenarios.

### 2. Editable Timing Parameters with JEDEC Risk Warnings
**Professional timing parameter editing with safety guidance:**
- Edit critical timing parameters: tCK, tAA, tRCD, tRP, tRAS, tRC
- Real-time JEDEC DDR4 specification compliance checking
- Three-level risk indicators:
  - 🟢 **SAFE**: Within JEDEC specifications
  - 🟡 **WARNING**: Below recommended values
  - 🔴 **DANGER**: Significantly below safe thresholds
- MTB (125ps) and FTB (1ps) encoding preview
- Warnings are informative only - advanced users can proceed

Designed for overclockers and memory enthusiasts who need fine-grained control.

### 3. XMP Profile Editing and Creation
**Full XMP 2.0 profile management:**
- **Edit Existing Profiles**: Modify XMP Profile 1 and Profile 2
- **Create New Profiles**: Add XMP support to modules without XMP
- Editable parameters:
  - Frequency (1600-6000 MT/s)
  - Voltage (1.10-1.50V)
  - CAS Latency (CL)
  - tRCD, tRP, tRAS timings
- Real-time preview with risk validation
- XMP 2.0 compliant SPD byte encoding
- Automatic profile activation

Enables users to create custom XMP profiles for better performance.

### 4. Automatic Update Checker
**Stay up-to-date effortlessly:**
- Silent update check on startup (2-second delay)
- Notification dialog when new version is available
- Manual "检查更新" (Check for Updates) button in toolbar
- Direct download link to GitHub releases
- Version comparison using semantic versioning
- Shows release notes and changelog

Ensures you always have access to the latest features and bug fixes.

## 🐛 Bug Fixes

### XMP Dialog Parameter Mismatch (v1.1.0)
- Fixed `TypeError` when creating XMP profiles
- Corrected parameter name from `profile_data` to `existing_data`
- Fixed callback signature to match `on_save(profile_num, data)`
- Resolved duplicate emoji prefix in risk messages

### Timing Dialog Display Improvements (v1.1.0)
- Increased risk indicator size for better visibility (20 → 24pt)
- Improved layout padding for cleaner appearance
- Enhanced multi-line message display

## 📋 Complete Changelog

```
8c1a9d7 chore: bump version to 1.1.0
2f3d4c4 fix(xmp,timing): fix parameter mismatch and add manual update check
d409651 feat(xmp): add XMP profile editing and creation
048442e feat(timing): add editable timing parameters with JEDEC risk warnings
c3a306a feat(update): add automatic update checker from GitHub releases
19d0361 feat(serial): add random and all-zeros serial number generators
```

## 🔧 Technical Details

### New Files Created
- `src/utils/timing_validator.py` - JEDEC DDR4 timing validation
- `src/gui/widgets/timing_edit_dialog.py` - Timing parameter editor
- `src/gui/widgets/xmp_edit_dialog.py` - XMP profile editor
- `src/core/updater.py` - GitHub release update checker
- `src/gui/widgets/update_dialog.py` - Update notification dialog
- `src/utils/version.py` - Version constants

### Modified Files
- `src/gui/app.py` - Added update checker integration and "检查更新" button
- `src/gui/tabs/details.py` - Enabled serial number generator
- `src/gui/tabs/timing.py` - Made timing parameters editable
- `src/gui/tabs/xmp.py` - Added XMP editing and creation
- `src/gui/widgets/editable_field.py` - Added serial generator functionality

### Architecture Improvements
- Observer pattern ensures automatic UI refresh after modifications
- Async threading for update checks to avoid blocking UI
- Modular validation system for extensibility
- XMP 2.0 compliant SPD byte encoding

## ⚠️ Important Notes

### For Users
1. **Timing Parameters**: Warnings are advisory only. Advanced users who understand memory timings can override warnings.
2. **XMP Profiles**: Always test new XMP profiles in BIOS before relying on them for production systems.
3. **Backup**: The application automatically backs up SPD data when reading from devices.
4. **Updates**: The update checker requires internet connection and accesses GitHub API.

### For Developers
1. **Conventional Commits**: All commits follow the conventional commit specification.
2. **No Pre-commit Hooks Skipped**: All commits passed local Git hooks.
3. **Observer Pattern**: Data changes automatically trigger UI refresh via `SPDDataModel`.
4. **MTB/FTB Encoding**: Timing values use 125ps MTB and 1ps FTB with signed byte conversion.

## 🙏 Acknowledgments

Thank you to all users who provided feedback and feature requests. This release incorporates community-driven improvements for professional memory module management.

## 📦 Installation

Download the latest release from:
https://github.com/lvusyy/SPDStudio/releases/tag/v1.1.0

For Windows: Download `SPDStudio-v1.1.0-Windows.exe`
For source: Download `Source code (zip)` or `Source code (tar.gz)`

## 📝 License

MIT License - See LICENSE file for details

---

**Full Changelog**: https://github.com/lvusyy/SPDStudio/compare/v1.0.0...v1.1.0
