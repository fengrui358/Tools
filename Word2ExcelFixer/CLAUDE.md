# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Word2Excel Fixer repairs Excel tables that were copied from Microsoft Word. When copying tables from Word to Excel, a single Word cell with multiple lines gets split across multiple Excel rows. This tool detects and merges those split cells back together.

## Key Commands

```bash
# Install dependencies
uv sync

# Run via CLI (uses column A as anchor by default)
uv run word2excel-fix <path_to_excel_file>

# Run with custom output path
uv run word2excel-fix <input> -o <output>

# Run with verbose logging
uv run word2excel-fix <input> -v

# Use as Python module
from word2excel_fixer import fix_excel
fix_excel('path/to/file.xlsx')

# With custom anchor column (1=Column A, 2=Column B, 4=Column D...)
fix_excel('path/to/file.xlsx', anchor_column=4)
```

## Architecture

The project has three main modules:

- `core.py` - Core logic for detecting and merging split cells
- `cli.py` - Command-line interface
- `__init__.py` - Public API exports (`fix_excel`, `fix_excel_from_file`)

## Core Algorithm

The merge detection logic is based on an **anchor column** (锚定列) that identifies logical row boundaries.

### What is an Anchor Column?

An anchor column is a column where:
- Each **logical row** has exactly one value
- Rows with **empty values** should be merged into the previous non-empty row

### Detection Rule

1. For each row, check if the anchor column has a value
2. If the anchor column has a value → start of a new logical row
3. If the anchor column is empty → merge this row into the previous logical row
4. Merge all columns' content and delete the now-empty rows

### Key Functions

- `_find_merge_groups_by_key_column()` - Finds row groups to merge based on anchor column
- `_process_worksheet()` - Orchestrates the merging process
- `fix_excel_from_file()` - Main entry point for file processing

### Default Behavior

- By default, **column A (column 1)** is used as the anchor column
- Users can specify a different anchor column via the `anchor_column` parameter

## Dependencies

- `openpyxl>=3.1.0` - Excel file manipulation
- Python >= 3.10
