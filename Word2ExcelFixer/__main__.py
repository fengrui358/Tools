"""
模块入口，支持 `python -m word2excel_fixer` 调用
"""

from .cli import main
import sys

if __name__ == "__main__":
    sys.exit(main())
