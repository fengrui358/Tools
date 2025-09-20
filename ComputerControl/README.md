# Computer Control Service

一个HTTP服务，提供远程关机功能接口。

## 功能
- 提供 `/shutdown` POST接口
- 自动识别操作系统并执行相应关机命令
- 返回命令执行结果

## 安装为Windows服务

1. 以管理员身份运行 `install_service.bat`
2. 服务将自动安装并设置为开机启动

## 使用方法
```bash
curl -X POST http://localhost:8080/shutdown
```

## 服务管理命令
- 启动服务: `net start ComputerControlService`
- 停止服务: `net stop ComputerControlService`
- 卸载服务: 运行 `uninstall_service.bat`

## 注意事项
- 需要管理员权限执行关机命令
- 服务默认监听8080端口
