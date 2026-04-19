# day09_tools.py
import json
from typing import Dict, Any, List


# ---------- 1. 查询天气（模拟）----------
def get_weather(city: str, date: str = "today") -> Dict[str, Any]:
    """
    模拟查询天气 API
    :param city: 城市名称
    :param date: 日期，默认 "today"
    :return: 包含天气信息的字典
    """
    # 参数校验
    if not isinstance(city, str) or len(city.strip()) == 0:
        raise ValueError("城市名必须是非空字符串")
    if date not in ["today", "tomorrow", "2026-04-15"]:  # 简单模拟允许的值
        date = "today"

    # 模拟数据
    weather_db = {
        "北京": {"today": "晴, 22°C", "tomorrow": "多云, 24°C"},
        "上海": {"today": "小雨, 18°C", "tomorrow": "阴, 20°C"},
        "深圳": {"today": "雷阵雨, 28°C", "tomorrow": "晴, 30°C"},
    }
    city_info = weather_db.get(city, {})
    weather = city_info.get(date, "未知")
    return {"city": city, "date": date, "weather": weather}


# 天气工具的 JSON Schema
weather_tool_schema = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询指定城市在指定日期的天气情况",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，如'北京'、'上海'"
                },
                "date": {
                    "type": "string",
                    "enum": ["today", "tomorrow"],
                    "description": "日期，默认为 today"
                }
            },
            "required": ["city"]
        }
    }
}


# ---------- 2. 查询知识库 ----------
def query_knowledge_base(query: str, top_k: int = 2) -> List[Dict[str, Any]]:
    """
    模拟向量数据库检索
    :param query: 用户问题或关键词
    :param top_k: 返回最相关的前 k 条结果
    :return: 列表，每个元素是 {"content": "...", "score": 0.xx}
    """
    if not isinstance(query, str) or len(query) < 2:
        raise ValueError("查询字符串长度至少为2")
    if not isinstance(top_k, int) or top_k < 1:
        top_k = 2

    # 模拟知识库内容
    fake_kb = {
        "会议": "会议纪要应包含议题、决策、待办事项。",
        "人工智能": "AI 是模拟人类智能的计算机科学分支。",
        "天气预报": "天气预报通过气象卫星和数值模型生成。",
        "Python": "Python 是一种解释型、高级编程语言。"
    }
    # 非常简单的关键词匹配（真实场景用向量检索）
    results = []
    for key, content in fake_kb.items():
        if key in query or query in key:
            results.append({"content": content, "score": 0.9})
    if not results:
        results.append({"content": "知识库中未找到相关信息。", "score": 0.0})
    return results[:top_k]


kb_tool_schema = {
    "type": "function",
    "function": {
        "name": "query_knowledge_base",
        "description": "从公司内部知识库中检索与问题相关的内容",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "要检索的问题或关键词"
                },
                "top_k": {
                    "type": "integer",
                    "description": "返回最相关的结果数量，默认2",
                    "default": 2,
                    "minimum": 1,
                    "maximum": 5
                }
            },
            "required": ["query"]
        }
    }
}


# ---------- 3. 发送摘要（模拟）----------
def send_summary(recipient: str, subject: str, content: str) -> Dict[str, Any]:
    """
    模拟发送邮件或通知
    :param recipient: 接收者邮箱或ID
    :param subject: 主题
    :param content: 摘要正文
    :return: 发送状态
    """
    # 参数校验
    if not recipient or "@" not in recipient:
        raise ValueError("请提供有效的邮箱地址")
    if not subject or len(subject) > 200:
        raise ValueError("主题不能为空且不超过200字符")
    if not content or len(content) < 5:
        raise ValueError("摘要内容至少5个字符")

    # 模拟发送成功
    print(f"\n[模拟发送] 收件人: {recipient}\n主题: {subject}\n内容: {content}\n")
    return {"status": "success", "message": "摘要已发送"}


summary_tool_schema = {
    "type": "function",
    "function": {
        "name": "send_summary",
        "description": "将生成的摘要通过邮件发送给指定人员",
        "parameters": {
            "type": "object",
            "properties": {
                "recipient": {
                    "type": "string",
                    "format": "email",
                    "description": "收件人邮箱地址"
                },
                "subject": {
                    "type": "string",
                    "description": "邮件主题"
                },
                "content": {
                    "type": "string",
                    "description": "摘要正文"
                }
            },
            "required": ["recipient", "subject", "content"]
        }
    }
}

# 工具列表（方便外部调用）
ALL_TOOLS = {
    "get_weather": {"func": get_weather, "schema": weather_tool_schema},
    "query_knowledge_base": {"func": query_knowledge_base, "schema": kb_tool_schema},
    "send_summary": {"func": send_summary, "schema": summary_tool_schema},
}