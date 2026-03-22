# Word2PDF

使用 Python 将指定目录下的 Word 文档批量转换为 PDF 格式（跨平台）。

## 功能特性

- **跨平台支持**: Windows, macOS, Linux 通用
- 使用 **LibreOffice** 进行转换（免费开源）
- **稳定可靠**: 串行处理，避免资源冲突
- **详细报告**: 终端显示 + 保存到文件 `conversion_report.txt`
- 支持多种格式: `.doc`, `.docx`, `.odt`, `.rtf`

## 为什么需要 LibreOffice？

Word 格式 (.doc/.docx) 是微软专有格式，目前没有完全免费且无需安装任何软件的转换方案：

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **LibreOffice** | 免费、跨平台、格式支持好、离线、稳定 | 需要安装 (~300MB)、串行处理 | ⭐⭐⭐⭐⭐ |
| 在线 API | 无需本地安装、可能更快 | 付费、隐私风险、需联网 | ⭐⭐ |
| 云服务 (AWS/GCP) | 稳定可靠 | 按量收费、需要联网 | ⭐⭐ |
| Microsoft Word API | 格式最准确 | 需要购买 MS Word + 仅 Windows | ⭐⭐⭐ |

**LibreOffice 是目前最平衡的方案**：免费 + 跨平台 + 离线工作 + 稳定可靠。

## 前置要求

安装 [LibreOffice](https://www.libreoffice.org/download/)：

```bash
# Windows
winget install LibreOffice

# macOS
brew install --cask libreoffice

# Linux (Ubuntu/Debian)
sudo apt install libreoffice

# Linux (CentOS/RHEL)
sudo yum install libreoffice
```

## 安装

```bash
# 安装 uv (如果尚未安装)
pip install uv

# 安装依赖
uv sync
```

## 使用方法

```bash
# 基本使用 - 转换当前目录下的 Word 文件
uv run word2pdf

# 指定输入目录
uv run word2pdf --input-dir path/to/word/files

# 指定输出目录
uv run word2pdf --output-dir path/to/output

# 扁平化输出(所有 PDF 放在同一目录)
uv run word2pdf --flatten

# 指定 LibreOffice 路径
uv run word2pdf --libreoffice /path/to/soffice

# 组合使用
uv run word2pdf -i input_dir -o output_dir --flatten
```

## 参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--input-dir` | `-i` | Word 文档所在目录 | 当前目录自动发现 |
| `--output-dir` | `-o` | PDF 输出目录 | 当前目录下 PDF_YYYYMMDDHHMM |
| `--flatten` | | 将所有 PDF 输出到同一目录 | False(保持原目录结构) |
| `--libreoffice` | `-l` | LibreOffice soffice 路径 | 自动检测 |

## 性能说明

### 为什么采用串行处理？

LibreOffice 在并行模式下存在已知问题：
- 多个实例会产生 `libpng` 错误
- 字体、临时文件等资源会冲突
- 即使使用独立用户配置也无法完全隔离

### 实际性能参考

| 文件数量 | 预计耗时 | 说明 |
|----------|----------|------|
| 10 个 | ~1-2 分钟 | 取决于文件大小 |
| 50 个 | ~5-8 分钟 | 单核稳定处理 |
| 100 个 | ~15-20 分钟 | 可靠性优于速度 |

### 加速建议

1. **使用 SSD 硬盘** - 可提速 30-50%
2. **关闭实时杀毒扫描** - LibreOffice 启动会更快
3. **分批处理** - 将大量文件分成多个目录
4. **增加内存** - LibreOffice 启动需要一定内存

## 输出报告

转换完成后会生成：

1. **终端报告**: 实时显示转换进度和结果摘要
2. **详细报告文件**: `conversion_report.txt` 包含：
   - 转换成功/失败统计
   - 失败文件的详细错误信息
   - 每个文件的转换耗时
   - 所有文件的完整路径

报告示例：

```
============================================================
转换报告
============================================================

开始时间: 2026-03-22 18:23:03
结束时间: 2026-03-22 18:27:32
总计文件: 23
成功: 23
失败: 0
跳过: 0
总耗时: 268.66 秒

------------------------------------------------------------
所有文件详情:
------------------------------------------------------------

[成功] C:\Users\...\document1.docx
  -> PDF_output\document1.pdf
  耗时: 13.10 秒
```

## 支持的格式

- `.doc` - Microsoft Word 97-2003
- `.docx` - Microsoft Word 2007+
- `.odt` - OpenDocument Text
- `.rtf` - Rich Text Format

## 常见问题

### Q: 提示 "未找到 LibreOffice 安装"
A: 请确保已安装 LibreOffice。如果已安装但仍提示此错误，可使用 `--libreoffice` 参数手动指定 soffice 路径。

### Q: 转换速度慢
A:
- LibreOffice 需要为每个文件启动一个进程，这是正常的
- 检查是否为 HDD 硬盘（SSD 速度提升显著）
- 杀毒软件可能会拖慢速度

### Q: 某些文件转换失败
A:
1. 查看输出目录中的 `conversion_report.txt` 获取详细错误
2. 文件可能损坏或密码保护
3. 尝试用 LibreOffice 手动打开该文件

### Q: 中文显示乱码
A: 确保 LibreOffice 已安装中文语言包和对应字体。

### Q: 可以不安装 LibreOffice 吗？
A: 不可以。Word 是专有格式，需要专门的转换引擎。LibreOffice 是唯一的免费跨平台方案。

### Q: 有付费但更快的方案吗？
A: 可以考虑：
- **云服务**: AWS Document Converter、Google Cloud Conversion API
- **在线 API**: CloudConvert、ConvertAPI（按量付费）
- **商业库**: Aspose.Words（一次性购买，但较贵）

## 技术实现

```
word2pdf/
├── cli.py           # 命令行接口 (Click)
├── converter.py     # 核心转换逻辑
└── __init__.py      # 包初始化
```

**转换流程**：
1. 递归扫描输入目录，查找所有支持的文档格式
2. 使用 tqdm 显示实时进度
3. 对每个文件调用 LibreOffice headless 模式转换
4. 将生成的 PDF 移动到目标位置（保持或扁平化目录结构）
5. 生成详细的转换报告

## 许可证

MIT
