# day09_workflow.py
import json
from typing import Dict, Any, List
from day09_tools import ALL_TOOLS


def run_workflow(user_query: str) -> Dict[str, Any]:
    """
    多步骤流程：
    1. 根据用户查询，先去知识库检索相关信息
    2. 如果问题涉及天气，补充调用天气工具
    3. 汇总所有信息，生成最终回答
    """
    print(f"用户提问: {user_query}\n")

    # 步骤1：调用知识库
    kb_result = ALL_TOOLS["query_knowledge_base"]["func"](
        query=user_query, top_k=2
    )
    print(f"[知识库结果] {kb_result}")

    # 步骤2：判断是否需要天气（简单规则：如果问题包含“天气”或“温度”）
    weather_info = None
    if "天气" in user_query or "温度" in user_query:
        # 尝试提取城市（模拟：默认北京，也可以更智能提取）
        city = "北京"
        if "上海" in user_query:
            city = "上海"
        elif "深圳" in user_query:
            city = "深圳"
        weather_info = ALL_TOOLS["get_weather"]["func"](city=city, date="today")
        print(f"[天气补充] {weather_info}")

    # 步骤3：汇总结果
    summary = f"根据您的问题「{user_query}」，我们检索到以下信息：\n"
    for idx, item in enumerate(kb_result, 1):
        summary += f"{idx}. {item['content']}\n"
    if weather_info:
        summary += f"\n天气信息：{weather_info['city']} {weather_info['date']} {weather_info['weather']}\n"
    else:
        summary += "\n（未请求天气信息）\n"

    # 可选：发送摘要（模拟）
    send_status = ALL_TOOLS["send_summary"]["func"](
        recipient="admin@example.com",
        subject=f"用户问答摘要 - {user_query[:20]}",
        content=summary
    )

    return {
        "final_answer": summary,
        "kb_used": kb_result,
        "weather_used": weather_info,
        "send_status": send_status
    }


if __name__ == "__main__":
    # 测试两个场景
    test_queries = [
        "人工智能在会议中的应用",
        "上海明天的天气如何？"
    ]
    for q in test_queries:
        result = run_workflow(q)
        print("\n=== 最终回答 ===\n", result["final_answer"])
        print("-" * 50)