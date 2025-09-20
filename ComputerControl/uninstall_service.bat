@echo off
echo Uninstalling ComputerControl Service...

REM 检查nssm是否存在
if not exist nssm.exe (
    echo nssm.exe not found. Please run install_service.bat first.
    pause
    exit /b 1
)

REM 停止服务
net stop ComputerControlService 2>nul

REM 卸载服务
nssm.exe remove ComputerControlService confirm

echo Service uninstalled successfully!
pause
