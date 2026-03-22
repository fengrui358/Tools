"""Core conversion logic for Word to PDF using LibreOffice."""

import os
import platform
import subprocess
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Dict, Any
import time

from tqdm import tqdm


@dataclass
class ConversionResult:
    """Result of a single file conversion."""
    input_path: str
    output_path: str
    success: bool
    error: Optional[str] = None
    duration: float = 0.0


@dataclass
class ConversionReport:
    """Summary report of batch conversion."""
    total_files: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    total_duration: float = 0.0
    results: List[ConversionResult] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    def print_report(self) -> None:
        """Print a formatted report to console."""
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel

        console = Console()

        # Summary panel
        summary = f"""
[bold green]✓ 转换完成[/bold green]

总计文件: {self.total_files}
成功: [green]{self.successful}[/green]
失败: [red]{self.failed}[/red]
跳过: [yellow]{self.skipped}[/yellow]
耗时: {self.total_duration:.2f} 秒
        """.strip()

        console.print(Panel(summary, title="转换报告", border_style="bright_blue"))

        # Failed files table
        if self.failed > 0:
            table = Table(title="失败的文件", show_header=True, header_style="bold red")
            table.add_column("文件", style="dim")
            table.add_column("错误信息")

            for result in self.results:
                if not result.success and result.error:
                    table.add_column(result.input_path, result.error)

            console.print(table)


