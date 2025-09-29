@echo off
echo Installing ComputerControl Service...

nssm install ComputerControl "C:\Users\fengr\AppData\Local\Programs\Python\Python311\python.exe" "C:\WorkSpace\Tools\ComputerControl\server.py"
nssm set ComputerControl AppDirectory "C:\WorkSpace\Tools\ComputerControl\"
nssm set ComputerControl AppStdout "C:\WorkSpace\Tools\ComputerControl\stdout.log"
nssm set ComputerControl AppStderr "C:\WorkSpace\Tools\ComputerControl\stderr.log"

echo Service installed successfully!
echo To start the service: net start ComputerControl
echo To stop the service: net stop ComputerControl
pause