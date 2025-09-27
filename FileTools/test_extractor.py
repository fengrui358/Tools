#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
压缩文件解压工具测试脚本
"""

import os
import tempfile
import zipfile
import tarfile
import gzip
from pathlib import Path
from archive_extractor import ArchiveExtractor

def create_test_archive(archive_type, file_path, content_files):
    """创建测试压缩文件"""
    if archive_type == 'zip':
        with zipfile.ZipFile(file_path, 'w') as zipf:
            for filename, content in content_files.items():
                zipf.writestr(filename, content)
    
    elif archive_type == 'tar':
        with tarfile.open(file_path, 'w') as tarf:
            for filename, content in content_files.items():
                # 创建临时文件
                temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
                temp_file.write(content)
                temp_file.close()
                
                # 添加到tar文件
                tarf.add(temp_file.name, arcname=filename)
                
                # 删除临时文件
                os.unlink(temp_file.name)
    
    elif archive_type == 'gz':
        with gzip.open(file_path, 'wt') as gzf:
            # GZIP通常只压缩单个文件
            first_filename = list(content_files.keys())[0]
            gzf.write(content_files[first_filename])

def test_basic_functionality():
    """测试基本功能"""
    print("=" * 60)
    print("压缩文件解压工具基本功能测试")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试压缩文件
        test_files = {
            'test1.txt': '这是测试文件1的内容',
            'test2.txt': '这是测试文件2的内容',
            'subfolder/test3.txt': '这是子文件夹中的测试文件3'
        }
        
        zip_path = os.path.join(temp_dir, 'test.zip')
        create_test_archive('zip', zip_path, test_files)
        
        print(f"创建测试ZIP文件: {zip_path}")
        print(f"文件大小: {os.path.getsize(zip_path)} 字节")
        
        # 测试解压功能
        extractor = ArchiveExtractor(temp_dir, dry_run=False)
        
        # 扫描压缩文件
        archives = extractor.scan_archive_files()
        print(f"扫描到的压缩文件: {archives}")
        
        # 解压文件
        success, files_extracted = extractor.extract_archive(zip_path)
        print(f"解压结果: 成功={success}, 提取文件数={files_extracted}")
        
        # 检查解压后的文件
        extracted_files = []
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file != 'test.zip':  # 排除原压缩文件
                    file_path = os.path.join(root, file)
                    extracted_files.append(file_path)
        
        print(f"解压后的文件: {extracted_files}")
        
        # 验证文件内容
        for filename, expected_content in test_files.items():
            file_path = os.path.join(temp_dir, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content == expected_content:
                        print(f"✓ 文件 {filename} 内容正确")
                    else:
                        print(f"✗ 文件 {filename} 内容不正确")
            else:
                print(f"✗ 文件 {filename} 不存在")

def test_recursive_extraction():
    """测试递归解压功能"""
    print("\n" + "=" * 60)
    print("递归解压功能测试")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建嵌套的压缩文件
        inner_files = {'inner.txt': '内部文件内容'}
        inner_zip_path = os.path.join(temp_dir, 'inner.zip')
        create_test_archive('zip', inner_zip_path, inner_files)
        
        # 创建外层压缩文件（包含内层压缩文件）
        outer_files = {
            'outer.txt': '外层文件内容',
            'inner.zip': ''  # 占位符，实际会用二进制内容
        }
        
        # 读取内层压缩文件的二进制内容
        with open(inner_zip_path, 'rb') as f:
            inner_zip_content = f.read()
        
        outer_zip_path = os.path.join(temp_dir, 'outer.zip')
        with zipfile.ZipFile(outer_zip_path, 'w') as zipf:
            zipf.writestr('outer.txt', '外层文件内容')
            zipf.writestr('inner.zip', inner_zip_content)
        
        print(f"创建嵌套压缩文件结构")
        print(f"外层ZIP: {outer_zip_path}")
        print(f"内层ZIP: {inner_zip_path}")
        
        # 测试递归解压
        extractor = ArchiveExtractor(temp_dir, dry_run=False)
        success = extractor.run_recursive_extraction(max_iterations=3)
        
        print(f"递归解压结果: {success}")
        print(f"统计信息: {extractor.stats}")
        
        # 检查最终文件结构
        final_files = []
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, temp_dir)
                final_files.append(relative_path)
        
        print(f"最终文件结构: {final_files}")

def test_dry_run_mode():
    """测试预览模式"""
    print("\n" + "=" * 60)
    print("预览模式测试")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件
        test_files = {'test.txt': '测试内容'}
        zip_path = os.path.join(temp_dir, 'test.zip')
        create_test_archive('zip', zip_path, test_files)
        
        print(f"创建测试文件: {zip_path}")
        
        # 使用预览模式
        extractor = ArchiveExtractor(temp_dir, dry_run=True)
        archives = extractor.scan_archive_files()
        
        print(f"扫描到的压缩文件: {archives}")
        
        # 尝试解压（应该只显示预览信息）
        success, files_extracted = extractor.extract_archive(zip_path)
        print(f"预览模式解压结果: 成功={success}, 提取文件数={files_extracted}")
        
        # 检查文件是否真的被解压（不应该被解压）
        extracted_file = os.path.join(temp_dir, 'test.txt')
        if os.path.exists(extracted_file):
            print("✗ 预览模式下文件被实际解压了")
        else:
            print("✓ 预览模式下文件没有被实际解压")

def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("错误处理测试")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 测试不存在的文件
        extractor = ArchiveExtractor(temp_dir)
        
        # 测试不支持的格式
        invalid_file = os.path.join(temp_dir, 'test.invalid')
        with open(invalid_file, 'w') as f:
            f.write('这不是压缩文件')
        
        success, files_extracted = extractor.extract_archive(invalid_file)
        print(f"不支持格式测试: 成功={success}, 提取文件数={files_extracted}")
        
        # 测试损坏的压缩文件
        corrupt_zip = os.path.join(temp_dir, 'corrupt.zip')
        with open(corrupt_zip, 'w') as f:
            f.write('这不是有效的ZIP文件内容')
        
        success, files_extracted = extractor.extract_archive(corrupt_zip)
        print(f"损坏文件测试: 成功={success}, 提取文件数={files_extracted}")

if __name__ == "__main__":
    print("开始压缩文件解压工具测试...")
    
    try:
        test_basic_functionality()
        test_recursive_extraction()
        test_dry_run_mode()
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