class LibreOfficeFinder:
    """Find LibreOffice installation on different platforms."""

    @staticmethod
    def find_soffice() -> Optional[Path]:
        """Find LibreOffice/soffice executable."""
        system = platform.system()

        # Common LibreOffice installation paths
        paths = []

        if system == "Windows":
            paths = [
                Path("C:/Program Files/LibreOffice/program/soffice.exe"),
                Path("C:/Program Files (x86)/LibreOffice/program/soffice.exe"),
                Path("C:/Program Files/LibreOffice/program/soffice.com"),
                Path("C:/Program Files (x86)/LibreOffice/program/soffice.com"),
            ]
        elif system == "Darwin":  # macOS
            paths = [
                Path("/Applications/LibreOffice.app/Contents/MacOS/soffice"),
                Path("/Applications/OpenOffice.app/Contents/MacOS/soffice"),
            ]
        else:  # Linux
            paths = [
                Path("/usr/bin/libreoffice"),
                Path("/usr/bin/soffice"),
                Path("/usr/local/bin/libreoffice"),
                Path("/usr/local/bin/soffice"),
                Path("/opt/libreoffice/program/soffice"),
            ]

        # Check predefined paths
        for path in paths:
            if path.exists():
                return path

        # Try to find in PATH
        soffice_names = ["soffice", "libreoffice", "soffice.exe"]
        for name in soffice_names:
            path = shutil.which(name)
            if path:
                return Path(path)

        return None

    @staticmethod
    def check_version(soffice_path: Path) -> Optional[str]:
        """Get LibreOffice version."""
        try:
            result = subprocess.run(
                [str(soffice_path), "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None


class Word2PDFConverter:
    """Batch Word to PDF converter with parallel processing (LibreOffice-based)."""

    SUPPORTED_EXTENSIONS = {'.doc', '.docx', '.odt', '.rtf'}

    def __init__(
        self,
        input_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        flatten: bool = False,
        workers: Optional[int] = None,
        libreoffice_path: Optional[Path] = None,
    ):
        """Initialize the converter.

        Args:
            input_dir: Directory containing Word files. If None, uses current directory.
            output_dir: Directory for PDF output. If None, creates timestamped folder.
            flatten: If True, all PDFs go to output root. If False, preserves structure.
            workers: Number of parallel workers. If None, uses CPU count.
            libreoffice_path: Path to LibreOffice soffice executable. Auto-detected if None.
        """
        self.input_dir = Path(input_dir) if input_dir else Path.cwd()
        self.flatten = flatten

        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            timestamp = datetime.now().strftime("%Y%m%d%H%M")
            self.output_dir = Path.cwd() / f"PDF_{timestamp}"

        # Find LibreOffice
        if libreoffice_path:
            self.soffice_path = libreoffice_path
        else:
            self.soffice_path = LibreOfficeFinder.find_soffice()

        if not self.soffice_path:
            raise RuntimeError(
                "未找到 LibreOffice 安装。请安装 LibreOffice: https://www.libreoffice.org/download/\n"
                "安装后 LibreOffice 支持的平台: Windows, macOS, Linux"
            )

        # LibreOffice doesn't handle parallel conversions well, so we limit workers
        # and process sequentially with user folder isolation
        self.workers = 1  # Force sequential for LibreOffice stability
        self.report = ConversionReport()

        # Verify LibreOffice is working
        version = LibreOfficeFinder.check_version(self.soffice_path)
        if version:
            self._libreoffice_version = version
        else:
            self._libreoffice_version = "unknown"

    def _find_word_files(self) -> List[Path]:
        """Find all Word files in the input directory recursively."""
        word_files = []
        for ext in self.SUPPORTED_EXTENSIONS:
            word_files.extend(self.input_dir.rglob(f"*{ext}"))
        return sorted(word_files)

    def _get_output_path(self, input_path: Path) -> Path:
        """Determine the output path for a given input file."""
        if self.flatten:
            return self.output_dir / f"{input_path.stem}.pdf"

        # Preserve directory structure
        relative_path = input_path.relative_to(self.input_dir)
        output_path = self.output_dir / relative_path.with_suffix('.pdf')
        return output_path

    def _convert_single(self, input_path: Path, output_path: Path) -> ConversionResult:
        """Convert a single Word file to PDF using LibreOffice."""
        start_time = time.time()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # LibreOffice converts to the same directory as input, then we move
        temp_dir = input_path.parent

        try:
            # Use LibreOffice headless mode to convert
            cmd = [
                str(self.soffice_path),
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(temp_dir),
                str(input_path),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout per file
                env={**os.environ, "DISPLAY": ""}  # Ensure headless mode
            )

            if result.returncode != 0:
                return ConversionResult(
                    input_path=str(input_path),
                    output_path=str(output_path),
                    success=False,
                    error=f"LibreOffice 错误: {result.stderr or result.stdout}",
                    duration=time.time() - start_time,
                )

            # Find the generated PDF
            expected_pdf = temp_dir / f"{input_path.stem}.pdf"

            if not expected_pdf.exists():
                return ConversionResult(
                    input_path=str(input_path),
                    output_path=str(output_path),
                    success=False,
                    error="PDF 文件未生成",
                    duration=time.time() - start_time,
                )

            # Move PDF to target location
            shutil.move(str(expected_pdf), str(output_path))

            return ConversionResult(
                input_path=str(input_path),
                output_path=str(output_path),
                success=True,
                duration=time.time() - start_time,
            )

        except subprocess.TimeoutExpired:
            return ConversionResult(
                input_path=str(input_path),
                output_path=str(output_path),
                success=False,
                error="转换超时 (>60秒)",
                duration=60.0,
            )
        except Exception as e:
            return ConversionResult(
                input_path=str(input_path),
                output_path=str(output_path),
                success=False,
                error=str(e),
                duration=time.time() - start_time,
            )

    def convert(self) -> ConversionReport:
        """Execute the batch conversion."""
        self.report.start_time = datetime.now()
        start_time = time.time()

        # Find all Word files
        word_files = self._find_word_files()
        self.report.total_files = len(word_files)

        if not word_files:
            from rich.console import Console
            console = Console()
            console.print(f"[yellow]在 {self.input_dir} 中未找到支持的文档文件[/yellow]")
            console.print(f"[dim]支持的格式: {', '.join(self.SUPPORTED_EXTENSIONS)}[/dim]")
            self.report.end_time = datetime.now()
            return self.report

        # Print info
        from rich.console import Console
        console = Console()
        console.print(f"\n[cyan]找到 {len(word_files)} 个文档[/cyan]")
        console.print(f"[cyan]LibreOffice: {self._libreoffice_version}[/cyan]")
        console.print(f"[cyan]输出目录: {self.output_dir}[/cyan]\n")

        # Convert files sequentially (LibreOffice limitation)
        # Using ThreadPool with 1 worker for consistency with interface
        with tqdm(
            total=len(word_files),
            desc="转换进度",
            unit="文件",
            ncols=80,
        ) as pbar:
            for word_file in word_files:
                output_path = self._get_output_path(word_file)
                result = self._convert_single(word_file, output_path)

                self.report.results.append(result)

                if result.success:
                    self.report.successful += 1
                    pbar.set_postfix(success=f"{self.report.successful}", failed=f"{self.report.failed}")
                else:
                    self.report.failed += 1
                    pbar.set_postfix(success=f"{self.report.successful}", failed=f"{self.report.failed}")

                pbar.update(1)

        self.report.end_time = datetime.now()
        self.report.total_duration = time.time() - start_time

        return self.report
