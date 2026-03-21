# GA Audit - Word转PDF工具 + AI内容审核

一个Python工具，用于将Word文档转换为PDF，并使用GLM大模型进行内容审核和人员名单检查。

## 功能

- 📄 **Word转PDF**: 批量转换Word文档为PDF格式
- 📁 **智能文件名处理**: 自动处理不以"2024年"或"2025年"开头的文件名
- 🤖 **AI内容审核**: 使用GLM大模型检查文档是否符合考核要求
- 👥 **人员名单检查**: 验证文档中的人名是否都在人员名单中
- ⏰ **时间戳输出**: PDF输出到带时间戳的文件夹（`pdf_年月日时分秒`）

## 安装

### 1. 安装依赖

项目使用GLM-API的虚拟环境，无需额外安装依赖。

### 2. 配置API密钥

在 `.env` 文件中设置你的智谱AI API密钥：

```bash
# 编辑 .env 文件
ZHIPUAI_API_KEY=your_api_key_here
```

获取API密钥：https://open.bigmodel.cn/

### 4. 安装 LibreOffice（用于Word转PDF）

```bash
# macOS
brew install --cask libreoffice

# Ubuntu/Debian
sudo apt-get install libreoffice

# Windows
# 从 https://www.libreoffice.org/ 下载安装
```

## 使用方法

### 快速开始

```bash
cd /Users/free/WorkSpace/Tools-1/GA_Audit

# 运行测试（验证功能）
./ga-audit.sh test

# 转换Word为PDF（需要安装LibreOffice）
./ga-audit.sh convert

# AI内容审核（需要设置API密钥）
./ga-audit.sh audit

# 完整流程（转换+审核）
./ga-audit.sh all
```

### 使用Python直接运行

```bash
# 运行测试
/Users/free/WorkSpace/GLM-API/.venv/bin/python test.py

# 运行主程序
/Users/free/WorkSpace/GLM-API/.venv/bin/python run.py convert
/Users/free/WorkSpace/GLM-API/.venv/bin/python run.py audit
/Users/free/WorkSpace/GLM-API/.venv/bin/python run.py all
```

## 项目结构

```
GA_Audit/
├── Word/                    # 输入的Word文档
├── 考核要求/
│   └── 考核.docx           # 考核要求文档
├── 人员名单/
│   └── 人员.md             # 人员名单
├── ga_audit/
│   ├── __init__.py
│   ├── config.py           # 配置文件
│   ├── converter.py        # Word转PDF模块
│   ├── auditor.py          # AI审核模块
│   └── main.py             # 主入口
├── pyproject.toml          # 项目配置
├── .env                    # 环境变量（API密钥）
└── README.md
```

## 文件名处理规则

- 如果文件名以 **2024年** 或 **2025年** 开头，保持原样
- 如果不是，删除前面的内容，保留从"2024年"或"2025年"开始的部分
- 示例：
  - `【已检查】2025年12月感知源后端运维文档汇总.docx` → `2025年12月感知源后端运维文档汇总.docx`
  - `前缀内容2024年3月感知源后端运维文档汇总.docx` → `2024年3月感知源后端运维文档汇总.docx`

## AI审核说明

工具会使用GLM-4-Flash模型进行以下检查：

1. **内容合规性**: 检查文档是否符合考核要求
2. **问题识别**: 找出可能导致扣分的问题
3. **修改建议**: 提供具体的修改建议
4. **人员验证**: 验证文档中的人名是否都在人员名单中

## 注意事项

1. 首次使用需要配置智谱AI API密钥
2. Word转PDF需要安装LibreOffice或Microsoft Word
3. AI审核需要网络连接到智谱AI API
4. 人员名单文件位于 `人员名单/人员.md`

## 故障排查

### 转换失败
- 确保已安装LibreOffice
- 检查Word文件是否损坏

### API调用失败
- 检查API密钥是否正确
- 确认网络连接正常
- 检查API余额是否充足

### 找不到模块
```bash
# 重新安装依赖
uv sync
```
