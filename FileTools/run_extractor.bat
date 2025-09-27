@echo off
chcp 65001 >nul
echo ========================================
echo   压缩文件解压工具启动脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.6或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 显示使用说明
echo 使用方法:
echo   run_extractor.bat [文件夹路径] [选项]
echo.
echo 选项:
echo   -l [日志文件]   指定日志文件路径
echo   -d             预览模式（不实际解压和删除）
echo   -t [线程数]    指定最大线程数
echo   -k             解压后保留原压缩文件
echo   -m [迭代次数]  最大递归迭代次数
echo.
echo 示例:
echo   run_extractor.bat C:\MyFiles
echo   run_extractor.bat D:\Documents -l C:\Logs\extract.log
echo   run_extractor.bat E:\TestFolder -d -t 4
echo   run_extractor.bat F:\Archives -k -m 5
echo.

REM 如果没有参数，显示帮助信息
if "%~1"=="" (
    echo 请指定要扫描的文件夹路径
    pause
    exit /b 1
)

REM 构建Python命令
set "PYTHON_CMD=python archive_extractor.py"

REM 处理参数
:parse_args
if "%~1"=="" goto execute

if "%~1"=="-l" (
    shift
    set "PYTHON_CMD=%PYTHON_CMD% --log "%~1""
    shift
    goto parse_args
)

if "%~1"=="-d" (
    set "PYTHON_CMD=%PYTHON_CMD% --dry-run"
    shift
    goto parse_args
)

if "%~1"=="-t" (
    shift
    set "PYTHON_CMD=%PYTHON_CMD% --threads "%~1""
    shift
    goto parse_args
)

if "%~1"=="-k" (
    set "PYTHON_CMD=%PYTHON_CMD% --keep-archives"
    shift
    goto parse_args
)

if "%~1"=="-m" (
    shift
    set "PYTHON_CMD=%PYTHON_CMD% --max-iterations "%~1""
    shift
    goto parse_args
)

REM 第一个非选项参数作为目标路径
if not defined TARGET_PATH (
    set "TARGET_PATH=%~1"
    set "PYTHON_CMD=%PYTHON_CMD% "%TARGET_PATH%""
    shift
    goto parse_args
)

shift
goto parse_args

:execute
echo 执行命令: %PYTHON_CMD%
echo.
%PYTHON_CMD%

echo.
if %errorlevel% equ 0 (
    echo 解压任务完成!
) else (
    echo 解压任务完成，但遇到一些错误。
)

if exist archive_extractor.log (
    echo 日志文件已保存到: archive_extractor.log
)

echo.
echo 支持的压缩格式:
echo   ZIP (.zip), RAR (.rar), 7Z (.7z), TAR (.tar)
echo   GZIP (.gz, .tgz), BZIP2 (.bz2, .tbz2)
echo.
echo 注意: 如需支持RAR和7Z格式，请安装相应库:
echo   pip install rarfile py7zr
echo.

pause
