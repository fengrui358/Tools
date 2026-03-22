"""Command-line interface for Word2PDF converter."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from .converter import Word2PDFConverter

console = Console()


@click.command()
@click.option(
    '--input-dir', '-i',
    type=click.Path(exists=True, path_type=Path),
    help='Word 文档所在目录 (默认: 当前目录自动发现)',
)
@click.option(
    '--output-dir', '-o',
    type=click.Path(path_type=Path),
    help='PDF 输出目录 (默认: 当前目录下 PDF_YYYYMMDDHHMM)',
)
@click.option(
    '--flatten',
    is_flag=True,
    default=False,
    help='将所有 PDF 输出到同一目录 (默认: 保持原目录结构)',
)
@click.option(
    '--libreoffice', '-l',
    'libreoffice_path',
    type=click.Path(exists=True, path_type=Path),
    help='LibreOffice soffice 路径 (默认: 自动检测)',
)
@click.version_option(version='0.1.0')
def main(
    input_dir: Optional[Path],
    output_dir: Optional[Path],
    flatten: bool,
    libreoffice_path: Optional[Path],
) -> None:
    """批量将 Word 文档转换为 PDF 格式 (跨平台).

    使用 LibreOffice 进行转换，支持 Windows, macOS, Linux.

    \b
    示例:
        word2pdf                          # 转换当前目录
        word2pdf -i ./docs -o ./pdf       # 指定输入输出目录
        word2pdf --flatten                # 扁平化输出
        word2pdf -l /path/to/soffice      # 指定 LibreOffice 路径
    """
    console.print("[bold cyan]Word2PDF 批量转换工具 (跨平台版)[/bold cyan]\n")

    try:
        converter = Word2PDFConverter(
            input_dir=input_dir,
            output_dir=output_dir,
            flatten=flatten,
            libreoffice_path=libreoffice_path,
        )

        report = converter.convert()

        # Get output directory for report file
        output_dir = converter.output_dir
        report.print_report(output_dir)

        # Exit with error code if any conversions failed
        if report.failed > 0:
            sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]转换已取消[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")
        raise click.ClickException(str(e))


if __name__ == '__main__':
    main()
