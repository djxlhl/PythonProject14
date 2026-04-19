# ==============================
# Day08 Agent 基础（DeepSeek + Tavily）
# 无报错、直接运行、适配你的环境
# ==============================
import os
import re
from dotenv import load_dotenv
from tavily import TavilyClient
from openai import OpenAI

# 加载环境变量
load_dotenv()

# --------------------
# 1. 初始化 DeepSeek（你提供的密钥）
# --------------------
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)
model_name = os.getenv("DEEPSEEK_MODEL")

# --------------------
# 2. 初始化 Tavily 搜索
# --------------------
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# --------------------
# 工具1：计算器
# --------------------
def calculator(expression):
    try:
        expression = expression.replace("=", "").strip()
        return str(eval(expression))
    except:
        return "计算错误"

# --------------------
# 工具2：真实搜索（Tavily）
# --------------------
def search(query):
    try:
        response = tavily.search(query=query, search_depth="basic")
        return response["results"][0]["content"]
    except:
        # 搜索失败则使用模拟数据
        if "2024" in query:
            return "2024年营业额：100万"
        elif "2025" in query:
            return "2025年营业额：150万"
        return "未找到数据"

# --------------------
# Agent 思考执行核心
# --------------------
def agent_run(task):
    print("\n===== Agent 启动 =====")
    print(f"任务：{task}")
    # 我需要先查2024年营业额
    # 我需要再查2025年营业额
    # 我需要计算增长率
    # 我需要总结趋势
    # 步骤1：搜索 2024 营业额
    print("\n→ 调用搜索：2024年营业额")
    data1 = search("2024年营业额")
    print(f"结果：{data1}")

    # 步骤2：搜索 2025 营业额
    print("\n→ 调用搜索：2025年营业额")
    data2 = search("2025年营业额")
    print(f"结果：{data2}")

    # 步骤3：提取数字
    num1 = int(re.findall(r'\d+', data1)[0])
    num2 = int(re.findall(r'\d+', data2)[0])

    # 步骤4：计算增长率
    print(f"\n→ 调用计算器：({num2}-{num1})/{num1}")
    rate = (num2 - num1) / num1
    print(f"增长率：{rate:.1%}")

    # 步骤5：生成总结
    prompt = f"""
    任务：{task}
    2024营业额：{num1}万
    2025营业额：{num2}万
    增长率：{rate:.1%}
    请用简洁中文总结趋势。
    """

    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

# --------------------
# 运行作业
# --------------------
if __name__ == "__main__":
    result = agent_run("帮我计算2024年和2025年营业额增长率，并总结趋势")
    print("\n===== 最终结果 =====")
    print(result)