import os  # 添加这一行以导入 os 模块

from pathlib import Path
from openai import OpenAI

# 获取系统变量
api_key = os.environ.get("MOONSHOT_API_KEY")  # 从环境变量中获取 API 密钥

client = OpenAI(
    api_key=api_key,  # 使用获取的 API 密钥
    base_url="https://api.moonshot.cn/v1",
)

pdf_path = "/Users/coolsnow/code/fun_bot/研报/2024Z世代AIGC态度报告：AI如何影响每个“我”.pdf" 
# xlnet.pdf 是一个示例文件, 我们支持 pdf, doc 以及图片等格式, 对于图片和 pdf 文件，提供 ocr 相关能力
file_object = client.files.create(file=Path(pdf_path), purpose="file-extract")

# 获取结果
# file_content = client.files.retrieve_content(file_id=file_object.id)
# 注意，之前 retrieve_content api 在最新版本标记了 warning, 可以用下面这行代替
# 如果是旧版本，可以用 retrieve_content
file_content = client.files.content(file_id=file_object.id).text

# 把它放进请求中
messages = [
    {
        "role": "system",
        "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
    },
    {
        "role": "system",
        "content": file_content,
    },
    # {"role": "user", "content": "请简单介绍此pdf 讲了啥"},
]

while True:  # 添加循环以实现可循环问答
    user_input = input("\n请输入你的问题（输入 '退出' 结束）：")  # 获取用户输入
    if user_input.lower() == '退出':  # 检查是否输入 '退出'
        break  # 退出循环

    messages.append({"role": "user", "content": user_input})  # 将用户输入添加到消息中

    # 然后调用 chat-completion, 获取 Kimi 的回答
    completion = client.chat.completions.create(
        model="moonshot-v1-32k",
        messages=messages,
        temperature=0.3,
        stream=True,  # 添加此行以启用流式输入
    )

    # 处理流式输出
    for chunk in completion:
        # 在这里，每个 chunk 的结构都与之前的 completion 相似，但 message 字段被替换成了 delta 字段
        delta = chunk.choices[0].delta # <-- message 字段被替换成了 delta 字段
 
        if delta.content:
            # 我们在打印内容时，由于是流式输出，为了保证句子的连贯性，我们不人为地添加
            # 换行符，因此通过设置 end="" 来取消 print 自带的换行符。
            print(delta.content, end="")