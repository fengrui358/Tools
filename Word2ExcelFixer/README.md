# Word2Excel Fixer

修复从 Word 复制到 Excel 的表格问题：将 Word 单元格内被拆分成多行的文本合并回一个单元格。

## 问题描述

从 Word 复制表格到 Excel 时，Word 中一个单元格内的多行文本会被拆分成 Excel 的多个行。本工具通过检测单元格边框，识别需要合并的行，并将其合并回原始格式。

## 判断规则

属于同一原始 Word 单元格的 Excel 行，其对应单元格的上下边缘都有完整边框。

## 安装

```bash
# 使用 uv 安装依赖
uv sync
```

## 使用方法

### 命令行

```bash
# 激活虚拟环境后运行
uv run word2excel-fix <excel_file_path>

# 或直接运行模块
uv run python -m word2excel_fixer <excel_file_path>
```

### Python 代码

```python
from word2excel_fixer import fix_excel

fix_excel("path/to/your/file.xlsx")
```

## 输出

修复后的文件将保存在原文件同目录下，文件名为 `原文件名_fixed.xlsx`。

## 技术说明

- 使用 `openpyxl` 库读取和操作 Excel 文件
- 通过检测单元格边框判断是否需要合并
- 合并时保留原始换行格式
- 自动删除合并后多余的空行

## 依赖

- Python >= 3.10
- openpyxl >= 3.1.0
