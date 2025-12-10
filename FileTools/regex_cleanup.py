#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
正则表达式文件清理工具

功能：
1. 递归扫描指定文件夹下的所有文件和文件夹
2. 使用正则表达式匹配需要清理的文件名
3. 支持Windows和MacOS常见的临时文件、系统文件清理
4. 可配置的清理规则
5. 预览模式（dry-run）和安全删除
6. 详细的操作日志记录

使用示例：
python regex_cleanup.py /path/to/folder
python regex_cleanup.py /path/to/folder --dry-run
python regex_cleanup.py /path/to/folder --pattern ".*\\.tmp$"
python regex_cleanup.py /path/to/folder --config custom_rules.json

常见需要清理的文件模式（在正则表达式中用注释说明）：
Windows系统：
- 临时文件：~$* (Office临时文件), *.tmp, *.temp, *.~*, Thumbs.db, Desktop.ini
- 系统文件：*.log (日志文件), *.bak (备份文件), *.old (旧文件)
- 回收站文件：$RECYCLE.BIN\\*, .Trashes\\*

MacOS系统：
- 临时文件：.DS_Store, ._.* (资源派生文件), *.DS_Store
- 系统文件：*.log, *.tmp, .Spotlight-V100, .Trashes, .fseventsd
- 缓存文件：__pycache__\\*, *.pyc, *.pyo

