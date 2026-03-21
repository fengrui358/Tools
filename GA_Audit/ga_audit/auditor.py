"""AI-powered content audit using GLM API."""

import json
import re
import sys
from pathlib import Path
from typing import Any

from zhipuai import ZhipuAI

from .config import (
    DEFAULT_MODEL,
    GLM_API_PATH,
    MAX_TOKENS,
    PERSONNEL_NAMES,
    REQUIREMENT_DIR,
    TEMPERATURE,
    ZHIPUAI_API_KEY,
)
from .converter import extract_text_from_docx

# Add GLM API path to sys.path for imports
if str(GLM_API_PATH) not in sys.path:
    sys.path.insert(0, str(GLM_API_PATH))


class ContentAuditor:
    """AI-powered content auditor for document review."""

    def __init__(self, api_key: str | None = None):
        """Initialize the auditor with ZhipuAI client."""
        self.api_key = api_key or ZHIPUAI_API_KEY
        if not self.api_key:
            raise ValueError(
                "ZHIPUAI_API_KEY not found. Please set it in environment or .env file."
            )
        self.client = ZhipuAI(api_key=self.api_key)
        self.requirement_text = self._load_requirements()

    def _load_requirements(self) -> str:
        """Load assessment requirements from file."""
        req_file = REQUIREMENT_DIR / "考核.docx"
        if req_file.exists():
            return extract_text_from_docx(req_file)
        return "No requirements file found."

    def _call_glm(self, prompt: str, system_prompt: str | None = None) -> str:
        """Call GLM API with the given prompt."""

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling GLM API: {e}"

    def audit_content(self, document_text: str, filename: str) -> dict[str, Any]:
        """
        Audit document content against requirements.

        Args:
            document_text: Text content of the document
            filename: Name of the document being audited

        Returns:
            Dictionary with audit results
        """
        system_prompt = """你是一个专业的文档审核助手，负责审核运维文档是否符合考核要求。

你需要仔细分析文档内容，判断：
1. 文档内容是否完整对应考核要求
2. 是否存在可能导致扣分的问题
3. 哪些地方需要修改或补充

请以结构化的方式返回审核结果，明确指出需要修改的地方。"""

        user_prompt = f"""请审核以下文档是否符合考核要求。

文档名称: {filename}

考核要求:
{self.requirement_text[:2000]}

待审核文档内容:
{document_text[:4000]}

请返回JSON格式的审核结果，格式如下：
{{
    "is_compliant": true/false,
    "summary": "总体评价",
    "issues": [
        {{
            "category": "问题描述类型",
            "description": "具体问题描述",
            "suggestion": "修改建议"
        }}
    ],
    "missing_items": ["缺失的内容项"]
}}"""

        response = self._call_glm(user_prompt, system_prompt)

        # Try to parse JSON response
        try:
            # Extract JSON from response if it contains extra text
            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {
                    "is_compliant": False,
                    "summary": response,
                    "issues": [],
                    "missing_items": []
                }
        except json.JSONDecodeError:
            result = {
                "is_compliant": False,
                "summary": response,
                "issues": [{"category": "解析错误", "description": response, "suggestion": "请手动审核"}],
                "missing_items": []
            }

        result["raw_response"] = response
        return result

    def extract_names(self, text: str) -> list[str]:
        """
        Extract Chinese names from text.

        Args:
            text: Text content to extract names from

        Returns:
            List of extracted names
        """
        # Pattern for Chinese names (2-4 characters)
        name_pattern = r"[\u4e00-\u9fa5]{2,4}"
        names = re.findall(name_pattern, text)

        # Filter out common non-name words
        exclude_words = {
            "文档", "汇总", "运维", "感知", "源", "后端", "前端", "系统", "服务",
            "检查", "测试", "部署", "监控", "日志", "数据", "接口", "配置",
            "问题", "解决", "方法", "说明", "记录", "报告", "月份", "年度",
            "考核", "要求", "内容", "项目", "工作", "完成", "情况", "处理",
            "结果", "分析", "评估", "结论", "建议", "时间", "日期", "人员",
            "部门", "负责", "参与", "协助", "支持", "提供", "确认", "审核",
            "批准", "签字", "日期", "备注", "附件", "说明", "注意", "重要",
        }

        personnel_names_set = set(PERSONNEL_NAMES)
        filtered_names = []

        for name in names:
            if name in personnel_names_set:
                filtered_names.append(name)
            elif len(name) >= 2 and name not in exclude_words:
                # Check if it looks like a name (surname check)
                common_surnames = {
                    "王", "李", "张", "刘", "陈", "杨", "黄", "赵", "周", "吴",
                    "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
                    "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧",
                    "程", "曹", "袁", "邓", "许", "傅", "沈", "曾", "彭", "吕",
                }
                if name[0] in common_surnames:
                    filtered_names.append(name)

        return list(set(filtered_names))

    def check_personnel(self, document_text: str, filename: str) -> dict[str, Any]:
        """
        Check if all names in document are in the personnel list.

        Args:
            document_text: Text content of the document
            filename: Name of the document being checked

        Returns:
            Dictionary with check results
        """
        personnel_list = PERSONNEL_NAMES
        extracted_names = self.extract_names(document_text)

        # Filter to only names in our personnel list
        found_in_list = [n for n in extracted_names if n in personnel_list]
        not_in_list = [n for n in extracted_names if n not in personnel_list]

        return {
            "filename": filename,
            "total_names_found": len(extracted_names),
            "names_in_list": found_in_list,
            "names_not_in_list": not_in_list,
            "has_unknown_names": len(not_in_list) > 0,
        }


def audit_document(docx_path: Path, auditor: ContentAuditor) -> dict[str, Any]:
    """
    Perform complete audit on a document.

    Args:
        docx_path: Path to the Word document
        auditor: ContentAuditor instance

    Returns:
        Dictionary with complete audit results
    """
    filename = docx_path.name
    document_text = extract_text_from_docx(docx_path)

    result = {
        "filename": filename,
        "content_audit": auditor.audit_content(document_text, filename),
        "personnel_check": auditor.check_personnel(document_text, filename),
    }

    return result


def audit_all_documents() -> dict[str, Any]:
    """
    Audit all Word documents in the Word directory.

    Returns:
        Dictionary with all audit results
    """
    from .config import WORD_DIR

    if not ZHIPUAI_API_KEY:
        return {
            "status": "error",
            "message": "ZHIPUAI_API_KEY not set. Please set it in .env file."
        }

    try:
        auditor = ContentAuditor()
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    word_files = list(WORD_DIR.glob("*.docx")) + list(WORD_DIR.glob("*.doc"))

    results = {
        "status": "success",
        "total_documents": len(word_files),
        "audits": [],
        "summary": {
            "compliant": 0,
            "needs_review": 0,
            "unknown_names_found": False
        }
    }

    for word_file in word_files:
        audit_result = audit_document(word_file, auditor)
        results["audits"].append(audit_result)

        # Update summary
        if audit_result["content_audit"].get("is_compliant"):
            results["summary"]["compliant"] += 1
        else:
            results["summary"]["needs_review"] += 1

        if audit_result["personnel_check"]["has_unknown_names"]:
            results["summary"]["unknown_names_found"] = True

    return results
