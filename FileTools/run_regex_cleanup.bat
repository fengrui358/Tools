@echo off
chcp 65001 >nul
echo ========================================
echo   正则表达式文件清理工具启动脚本
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
echo   run_regex_cleanup.bat [文件夹路径] [选项]
echo.
echo 选项:
echo   -p [模式]       正则表达式模式（可多次使用）
echo   -c [配置文件]   指定配置文件路径（JSON格式）
echo   -l [日志文件]   指定日志文件路径
echo   -d             预览模式（不实际删除）
echo   -nr            不递归扫描子目录
echo   -example       创建示例配置文件
echo.
echo 示例:
echo   run_regex_cleanup.bat C:\MyFiles
echo   run_regex_cleanup.bat D:\Documents -d
echo   run_regex_cleanup.bat E:\TestFolder -p ".*\.tmp$" -p ".*\.log$"
echo   run_regex_cleanup.bat F:\Data -c cleanup_rules.json
echo   run_regex_cleanup.bat -example
echo.

REM 如果没有参数，显示帮助信息
if "%~1"=="" (
    echo 请指定要扫描的文件夹路径或使用选项
    echo 使用 -example 创建示例配置文件
    pause
    exit /b 1
)

REM 构建Python命令
set "PYTHON_CMD=python regex_cleanup.py"

REM 处理参数
:parse_args
if "%~1"=="" goto execute

if "%~1"=="-p" (
    shift
    set "PYTHON_CMD=%PYTHON_CMD% --pattern "%~1""
    shift
    goto parse_args
)

if "%~1"=="-c" (
    shift
    set "PYTHON_CMD=%PYTHON_CMD% --config "%~1""
    shift
    goto parse_args
)

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

if "%~1"=="-nr" (
    set "PYTHON_CMD=%PYTHON_CMD% --no-recursive"
    shift
    goto parse_args
)

if "%~1"=="-example" (
    set "PYTHON_CMD=%PYTHON_CMD% --create-example-config"
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
if exist regex_cleanup.log (
    echo 日志文件已保存到: regex_cleanup.log
)
if exist cleanup_patterns_example.json (
    echo 示例配置文件已创建: cleanup_patterns_example.json
)
pause
