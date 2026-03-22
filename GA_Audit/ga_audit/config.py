"""Configuration settings for GA Audit."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
WORD_DIR = PROJECT_ROOT / "Word"
REQUIREMENT_DIR = PROJECT_ROOT / "考核要求"
PERSONNEL_FILE = PROJECT_ROOT / "人员名单" / "人员.md"

# GLM API settings
GLM_API_PATH = Path("/Users/free/WorkSpace/GLM-API")
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")

# Model settings
DEFAULT_MODEL = "glm-4-flash"
MAX_TOKENS = 4096
TEMPERATURE = 0.3

# Personnel list - names to validate against
PERSONNEL_NAMES = [
    "黄长亮", "陈星龙", "李浩", "刘光礼", "王亮", "温鹏", "吴俊杰",
    "张国强", "张兆敏", "仲新", "赵吉宏", "张廷玉", "刘振江", "李有军",
    "田庸", "黄耀年", "严鑫", "高乙圣", "邹勰", "何东先", "李浪",
    "魏超", "王春龙", "杨林", "张德智", "张奥", "杨桥", "龙昌伟",
    "汪飞", "王远东", "王晨彪", "王浩", "李兰君", "付智琦", "郑鑫洋",
    "陈勉"
]


def get_personnel_names() -> list[str]:
    """Get personnel names from file or use default list."""
    if PERSONNEL_FILE.exists():
        content = PERSONNEL_FILE.read_text(encoding="utf-8")
        # Parse names from the file (comma or Chinese comma separated)
        names = [name.strip() for name in content.replace("、", ",").split(",")]
        return [n for n in names if n]
    return PERSONNEL_NAMES
