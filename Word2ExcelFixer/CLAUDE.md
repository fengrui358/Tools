# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Word2Excel Fixer repairs Excel tables that were copied from Microsoft Word. When copying tables from Word to Excel, a single Word cell with multiple lines gets split across multiple Excel rows. This tool detects and merges those split cells back together.

## Key Commands

```bash
# Install dependencies
uv sync

# Run via CLI (preferred)
uv run word2excel-fix <path_to_excel_file>

# Run with custom output path
uv run word2excel-fix <input> -o <output>

# Run with verbose logging
uv run word2excel-fix <input> -v

# Use as Python module
uv run python -c "from word2excel_fixer import fix_excel; fix_excel('path/to/file.xlsx')"
```

## Architecture

The project has three main modules:

- `core.py` - Core logic for detecting and merging split cells
- `cli.py` - Command-line interface
- `__init__.py` - Public API exports (`fix_excel`, `fix_excel_from_file`)

## Core Algorithm (Critical)

The merge detection logic is **per-column**, not global. This is important because different columns may have different split boundaries.

### Detection Rule

When Word tables are copied to Excel, split cells have this border pattern:
- **Middle rows**: No bottom border (the cell was split)
- **Last row**: Has bottom border (marks the original Word cell boundary)

The algorithm:
1. For each column, scan rows top to bottom
2. When a row lacks a bottom border → start of a split group
3. Continue down until finding a row with a bottom border → end of group
4. Merge content from all rows in the group into the first row
5. Delete the now-empty intermediate rows

### Key Functions

- `_find_merge_groups_by_column()` - Returns `{col_idx: [[start, end], ...]}` mapping
- `_process_worksheet()` - Orchestrates per-column merging and row deletion
- `_has_bottom_border()` - Checks if a cell has a bottom border

### Important: Why Per-Column?

Consider a table where:
- Column E: Row 30 is a complete cell (has bottom border), Rows 31-33 are split
- Column F: Rows 30-33 are all part of one split cell (only Row 33 has bottom border)

Global row-based merging would incorrectly merge Column E's Rows 30-33. Per-column processing handles this correctly.

## Dependencies

- `openpyxl>=3.1.0` - Excel file manipulation
- Python >= 3.10
