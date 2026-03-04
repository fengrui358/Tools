# Tools

## ComputerControl

计算机控制，用于通过 Http 接口远程控制计算机的开关机、重启、锁屏等操作

## CSprojectReferenceSwitchTool

切换目录下的工程引用，从本地目录工程引用切换为Nuget引用

## FileTools

文件工具集，包括文件去重、文件自动解压缩

## InvalidPostfixCheckTool

后缀校验，用于检查后缀是否含有无效的数字字符

## Word2ExcelFixer

1. 问题背景：从 Word 复制表格到 Excel 时，Word 一个单元格内的多行文本会被拆分成 Excel 的多个行，需将这些拆分的行合并回一个单元格。
2. 判断规则：属于同一原始 Word 单元格的 Excel 行，其对应单元格的上下边缘都有完整边框。
3. 技术要求：
   - 使用 uv 管理 Python 依赖；
   - 优先使用 openpyxl 库操作 Excel（支持读取边框、编辑单元格）；
   - 程序需包含异常处理（文件不存在、格式错误等）；
   - 输入：待修复的 Excel 文件路径（可手动指定）；
   - 输出：修复后的 Excel 文件（原文件目录下生成「文件名_fixed.xlsx」）；
   - 合并文本时保留原换行格式；
   - 删除合并后多余的空行/无效行。

请生成完整的可运行代码，包含：

- 依赖清单（pyproject.toml 或 requirements.txt）；
- uv 安装依赖的命令；
- 代码注释（关键逻辑、函数说明）；
- 运行示例（如何执行程序）。
