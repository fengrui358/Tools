# Computer Control Service

一个HTTP服务，提供远程关机和系统硬件信息查询功能。

## 功能
- 提供 `/shutdown` POST接口 - 远程关机
- 提供 `/system_info` GET接口 - 查询系统硬件信息
- 自动识别操作系统并执行相应关机命令
- 返回JSON格式的系统硬件信息

## 安装为Windows服务

1. 以管理员身份运行 `install_service.bat`
2. 服务将自动安装并设置为开机启动

## 使用方法

### 远程关机
```bash
curl -X POST http://localhost:23009/shutdown
```

### 查询系统硬件信息
```bash
curl http://localhost:23009/system_info
```

### 系统硬件信息包含：
- 系统基本信息（平台、架构、处理器等）
- CPU信息（核心数、使用率、频率等）
- 内存信息（总内存、可用内存、使用率等）
- 磁盘信息（各分区使用情况）
- 网络信息（发送/接收字节数、包数等）
- 系统运行时间

## 服务管理命令
- 启动服务: `net start ComputerControl`
- 停止服务: `net stop ComputerControl`
- 卸载服务: 运行 `uninstall_service.bat`

## 注意事项
- 需要管理员权限执行关机命令
- 服务默认监听23009端口
- 需要安装psutil库：`pip install psutil`
