"""Main entry point for GA Audit application."""

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from .auditor import audit_all_documents, ContentAuditor
from .config import WORD_DIR, ZHIPUAI_API_KEY
from .converter import convert_all_word_to_pdf, get_word_files

console = Console()


def print_conversion_results(results: dict) -> None:
    """Print Word to PDF conversion results."""
    if results["status"] == "error":
        console.print(f"[red]Error: {results['message']}[/red]")
        return

    console.print(Panel.fit(f"[bold green]Output Directory:[/bold green] {results['output_dir']}"))

    # Print conversion summary
    console.print(f"\n[bold]Conversion Summary:[/bold]")
    console.print(f"  [green]✓[/green] Converted: {len(results['converted'])} files")
    console.print(f"  [red]✗[/red] Failed: {len(results['failed'])} files")

    # Print renamed files
    if results["renamed"]:
        console.print(f"\n[bold yellow]Normalized Filenames:[/bold yellow]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Original", style="dim")
        table.add_column("Normalized")

        for item in results["renamed"]:
            table.add_row(item["original"], item["normalized"])

        console.print(table)

    # Print converted files
    if results["converted"]:
        console.print(f"\n[bold green]Successfully Converted:[/bold green]")
        for item in results["converted"]:
            console.print(f"  {item['word_file']} → {item['pdf_file']}")

    # Print failed files
    if results["failed"]:
        console.print(f"\n[bold red]Failed to Convert:[/bold red]")
        for filename in results["failed"]:
            console.print(f"  [red]✗[/red] {filename}")


def print_audit_results(results: dict) -> None:
    """Print audit results."""
    if results["status"] == "error":
        console.print(f"[red]Error: {results['message']}[/red]")
        return

    console.print(Panel.fit("[bold blue]Document Audit Results[/bold blue]"))

    # Print summary
    console.print(f"\n[bold]Audit Summary:[/bold]")
    console.print(f"  Total Documents: {results['total_documents']}")
    console.print(f"  [green]Compliant: {results['summary']['compliant']}[/green]")
    console.print(f"  [yellow]Needs Review: {results['summary']['needs_review']}[/yellow]")

    if results["summary"]["unknown_names_found"]:
        console.print(f"  [red]⚠ Unknown names found in documents![/red]")

    # Print detailed results for each document
    for audit in results["audits"]:
        console.print(f"\n[bold]{'='*60}[/bold]")
        console.print(f"[bold cyan]Document: {audit['filename']}[/bold cyan]")

        # Content audit results
        content_audit = audit["content_audit"]
        if content_audit.get("is_compliant"):
            console.print("  [green]✓ Content Audit: Compliant[/green]")
        else:
            console.print("  [yellow]⚠ Content Audit: Needs Review[/yellow]")

        if content_audit.get("summary"):
            console.print(f"  Summary: {content_audit['summary'][:100]}...")

        # Print issues if any
        issues = content_audit.get("issues", [])
        if issues:
            console.print(f"  [yellow]Issues Found ({len(issues)}):[/yellow]")
            for issue in issues[:3]:  # Show first 3 issues
                console.print(f"    - [{issue.get('category', 'N/A')}] {issue.get('description', '')[:80]}")

        # Missing items
        missing = content_audit.get("missing_items", [])
        if missing:
            console.print(f"  [red]Missing Items:[/red]")
            for item in missing:
                console.print(f"    - {item}")

        # Personnel check results
        personnel = audit["personnel_check"]
        if personnel["has_unknown_names"]:
            console.print(f"  [red]⚠ Unknown Names:[/red] {', '.join(personnel['names_not_in_list'])}")
        else:
            console.print(f"  [green]✓ All names found in personnel list[/green]")

        console.print(f"  Names found: {len(personnel['names_in_list'])}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="GA Audit - Word to PDF converter with AI content audit"
    )
    parser.add_argument(
        "action",
        choices=["convert", "audit", "all"],
        help="Action to perform: convert (Word to PDF), audit (AI content check), or all"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for audit results (JSON format)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    console.print(Panel.fit("[bold blue]GA Audit Tool[/bold blue]"))

    # Check API key for audit
    if args.action in ["audit", "all"] and not ZHIPUAI_API_KEY:
        console.print("[red]Error: ZHIPUAI_API_KEY not set![/red]")
        console.print("Please set it in .env file: ZHIPUAI_API_KEY=your_key_here")
        return

    # Execute requested action
    if args.action == "convert":
        results = convert_all_word_to_pdf()
        print_conversion_results(results)

    elif args.action == "audit":
        results = audit_all_documents()
        print_audit_results(results)

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
            console.print(f"\n[green]Results saved to: {output_path}[/green]")

    elif args.action == "all":
        # First convert, then audit
        console.print("\n[bold]Step 1: Converting Word to PDF...[/bold]")
        conversion_results = convert_all_word_to_pdf()
        print_conversion_results(conversion_results)

        console.print("\n[bold]Step 2: Auditing content...[/bold]")
        audit_results = audit_all_documents()
        print_audit_results(audit_results)

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(json.dumps(audit_results, ensure_ascii=False, indent=2))
            console.print(f"\n[green]Audit results saved to: {output_path}[/green]")


if __name__ == "__main__":
    main()
