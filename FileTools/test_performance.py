#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
性能测试脚本 - 测试优化后的文件哈希计算速度
"""

import os
import time
import tempfile
from file_cleanup import FileCleanupTool

def create_test_file(size_mb, file_path):
    """创建测试文件"""
    size_bytes = size_mb * 1024 * 1024
    with open(file_path, 'wb') as f:
        # 写入随机数据
        f.write(os.urandom(size_bytes))
    return file_path

def test_hash_performance():
    """测试哈希计算性能"""
    print("=" * 60)
    print("文件哈希计算性能测试")
    print("=" * 60)
    
    # 创建临时目录用于测试
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建不同大小的测试文件
        test_files = []
        sizes = [10, 100, 500, 1000, 2000]  # MB
        
        print("创建测试文件...")
        for size in sizes:
            file_path = os.path.join(temp_dir, f"test_{size}MB.dat")
            create_test_file(size, file_path)
            test_files.append((size, file_path))
            print(f"创建了 {size}MB 测试文件")
        
        print("\n开始性能测试...")
        
        # 测试优化后的哈希计算
        tool = FileCleanupTool(temp_dir, dry_run=True)
        
        for size, file_path in test_files:
            print(f"\n测试 {size}MB 文件:")
            
            # 测试单文件哈希计算
            start_time = time.time()
            hash_result = tool.calculate_file_hash(file_path)
            end_time = time.time()
            
            duration = end_time - start_time
            speed = size / duration if duration > 0 else 0
            
            print(f"  哈希值: {hash_result[:16]}...")
            print(f"  耗时: {duration:.2f} 秒")
            print(f"  速度: {speed:.2f} MB/秒")
        
        print("\n" + "=" * 60)
        print("性能测试完成")
        print("=" * 60)

if __name__ == "__main__":
    test_hash_performance()
