# Word2PDF

使用 Python 将指定目录下的 Word 文档批量转换为 PDF 格式（跨平台）。

## 功能特性

- **跨平台支持**: Windows, macOS, Linux 通用
- 使用 **LibreOffice** 进行转换，无需 Microsoft Word
- 使用 uv 做依赖管理
- 可配置输入/输出目录
- 支持保持或扁平化目录结构
- 实时进度提示和详细报告
- 支持多种文档格式: .doc, .docx, .odt, .rtf

## 前置要求

安装 [LibreOffice](https://www.libreoffice.org/download/)（免费开源）：

- **Windows**: 下载安装包或通过 winget `winget install LibreOffice`
- **macOS**: `brew install --cask libreoffice` 或下载安装包
- **Linux**: `sudo apt install libreoffice` (Ubuntu/Debian)

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

# 使用 Python 直接运行
uv run python word2pdf/cli.py -i input_dir -o output_dir --flatten
```

## 参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--input-dir` | `-i` | Word 文档所在目录 | 当前目录自动发现 |
| `--output-dir` | `-o` | PDF 输出目录 | 当前目录下 PDF_YYYYMMDDHHMM |
| `--flatten` | | 将所有 PDF 输出到同一目录 | False(保持原目录结构) |
| `--libreoffice` | `-l` | LibreOffice soffice 路径 | 自动检测 |

## 支持的格式

- `.doc` - Microsoft Word 97-2003
- `.docx` - Microsoft Word 2007+
- `.odt` - OpenDocument Text
- `.rtf` - Rich Text Format

## 常见问题

### Q: 提示 "未找到 LibreOffice 安装"
A: 请确保已安装 LibreOffice。如果已安装但仍提示此错误，可使用 `--libreoffice` 参数手动指定 soffice 路径。

### Q: 转换速度较慢
A: LibreOffice 转换每个文件需要启动一个 headless 进程，这是正常现象。大量文件建议分批处理。

### Q: 中文显示乱码
A: 确保 LibreOffice 已安装中文语言包和对应字体。

## 许可证

MIT
