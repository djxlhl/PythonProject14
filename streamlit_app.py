import streamlit as st
import re
from dotenv import load_dotenv
from tavily import TavilyClient
from openai import OpenAI
import os

# 加载环境变量
load_dotenv()

# 初始化 DeepSeek
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)
model_name = os.getenv("DEEPSEEK_MODEL")

# 初始化 Tavily 搜索
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search_company_revenue(company_name, year):
    """搜索指定公司指定年份的营业额"""
    try:
        query = f"{company_name} {year}年 营业额"
        response = tavily.search(query=query, search_depth="basic")
        if response["results"]:
            return response["results"][0]["content"]
        return None
    except Exception as e:
        return None


def extract_revenue_number(text):
    """从文本中提取营业额数字（支持语义相似的多种关键词）"""
    if not text:
        return None, None, "未找到相关材料"
    
    # 语义相似的关键词组合：
    # 时间词：全年、年度、年
    # 核心词：总收入、总营收、营业额、营收、收入
    # 组合示例：全年总收入、年营业额、年度营收、全年收入等
    time_words = r'(?:全年|年度|年)'
    revenue_words = r'(?:总收入|总营收|营业额|营收|收入)'
    
    patterns = [
        # 匹配：时间词+核心词 + 数字 + 单位
        # 例如：全年总收入100万、年营业额50亿、年度营收200万
        rf'{time_words}{revenue_words}[：:\s]*(\d+(?:\.\d+)?)\s*([万亿]?)',
        
        # 匹配：数字 + 单位 + 时间词+核心词
        # 例如：100万全年总收入、50亿年营业额
        rf'(\d+(?:\.\d+)?)\s*([万亿]?)\s*{time_words}{revenue_words}',
        
        # 匹配：时间词+核心词 ... 数字 + 单位（中间可能有其他文字）
        # 例如：全年总收入达到了100万、年营业额为50亿元
        rf'{time_words}{revenue_words}.*?(\d+(?:\.\d+)?)\s*([万亿]?)',
        
        # 匹配：数字 + 单位 ... 时间词+核心词
        # 例如：100万元的全年总收入、50亿的年营业额
        rf'(\d+(?:\.\d+)?)\s*([万亿]?).*?{time_words}{revenue_words}',
        
        # 额外支持：核心词单独出现（不带时间词）
        # 例如：总收入100万、营业额50亿
        rf'{revenue_words}[：:\s]*(\d+(?:\.\d+)?)\s*([万亿]?)',
        rf'(\d+(?:\.\d+)?)\s*([万亿]?)\s*{revenue_words}',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            try:
                num_str, unit = matches[0]
                num = float(num_str)
                
                # 根据单位转换
                if unit == '亿':
                    num = num * 10000  # 转换为万
                elif unit == '万' or unit == '':
                    pass  # 保持原值（单位：万）
                
                # 返回整数或浮点数
                result = int(num) if num == int(num) else num
                
                # 提取匹配的关键词类型
                matched_text = re.search(pattern, text)
                if matched_text:
                    keyword_match = re.search(r'(全年|年度|年)?(总收入|总营收|营业额|营收|收入)', matched_text.group())
                    if keyword_match:
                        time_part = keyword_match.group(1) or ""
                        core_part = keyword_match.group(2)
                        keyword_type = time_part + core_part
                    else:
                        keyword_type = "数据"
                else:
                    keyword_type = "数据"
                
                return result, keyword_type, f"成功提取：{result}万"
            except Exception as e:
                continue
    
    return None, None, "未找到相关材料（未检测到包含'总收入'、'总营收'、'营业额'、'营收'、'收入'等关键词的有效数据）"


def calculate_growth_rate(revenue_2024, revenue_2025):
    """计算增长率"""
    if revenue_2024 and revenue_2025 and revenue_2024 > 0:
        rate = (revenue_2025 - revenue_2024) / revenue_2024
        return rate
    return None


def generate_summary(company_name, revenue_2024, revenue_2025, growth_rate, data_type="营业额"):
    """使用 AI 生成趋势总结"""
    prompt = f"""
    请分析以下公司的{data_type}趋势：
    公司名称：{company_name}
    2024年{data_type}：{revenue_2024}万
    2025年{data_type}：{revenue_2025}万
    {data_type}增长率：{growth_rate:.1%}
    
    请用简洁的中文总结该公司的{data_type}变化趋势，并给出简要分析。
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"{data_type}增长率：{growth_rate:.1%}。{'增长' if growth_rate > 0 else '下降'}趋势明显。"


# ==================== Streamlit 页面配置 ====================
st.set_page_config(
    page_title="公司营业额查询系统",
    page_icon="📊",
    layout="wide"
)

# 页面标题
st.title("📊 公司营业额查询与分析系统")
st.markdown("---")

# 侧边栏 - 使用说明
with st.sidebar:
    st.header("使用说明")
    st.info("""
    1. 输入要查询的公司名称
    2. 点击"开始查询"按钮
    3. 系统将自动搜索该公司2024年和2025年的营业额
    4. 自动计算增长率并生成趋势分析
    """)
    
    st.header("示例公司")
    st.caption("阿里巴巴、腾讯、百度、京东等")

# 主界面 - 输入区域
col1, col2 = st.columns([3, 1])

with col1:
    company_name = st.text_input(
        "🏢 请输入公司名称",
        placeholder="例如：阿里巴巴",
        help="输入您想要查询营业额的公司名称"
    )

with col2:
    st.write("")  # 占位
    st.write("")  # 占位
    query_button = st.button("🔍 开始查询", type="primary", use_container_width=True)

# 查询逻辑
if query_button:
    if not company_name:
        st.warning("⚠️ 请输入公司名称！")
    else:
        with st.spinner(f"正在查询 {company_name} 的营业额数据..."):
            # 步骤1：搜索2024年营业额
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("📡 正在搜索2024年营业额...")
            data_2024 = search_company_revenue(company_name, "2024")
            progress_bar.progress(25)
            
            # 步骤2：搜索2025年营业额
            status_text.text("📡 正在搜索2025年营业额...")
            data_2025 = search_company_revenue(company_name, "2025")
            progress_bar.progress(50)
            
            # 步骤3：提取数字
            status_text.text("🔢 正在提取数据...")
            revenue_2024, keyword_type_2024, msg_2024 = extract_revenue_number(data_2024)
            revenue_2025, keyword_type_2025, msg_2025 = extract_revenue_number(data_2025)
            progress_bar.progress(75)
            
            # 确定统一的数据类型标签（以第一个成功提取的为准）
            data_type_label = "营业额"
            if revenue_2024 is not None and keyword_type_2024:
                data_type_label = keyword_type_2024
            elif revenue_2025 is not None and keyword_type_2025:
                data_type_label = keyword_type_2025
            
            # 步骤4：计算增长率
            status_text.text("📈 正在计算增长率...")
            growth_rate = calculate_growth_rate(revenue_2024, revenue_2025)
            progress_bar.progress(90)
            
            # 步骤5：生成总结
            status_text.text("🤖 正在生成分析报告...")
            if revenue_2024 is not None and revenue_2025 is not None and growth_rate is not None:
                summary = generate_summary(company_name, revenue_2024, revenue_2025, growth_rate, data_type_label)
            else:
                # 构建详细的错误信息
                error_msgs = []
                if revenue_2024 is None:
                    error_msgs.append(f"2024年：{msg_2024}")
                if revenue_2025 is None:
                    error_msgs.append(f"2025年：{msg_2025}")
                summary = "❌ 数据提取失败\n\n" + "\n".join(error_msgs) + "\n\n请检查公司名称是否正确，或尝试其他公司。"
            progress_bar.progress(100)
            
            status_text.text("✅ 查询完成！")
        
        # 显示结果
        st.markdown("---")
        st.subheader(f"📋 {company_name} {data_type_label}分析报告")
        
        # 使用三列展示关键数据
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label=f"2024年{data_type_label}",
                value=f"{revenue_2024}万" if revenue_2024 else "未找到",
                delta=None
            )
        
        with col2:
            st.metric(
                label=f"2025年{data_type_label}",
                value=f"{revenue_2025}万" if revenue_2025 else "未找到",
                delta=None
            )
        
        with col3:
            if growth_rate is not None:
                st.metric(
                    label=f"{data_type_label}增长率",
                    value=f"{growth_rate:.1%}",
                    delta=f"{growth_rate:.1%}",
                    delta_color="normal" if growth_rate >= 0 else "inverse"
                )
            else:
                st.metric(label=f"{data_type_label}增长率", value="N/A")
        
        # 显示原始数据
        with st.expander("📄 查看原始搜索数据", expanded=False):
            st.write("**2024年数据源：**")
            if data_2024:
                st.info(data_2024)
                st.caption(f"提取结果：{msg_2024}")
            else:
                st.warning("未搜索到相关数据")
            
            st.write("**2025年数据源：**")
            if data_2025:
                st.info(data_2025)
                st.caption(f"提取结果：{msg_2025}")
            else:
                st.warning("未搜索到相关数据")
        
        # 显示AI分析总结
        st.markdown("### 🎯 趋势分析")
        st.success(summary)

# 页面底部说明
st.markdown("---")
st.caption("💡 提示：数据来源为网络搜索，仅供参考。如需精确数据，请参考公司官方财报。")