通用模式：
- 隐藏文件：^\\.* (以点开头的文件)
- 版本控制文件：.git\\*, .svn\\*, .hg\\*
- IDE配置文件：.idea\\*, .vscode\\*, *.swp, *.swo
"""

import os
import sys
import re
import argparse
import json
import logging
import shutil
from datetime import datetime
from typing import List, Dict, Set, Optional, Pattern
import fnmatch

class RegexFileCleanup:
    def __init__(self, target_path: str, patterns: List[str] = None, 
                 config_file: str = None, dry_run: bool = False, 
                 log_file: str = None, recursive: bool = True):
        """
        初始化正则表达式文件清理工具
        
        Args:
            target_path: 目标文件夹路径
            patterns: 正则表达式模式列表（可选）
            config_file: 配置文件路径（JSON格式，可选）
            dry_run: 预览模式，不实际执行删除操作
            log_file: 日志文件路径（可选）
            recursive: 是否递归扫描子目录
        """
        self.target_path = os.path.abspath(target_path)
        self.dry_run = dry_run
        self.recursive = recursive
        self.log_file = log_file or os.path.join(os.path.dirname(__file__), "regex_cleanup.log")
        
        # 设置日志
        self.setup_logging()
        
        # 编译正则表达式模式
        self.patterns = self.load_patterns(patterns, config_file)
        
        # 统计信息
        self.stats = {
            'total_files_scanned': 0,
            'total_dirs_scanned': 0,
            'files_matched': 0,
            'files_removed': 0,
            'dirs_matched': 0,
            'dirs_removed': 0,
            'space_saved': 0,
            'errors': 0
        }
    
    def setup_logging(self):
        """设置日志配置"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        if level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "DEBUG":
            self.logger.debug(message)
    
    def load_patterns(self, patterns: List[str] = None, config_file: str = None) -> List[Pattern]:
        """
        加载正则表达式模式
        
        Args:
            patterns: 命令行提供的模式列表
            config_file: 配置文件路径
            
        Returns:
            编译后的正则表达式模式列表
        """
        compiled_patterns = []
        
        # 如果提供了配置文件，从配置文件加载
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if 'patterns' in config:
                    for pattern_str in config['patterns']:
                        try:
                            pattern = re.compile(pattern_str)
                            compiled_patterns.append(pattern)
                            self.log(f"从配置文件加载模式: {pattern_str}")
                        except re.error as e:
                            self.log(f"无效的正则表达式 '{pattern_str}': {e}", "WARNING")
            except Exception as e:
                self.log(f"加载配置文件失败: {config_file} - {str(e)}", "ERROR")
        
        # 如果命令行提供了模式，添加到列表
        if patterns:
            for pattern_str in patterns:
                try:
                    pattern = re.compile(pattern_str)
                    compiled_patterns.append(pattern)
                    self.log(f"从命令行加载模式: {pattern_str}")
                except re.error as e:
                    self.log(f"无效的正则表达式 '{pattern_str}': {e}", "WARNING")
        
        # 如果没有提供任何模式，使用默认模式
        if not compiled_patterns:
            compiled_patterns = self.get_default_patterns()
            self.log("使用默认清理模式")
        
        return compiled_patterns
    
    def get_default_patterns(self) -> List[Pattern]:
        """
        获取默认的正则表达式模式
        
        包含Windows和MacOS常见的需要清理的文件模式
        在注释中详细说明每种模式的用途
        
        Returns:
            编译后的正则表达式模式列表
        """
        default_patterns = [
            # Windows系统常见临时文件
            r'~\$.*',           # Office临时文件（如~$Document.docx）
            r'.*\.tmp$',        # 临时文件
            r'.*\.temp$',       # 临时文件
            r'.*\.~.*',         # 备份文件（如Document~1.docx）
            r'^Thumbs\.db$',    # Windows缩略图缓存
            r'^Desktop\.ini$',  # Windows文件夹自定义设置
            
            # MacOS系统常见文件
            r'^\.DS_Store$',    # MacOS文件夹元数据
            r'^\._.*',          # MacOS资源派生文件（如._Document）
            r'.*\.DS_Store$',   # MacOS DS_Store文件
            
            # 通用临时和缓存文件
            r'.*\.log$',        # 日志文件
            r'.*\.bak$',        # 备份文件
            r'.*\.old$',        # 旧版本文件
            r'.*\.cache$',      # 缓存文件
            r'.*\.swp$',        # Vim交换文件
            r'.*\.swo$',        # Vim交换文件
            
            # 隐藏文件（以点开头）
            r'^\..*',
            
            # Python缓存文件
            r'.*\.pyc$',        # Python编译文件
            r'.*\.pyo$',        # Python优化编译文件
            r'^__pycache__$',   # Python缓存目录
            
            # 版本控制目录
            r'^\.git$',         # Git目录
            r'^\.svn$',         # SVN目录
            r'^\.hg$',          # Mercurial目录
            
            # IDE和编辑器文件
            r'^\.idea$',        # IntelliJ IDEA配置
            r'^\.vscode$',      # VS Code配置
            r'^\.vs$',          # Visual Studio配置
        ]
        
        compiled = []
        for pattern_str in default_patterns:
            try:
                pattern = re.compile(pattern_str, re.IGNORECASE)  # 不区分大小写
                compiled.append(pattern)
            except re.error as e:
                self.log(f"编译默认模式失败 '{pattern_str}': {e}", "ERROR")
        
        return compiled
    
    def matches_any_pattern(self, name: str) -> bool:
        """
        检查文件名是否匹配任何正则表达式模式
        
        Args:
            name: 文件名
            
        Returns:
            如果匹配任何模式返回True，否则返回False
        """
        for pattern in self.patterns:
            if pattern.search(name):
                return True
        return False
    
    def scan_directory(self) -> Dict[str, List[str]]:
        """
        扫描目录，查找匹配的文件和文件夹
        
        Returns:
            字典：{'files': [文件路径列表], 'dirs': [文件夹路径列表]}
        """
        self.log(f"开始扫描目录: {self.target_path}")
        
        matched_files = []
        matched_dirs = []
        
        try:
            if self.recursive:
                # 递归扫描
                for root, dirs, files in os.walk(self.target_path):
                    self.stats['total_dirs_scanned'] += 1
                    
                    # 检查当前目录名是否匹配
                    dir_name = os.path.basename(root)
                    if self.matches_any_pattern(dir_name):
                        matched_dirs.append(root)
                        self.log(f"匹配的目录: {root}", "DEBUG")
                    
                    # 检查文件
                    for file in files:
                        file_path = os.path.join(root, file)
                        self.stats['total_files_scanned'] += 1
                        
                        if self.matches_any_pattern(file):
                            matched_files.append(file_path)
                            self.log(f"匹配的文件: {file_path}", "DEBUG")
                            
                            # 每100个文件报告一次进度
                            if self.stats['total_files_scanned'] % 100 == 0:
                                self.log(f"已扫描 {self.stats['total_files_scanned']} 个文件...")
            else:
                # 仅扫描当前目录
                self.stats['total_dirs_scanned'] += 1
                
                # 检查当前目录
                dir_name = os.path.basename(self.target_path)
                if self.matches_any_pattern(dir_name):
                    matched_dirs.append(self.target_path)
                
                # 检查文件
                for item in os.listdir(self.target_path):
                    item_path = os.path.join(self.target_path, item)
                    
                    if os.path.isfile(item_path):
                        self.stats['total_files_scanned'] += 1
                        
                        if self.matches_any_pattern(item):
                            matched_files.append(item_path)
                            self.log(f"匹配的文件: {item_path}", "DEBUG")
            
            self.stats['files_matched'] = len(matched_files)
            self.stats['dirs_matched'] = len(matched_dirs)
            
            self.log(f"扫描完成: 共扫描 {self.stats['total_files_scanned']} 个文件和 {self.stats['total_dirs_scanned']} 个目录")
            self.log(f"匹配结果: {self.stats['files_matched']} 个文件, {self.stats['dirs_matched']} 个目录")
            
            return {'files': matched_files, 'dirs': matched_dirs}
            
        except Exception as e:
            self.log(f"扫描目录时发生错误: {str(e)}", "ERROR")
            self.stats['errors'] += 1
            return {'files': [], 'dirs': []}
    
    def remove_file(self, file_path: str) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            成功返回True，失败返回False
        """
        try:
            if self.dry_run:
                self.log(f"[预览] 将删除文件: {file_path}")
                return True
            
            # 获取文件大小（用于统计）
            file_size = os.path.getsize(file_path)
            
            # 删除文件
            os.remove(file_path)
            
            self.log(f"已删除文件: {file_path}")
            self.stats['files_removed'] += 1
            self.stats['space_saved'] += file_size
            
            return True
            
        except Exception as e:
            self.log(f"删除文件失败: {file_path} - {str(e)}", "ERROR")
            self.stats['errors'] += 1
            return False
    
    def remove_directory(self, dir_path: str) -> bool:
        """
        删除目录（递归删除）
        
        Args:
            dir_path: 目录路径
            
        Returns:
            成功返回True，失败返回False
        """
        try:
            if self.dry_run:
                self.log(f"[预览] 将删除目录: {dir_path}")
                return True
            
            # 递归删除目录
            shutil.rmtree(dir_path)
            
            self.log(f"已删除目录: {dir_path}")
            self.stats['dirs_removed'] += 1
            
            return True
            
        except Exception as e:
            self.log(f"删除目录失败: {dir_path} - {str(e)}", "ERROR")
            self.stats['errors'] += 1
            return False
    
    def cleanup(self, matches: Dict[str, List[str]]):
        """
        执行清理操作
        
        Args:
            matches: 匹配的文件和目录
        """
        self.log("开始清理操作...")
        
        # 先删除文件
        if matches['files']:
            self.log(f"准备删除 {len(matches['files'])} 个匹配的文件...")
            
            for file_path in matches['files']:
                self.remove_file(file_path)
        
        # 再删除目录（按路径长度排序，先删除最深层的目录）
        if matches['dirs']:
            self.log(f"准备删除 {len(matches['dirs'])} 个匹配的目录...")
            
            # 按路径长度排序，先删除最深层的目录
            sorted_dirs = sorted(matches['dirs'], key=len, reverse=True)
            
            for dir_path in sorted_dirs:
                # 检查目录是否仍然存在（可能已经被父目录删除）
                if os.path.exists(dir_path):
                    self.remove_directory(dir_path)
        
        # 输出统计信息
        self.log("=" * 60)
        self.log("清理操作完成统计:")
        self.log(f"扫描的文件数: {self.stats['total_files_scanned']}")
        self.log(f"扫描的目录数: {self.stats['total_dirs_scanned']}")
        self.log(f"匹配的文件数: {self.stats['files_matched']}")
        self.log(f"匹配的目录数: {self.stats['dirs_matched']}")
        self.log(f"删除的文件数: {self.stats['files_removed']}")
        self.log(f"删除的目录数: {self.stats['dirs_removed']}")
        
        if self.stats['space_saved'] > 0:
            space_saved_mb = self.stats['space_saved'] / (1024 * 1024)
            self.log(f"节省的空间: {space_saved_mb:.2f} MB")
        
        if self.stats['errors'] > 0:
            self.log(f"发生的错误数: {self.stats['errors']}", "WARNING")
        
        self.log("=" * 60)
    
    def run(self):
        """运行清理工具"""
        self.log("=" * 60)
        self.log("正则表达式文件清理工具启动")
        self.log(f"目标路径: {self.target_path}")
        self.log(f"日志文件: {self.log_file}")
        self.log(f"递归扫描: {'是' if self.recursive else '否'}")
        self.log(f"模式数量: {len(self.patterns)}")
        
        if self.dry_run:
            self.log("运行模式: 预览模式（不实际执行删除操作）")
        
        # 显示使用的模式
        self.log("使用的正则表达式模式:")
        for i, pattern in enumerate(self.patterns, 1):
            self.log(f"  {i}. {pattern.pattern}")
        
        self.log("=" * 60)
        
        try:
            # 检查目标路径是否存在
            if not os.path.exists(self.target_path):
                self.log(f"错误：指定的路径 '{self.target_path}' 不存在", "ERROR")
                return
            
            if not os.path.isdir(self.target_path):
                self.log(f"错误：'{self.target_path}' 不是一个文件夹", "ERROR")
                return
            
            # 扫描目录
            matches = self.scan_directory()
            
            # 如果没有匹配项，直接返回
            if not matches['files'] and not matches['dirs']:
                self.log("没有找到匹配的文件或目录，无需清理")
                return
            
            # 执行清理
            self.cleanup(matches)
            
        except Exception as e:
            self.log(f"工具执行过程中发生错误: {str(e)}", "ERROR")
            import traceback
            self.log(f"堆栈跟踪: {traceback.format_exc()}", "ERROR")


def create_example_config():
    """创建示例配置文件"""
    example_config = {
        "description": "正则表达式文件清理配置文件",
        "patterns": [
            r'~\$.*',
            r'.*\.tmp$',
            r'.*\.temp$',
            r'^\.DS_Store$',
            r'^\._.*',
            r'^Thumbs\.db$',
            r'^Desktop\.ini$',
            r'.*\.log$',
            r'.*\.bak$',
            r'.*\.old$',
            r'^\..*'
        ]
    }
    
    config_file = os.path.join(os.path.dirname(__file__), "cleanup_patterns_example.json")
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(example_config, f, indent=2, ensure_ascii=False)
        print(f"示例配置文件已创建: {config_file}")
        return True
    except Exception as e:
        print(f"创建示例配置文件失败: {str(e)}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="正则表达式文件清理工具 - 根据正则表达式模式清理文件和文件夹",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s /path/to/folder                    # 使用默认模式清理
  %(prog)s /path/to/folder --dry-run          # 预览模式，不实际删除
  %(prog)s /path/to/folder --pattern ".*\\.tmp$" --pattern ".*\\.log$"
  %(prog)s /path/to/folder --config custom_rules.json
  %(prog)s --create-example-config            # 创建示例配置文件
  
默认清理模式包括:
  - Windows临时文件: ~$*, *.tmp, *.temp, Thumbs.db, Desktop.ini
  - MacOS系统文件: .DS_Store, ._*, *.DS_Store
  - 通用临时文件: *.log, *.bak, *.old, *.cache
  - 隐藏文件: .*
  - 缓存目录: __pycache__, .git, .idea, .vscode
        """
    )
    
    parser.add_argument("path", nargs="?", help="要清理的目标文件夹路径")
    parser.add_argument("--pattern", "-p", action="append", 
                       help="正则表达式模式（可多次使用）")
    parser.add_argument("--config", "-c", help="配置文件路径（JSON格式）")
    parser.add_argument("--log", "-l", help="日志文件路径（可选）")
    parser.add_argument("--dry-run", "-d", action="store_true",
                       help="预览模式，只显示将要执行的操作而不实际执行")
    parser.add_argument("--no-recursive", action="store_true",
                       help="不递归扫描子目录")
    parser.add_argument("--create-example-config", action="store_true",
                       help="创建示例配置文件并退出")
    
    args = parser.parse_args()
    
    # 如果请求创建示例配置文件
    if args.create_example_config:
        create_example_config()
        return
    
    # 检查必要的参数
    if not args.path:
        parser.error("必须指定目标文件夹路径")
    
    # 运行清理工具
    tool = RegexFileCleanup(
        target_path=args.path,
        patterns=args.pattern,
        config_file=args.config,
        dry_run=args.dry_run,
        log_file=args.log,
        recursive=not args.no_recursive
    )
    
    tool.run()


if __name__ == "__main__":
    main()
