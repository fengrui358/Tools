"""
Word2Excel Fixer 使用示例

演示如何以不同方式使用 Word2Excel Fixer
"""

# 方式一：直接调用核心函数
from word2excel_fixer import fix_excel

# 修复单个文件，输出到默认位置（*_fixed.xlsx）
output = fix_excel("example.xlsx")
print(f"输出文件: {output}")

# 方式二：指定输出路径
output = fix_excel("example.xlsx", output_path="cleaned.xlsx")
print(f"输出文件: {output}")

# 方式三：使用命令行
# 在终端中运行：
#   uv run word2excel-fix example.xlsx
#   uv run word2excel-fix example.xlsx -o output.xlsx
#   uv run python -m word2excel_fixer example.xlsx -v

# 方式四：批量处理多个文件
from pathlib import Path

excel_dir = Path("./excel_files")
for excel_file in excel_dir.glob("*.xlsx"):
    if "_fixed" not in excel_file.name:  # 跳过已处理的文件
        try:
            output = fix_excel(str(excel_file))
            print(f"✓ {excel_file.name} -> {Path(output).name}")
        except Exception as e:
            print(f"✗ {excel_file.name} 失败: {e}")
