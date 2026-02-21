import os
from openai import OpenAI
import json

# DeepSeek is compatible with the OpenAI SDK
# Ensure DEEPSEEK_API_KEY is in your .env
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
    base_url="https://api.deepseek.com"
)

def extract_quotes(book_title: str, context: str) -> list[str]:
    """
    Uses DeepSeek to extract 10 quotes based on the search context.
    Returns a list of strings.
    """
    
    prompt = f"""
    我需要你根据以下关于《{book_title}》的搜索内容，提取并生成以下信息。
    必须严格按照JSON格式返回，包含一个字段：
    1. "quotes": 一个数组，包含10句书中的核心金句（必须深刻且有哲理，适合发朋友圈）。如果没有找到原著里足够的金句，请根据书本内容和作者观点，总结生成10个最符合原意的高质量金句。

    搜索内容：
    {context}
    
    请只返回JSON数据，不要包含Markdown格式（如```json），也不要有任何多余的解释。
    示例结构：
    {{
        "quotes": ["金句1", "金句2", "金句3", "金句4", "金句5", "金句6", "金句7", "金句8", "金句9", "金句10"]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的图书拆解专家和文案大师。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Strip potential markdown formatting if the model still outputs it
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
            
        result = json.loads(content.strip())
        return result.get("quotes", [])
        
    except Exception as e:
        print(f"Error during LLM extraction: {e}")
        # Fallback response
        return [f"关于《{book_title}》的精彩分享（默认金句 {i+1}）" for i in range(10)]

def generate_core_thought(book_title: str, context: str) -> str:
    """
    Generate a visualizable core thought based on the book's overall meaning.
    """
    prompt = f"""
    书籍《{book_title}》的背景与核心观点如下：
    {context}

    请写一段约50字的短文，总结这本书最核心的价值观与思想境界，用于大模型生成背景纯净唯美、留白足够的插画配图。必须具象化，可以描述一种意境，不要有文字元素，适合做文字海报的背景。
    直接返回这段文字，不需要任何解释。
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的AI生图提示词设计师。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating core thought: {e}")
        return "一本书静静地躺在阳光明媚的书桌上，散发着知识的光芒。"

def generate_mindmap_markdown(book_title: str, context: str) -> str:
    """
    Generate a structured Markdown mind map representation of the book.
    """
    prompt = f"""
    请根据以下关于《{book_title}》的内容，生成一个内容详实、结构严谨的 Markdown 思维导图。
    要求：
    1. 必须使用 Markdown 的多级列表语法（如 -, *, # 等）来表示层级关系。
    2. 第一层级（根节点）必须是书名《{book_title}》。
    3. 后续层级应包括：作者背景、核心思想、主要内容/结构拆解、经典金句、实际应用或启示等维度。
    4. 深入展开细节，保持文字精炼且专业，适合“高端大气”的呈现样式。
    5. 不要输出任何代码块标记（如 ```markdown），只输出纯净的文本格式。

    搜索内容参考：
    {context}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个资深的图书讲解人和逻辑架构师。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=2000
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```markdown"):
            content = content[11:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()
    except Exception as e:
        print(f"Error generating mindmap: {e}")
        return f"# 《{book_title}》\n- 生成思维导图失败\n  - 错误信息: {e}"
