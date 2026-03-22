#!/usr/bin/env python3
"""
Test script for GA Audit - tests file operations without API calls
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Add GLM-API to path for imports
GLM_API_PATH = Path("/Users/free/WorkSpace/GLM-API")
if str(GLM_API_PATH) not in sys.path:
    sys.path.insert(0, str(GLM_API_PATH))

from ga_audit.config import get_personnel_names, WORD_DIR
from ga_audit.converter import normalize_filename, get_word_files, extract_text_from_docx


def test_normalize_filename():
    """Test filename normalization."""
    print("=" * 60)
    print("Testing Filename Normalization")
    print("=" * 60)

    test_cases = [
        ("【已检查】2025年12月感知源后端运维文档汇总.docx", "2025年12月感知源后端运维文档汇总.docx"),
        ("前缀内容2024年3月感知源后端运维文档汇总.docx", "2024年3月感知源后端运维文档汇总.docx"),
        ("2025年1月感知源后端运维文档汇总.docx", "2025年1月感知源后端运维文档汇总.docx"),
        ("没有年份的文件.docx", "没有年份的文件.docx"),
    ]

    for original, expected in test_cases:
        result = normalize_filename(original)
        status = "✓" if result == expected else "✗"
        print(f"{status} {original} -> {result}")
        if result != expected:
            print(f"  Expected: {expected}")

    print()


def test_get_word_files():
    """Test getting Word files."""
    print("=" * 60)
    print("Testing Get Word Files")
    print("=" * 60)

    word_files = get_word_files()
    print(f"Found {len(word_files)} Word files in {WORD_DIR}")
    print(f"Word directory: {WORD_DIR}")

    for f in word_files[:5]:  # Show first 5
        print(f"  - {f.name}")

    if len(word_files) > 5:
        print(f"  ... and {len(word_files) - 5} more files")

    print()


def test_extract_text():
    """Test text extraction from Word files."""
    print("=" * 60)
    print("Testing Text Extraction")
    print("=" * 60)

    word_files = get_word_files()

    # Test first 3 files
    for word_file in word_files[:3]:
        print(f"File: {word_file.name}")
        text = extract_text_from_docx(word_file)

        # Show first 200 characters
        preview = text[:200].replace("\n", " ")
        print(f"Preview: {preview}...")
        print(f"Total length: {len(text)} characters")
        print()

    print()


def test_personnel_list():
    """Test personnel list loading."""
    print("=" * 60)
    print("Testing Personnel List")
    print("=" * 60)

    names = get_personnel_names()
    print(f"Total personnel names: {len(names)}")
    print(f"First 10 names: {', '.join(names[:10])}")
    print()


def test_name_extraction():
    """Test name extraction from document text."""
    print("=" * 60)
    print("Testing Name Extraction")
    print("=" * 60)

    word_files = get_word_files()

    # Simple name extraction (names in personnel list)
    from ga_audit.config import get_personnel_names
    personnel_names = set(get_personnel_names())

    for word_file in word_files[:3]:
        text = extract_text_from_docx(word_file)
        found_names = []

        for name in personnel_names:
            if name in text:
                found_names.append(name)

        print(f"File: {word_file.name}")
        print(f"Found names: {', '.join(found_names) if found_names else 'None'}")
        print()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("GA Audit - Test Suite")
    print("=" * 60 + "\n")

    test_normalize_filename()
    test_get_word_files()
    test_extract_text()
    test_personnel_list()
    test_name_extraction()

    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\nNote: To use AI audit features, please set ZHIPUAI_API_KEY in .env file")
    print("To use PDF conversion, please install LibreOffice:")
    print("  brew install --cask libreoffice")


if __name__ == "__main__":
    main()
