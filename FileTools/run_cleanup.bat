@echo off
chcp 65001 >nul
echo ========================================
echo   文件清理工具启动脚本
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
echo   run_cleanup.bat [文件夹路径] [选项]
echo.
echo 选项:
echo   -l [日志文件]   指定日志文件路径
echo   -d             预览模式（不实际删除）
echo.
echo 示例:
echo   run_cleanup.bat C:\MyFiles
echo   run_cleanup.bat D:\Documents -l C:\Logs\cleanup.log
echo   run_cleanup.bat E:\TestFolder -d
echo.

REM 如果没有参数，显示帮助信息
if "%~1"=="" (
    echo 请指定要扫描的文件夹路径
    pause
    exit /b 1
)

REM 构建Python命令
set "PYTHON_CMD=python file_cleanup.py"

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
echo 清理完成!
if exist file_cleanup.log (
    echo 日志文件已保存到: file_cleanup.log
)
pause
