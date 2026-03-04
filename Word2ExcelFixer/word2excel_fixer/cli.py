"""
Word2Excel Fixer 命令行入口

提供命令行接口来运行 Excel 表格修复工具
"""

import sys
import argparse
from pathlib import Path
from .core import fix_excel_from_file
import logging
import io


def _configure_encoding():
    """配置控制台编码以支持中文输出"""
    if sys.platform == 'win32':
        # 在 Windows 上尝试使用 UTF-8 编码
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except (AttributeError, LookupError):
            # 如果 reconfigure 不可用或不支持，尝试设置环境变量
            import os
            os.environ['PYTHONIOENCODING'] = 'utf-8'


def main() -> int:
    """
    命令行入口函数

    Returns:
        int: 退出码（0 表示成功，非 0 表示失败）
    """
    # 配置控制台编码
    _configure_encoding()

    parser = argparse.ArgumentParser(
        description="修复从 Word 复制到 Excel 的表格问题",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s data.xlsx
  %(prog)s data.xlsx -o output.xlsx
  %(prog)s "path/to/my file.xlsx" -v
        """
    )

    parser.add_argument(
        "input",
        help="输入的 Excel 文件路径 (.xlsx)"
    )

    parser.add_argument(
        "-o", "--output",
        help="输出文件路径（默认为 *_fixed.xlsx）",
        default=None
    )

    parser.add_argument(
        "-v", "--verbose",
        help="显示详细日志",
        action="store_true"
    )

    parser.add_argument(
        "-q", "--quiet",
        help="静默模式，仅输出错误信息",
        action="store_true"
    )

    args = parser.parse_args()

    # 设置日志级别
    if args.verbose:
        logging.getLogger("word2excel_fixer").setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger("word2excel_fixer").setLevel(logging.ERROR)

    try:
        output_path = fix_excel_from_file(args.input, args.output)
        print(f"\n[OK] 修复完成！输出文件: {output_path}")
        return 0

    except FileNotFoundError as e:
        print(f"[ERROR] 错误: {e}", file=sys.stderr)
        return 1

    except ValueError as e:
        print(f"[ERROR] 错误: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"[ERROR] 处理失败: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
