@echo off
echo Installing ComputerControl Service...

REM 下载nssm工具（如果不存在）
if not exist nssm.exe (
    echo Downloading nssm...
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'"
    powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath '.'"
    move nssm-2.24\win64\nssm.exe .
    rmdir /s /q nssm-2.24
    del nssm.zip
)

REM 安装服务
nssm.exe install ComputerControlService "python" "%~dp0server.py"
nssm.exe set ComputerControlService DisplayName "Computer Control Service"
nssm.exe set ComputerControlService Description "HTTP service for computer shutdown control"
nssm.exe set ComputerControlService Start SERVICE_AUTO_START

echo Service installed successfully!
echo To start the service: net start ComputerControlService
echo To stop the service: net stop ComputerControlService
pause
