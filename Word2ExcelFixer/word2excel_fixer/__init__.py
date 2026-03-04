"""
Word2Excel Fixer - 修复从 Word 复制到 Excel 的表格问题

主要功能：将 Word 单元格内被拆分成多行的文本合并回一个单元格
"""

from .core import fix_excel, fix_excel_from_file

__all__ = ["fix_excel", "fix_excel_from_file"]
__version__ = "1.0.0"
