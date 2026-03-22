"""Core conversion logic for Word to PDF using LibreOffice."""

import os
import platform
import subprocess
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import time

try:
    from tqdm import tqdm
except ImportError:
    class tqdm:
        def __init__(self, total, desc, unit):
            self.total = total
            self.desc = desc
            self.n = 0
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def update(self, n=1):
            self.n += n
            print(f"\r{self.desc}: {self.n}/{self.total}", end="", flush=True)
        def set_postfix(self, **kwargs):
            pass


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

    def print_report(self, output_dir: Optional[Path] = None) -> None:
        """Print a formatted report to console and save to file."""
        try:
            from rich.console import Console
            from rich.panel import Panel
            use_rich = True
        except ImportError:
            use_rich = False

        if use_rich:
            console = Console(width=100)
            summary = f"""
总计文件: {self.total_files}
成功: [green]{self.successful}[/green]
失败: [red]{self.failed}[/red]
跳过: [yellow]{self.skipped}[/yellow]
耗时: {self.total_duration:.2f} 秒
            """.strip()
            console.print(Panel(summary, title="[bold]转换报告[/bold]", border_style="bright_blue"))

            if self.failed > 0:
                console.print("\n[bold red]失败的文件:[/bold red]")
                for result in self.results:
                    if not result.success:
                        short_path = result.input_path
                        if len(short_path) > 60:
                            short_path = "..." + short_path[-57:]
                        console.print(f"  [red]X[/red] {short_path}")
                        console.print(f"      [dim]{result.error}[/dim]\n")
        else:
            print("\n" + "=" * 50)
            print("转换报告")
            print("=" * 50)
            print(f"总计文件: {self.total_files}")
            print(f"成功: {self.successful}")
            print(f"失败: {self.failed}")
            print(f"跳过: {self.skipped}")
            print(f"耗时: {self.total_duration:.2f} 秒")

            if self.failed > 0:
                print("\n失败的文件:")
                for result in self.results:
                    if not result.success:
                        print(f"  X {result.input_path}")
                        print(f"    {result.error}")

        # Save detailed report to file
        if output_dir:
            report_file = output_dir / "conversion_report.txt"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("转换报告\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"结束时间: {self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else 'N/A'}\n")
                f.write(f"总计文件: {self.total_files}\n")
                f.write(f"成功: {self.successful}\n")
                f.write(f"失败: {self.failed}\n")
                f.write(f"跳过: {self.skipped}\n")
                f.write(f"总耗时: {self.total_duration:.2f} 秒\n\n")

                if self.failed > 0:
                    f.write("-" * 60 + "\n")
                    f.write("失败的文件详情:\n")
                    f.write("-" * 60 + "\n\n")
                    for result in self.results:
                        if not result.success:
                            f.write(f"文件: {result.input_path}\n")
                            f.write(f"错误: {result.error}\n")
                            f.write(f"输出路径: {result.output_path}\n")
                            f.write(f"耗时: {result.duration:.2f} 秒\n\n")

                f.write("-" * 60 + "\n")
                f.write("所有文件详情:\n")
                f.write("-" * 60 + "\n\n")
                for result in self.results:
                    status = "成功" if result.success else "失败"
                    f.write(f"[{status}] {result.input_path}\n")
                    f.write(f"  -> {result.output_path}\n")
                    if result.error:
                        f.write(f"  错误: {result.error}\n")
                    f.write(f"  耗时: {result.duration:.2f} 秒\n\n")

            if use_rich:
                console.print(f"\n[dim]详细报告已保存到: {report_file}[/dim]")
            else:
                print(f"\n详细报告已保存到: {report_file}")


class LibreOfficeFinder:
    """Find LibreOffice installation on different platforms."""

    @staticmethod
    def find_soffice() -> Optional[Path]:
        """Find LibreOffice/soffice executable."""
        system = platform.system()

        paths = []

        if system == "Windows":
            paths = [
                Path("C:/Program Files/LibreOffice/program/soffice.exe"),
                Path("C:/Program Files (x86)/LibreOffice/program/soffice.exe"),
            ]
        elif system == "Darwin":  # macOS
            paths = [
                Path("/Applications/LibreOffice.app/Contents/MacOS/soffice"),
            ]
        else:  # Linux
            paths = [
                Path("/usr/bin/libreoffice"),
                Path("/usr/bin/soffice"),
                Path("/opt/libreoffice/program/soffice"),
            ]

        for path in paths:
            if path.exists():
                return path

        for name in ["soffice", "libreoffice"]:
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
    """Batch Word to PDF converter using LibreOffice."""

    SUPPORTED_EXTENSIONS = {'.doc', '.docx', '.odt', '.rtf'}

    def __init__(
        self,
        input_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        flatten: bool = False,
        libreoffice_path: Optional[Path] = None,
    ):
        """Initialize the converter."""
        self.input_dir = Path(input_dir) if input_dir else Path.cwd()
        self.flatten = flatten

        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            timestamp = datetime.now().strftime("%Y%m%d%H%M")
            self.output_dir = Path.cwd() / f"PDF_{timestamp}"

        if libreoffice_path:
            self.soffice_path = libreoffice_path
        else:
            self.soffice_path = LibreOfficeFinder.find_soffice()

        if not self.soffice_path:
            raise RuntimeError(
                "未找到 LibreOffice 安装。请安装 LibreOffice: https://www.libreoffice.org/download/"
            )

        self.report = ConversionReport()
        self._libreoffice_version = LibreOfficeFinder.check_version(self.soffice_path) or "unknown"

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

        relative_path = input_path.relative_to(self.input_dir)
        output_path = self.output_dir / relative_path.with_suffix('.pdf')
        return output_path

    def _convert_single(self, input_path: Path, output_path: Path) -> ConversionResult:
        """Convert a single Word file to PDF using LibreOffice."""
        start_time = time.time()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        temp_dir = output_path.parent

        try:
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
                timeout=120,
                env={**os.environ, "DISPLAY": ""}
            )

            if result.returncode != 0:
                return ConversionResult(
                    input_path=str(input_path),
                    output_path=str(output_path),
                    success=False,
                    error=f"LibreOffice: {result.stderr or result.stdout[:300]}",
                    duration=time.time() - start_time,
                )

            expected_pdf = temp_dir / f"{input_path.stem}.pdf"
            if not expected_pdf.exists():
                return ConversionResult(
                    input_path=str(input_path),
                    output_path=str(output_path),
                    success=False,
                    error="PDF 文件未生成",
                    duration=time.time() - start_time,
                )

            if str(expected_pdf) != str(output_path):
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
                error="转换超时 (>120秒)",
                duration=120.0,
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

        word_files = self._find_word_files()
        self.report.total_files = len(word_files)

        if not word_files:
            print(f"在 {self.input_dir} 中未找到支持的文档文件")
            print(f"支持的格式: {', '.join(self.SUPPORTED_EXTENSIONS)}")
            self.report.end_time = datetime.now()
            return self.report

        print(f"\n找到 {len(word_files)} 个文档")
        print(f"LibreOffice: {self._libreoffice_version}")
        print(f"输出目录: {self.output_dir}\n")

        # Convert files sequentially (most stable)
        with tqdm(total=len(word_files), desc="转换进度", unit="文件") as pbar:
            for word_file in word_files:
                output_path = self._get_output_path(word_file)
                result = self._convert_single(word_file, output_path)

                self.report.results.append(result)

                if result.success:
                    self.report.successful += 1
                else:
                    self.report.failed += 1

                pbar.update(1)
                pbar.set_postfix(success=self.report.successful, failed=self.report.failed)

        self.report.end_time = datetime.now()
        self.report.total_duration = time.time() - start_time

        return self.report
