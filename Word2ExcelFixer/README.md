# Word2Excel Fixer

修复从 Word 复制到 Excel 的表格问题：将 Word 单元格内被拆分成多行的文本合并回一个单元格。

## 问题描述

从 Word 复制表格到 Excel 时，Word 中一个单元格内的多行文本会被拆分成 Excel 的多个行。本工具通过锚定列检测，识别需要合并的行，并将其合并回原始格式。

## 核心概念：锚定列

**锚定列**是指逻辑上每行应该有唯一值的列。由于其他单元格的换行导致一行内容被拆分成多行，锚定列用于识别哪些行属于同一个逻辑行。

- 锚定列有值的行 = 新的逻辑行开始
- 锚定列为空的行 = 应该合并到上一个有值的行

默认使用第一列（A列）作为锚定列。

## 安装

```bash
# 使用 uv 安装依赖
uv sync
```

## 使用方法

### 命令行

```bash
# 基本用法 - 使用第一列作为锚定列
uv run word2excel-fix <excel_file_path>

# 指定输出文件
uv run word2excel-fix <input> -o <output>

# 显示详细日志
uv run word2excel-fix <input> -v
```

### Python 代码

```python
from word2excel_fixer import fix_excel

# 默认使用第一列作为锚定列
fix_excel("path/to/file.xlsx")

# 指定锚定列（1=列A, 2=列B, 4=列D...）
fix_excel("path/to/file.xlsx", anchor_column=4)
```

### Python API 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `input_path` | str | 必填 | 输入的 Excel 文件路径 |
| `output_path` | str | None | 输出文件路径（默认为 `*_fixed.xlsx`） |
| `anchor_column` | int | 1 | 锚定列编号（1=A列, 2=B列, 4=D列等） |

## 输出

修复后的文件将保存在原文件同目录下，文件名为 `原文件名_fixed.xlsx`。

## 技术说明

- 使用 `openpyxl` 库读取和操作 Excel 文件
- 基于锚定列检测需要合并的行组
- 合并时保留原始换行格式
- 自动删除合并后多余的空行

## 依赖

- Python >= 3.10
- openpyxl >= 3.1.0
