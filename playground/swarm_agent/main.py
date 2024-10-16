import json
from swarm import Swarm

from config.config import OLLAMA_DATA
from playground.swarm_agent.agent import triage_agent
from playground.swarm_agent.data import context_variables
from server.client.loadmodel.Ollama.OllamaClient import OllamaClient

# 美化打印消息内容
def pretty_print_messages(messages) -> None:
    for message in messages:
        if message["role"] != "assistant":  # 只打印助手的回复
            continue

        # 蓝色显示智能体名称
        print(f"\033[94m{message['sender']}\033[0m:", end=" ")

        # 打印智能体的回复内容
        if message["content"]:
            print(message["content"])

        # 如果有工具调用，则打印工具调用的信息
        tool_calls = message.get("tool_calls") or []
        if len(tool_calls) > 0:
            print("\n调用的工具信息：")  # 提示工具调用信息
        for tool_call in tool_calls:
            f = tool_call["function"]
            name, args = f["name"], f["arguments"]

            # 尝试将工具调用的参数格式化为 key=value 形式
            try:
                arg_str = json.dumps(json.loads(args), ensure_ascii=False, indent=2).replace(":", "=")
            except json.JSONDecodeError:
                arg_str = args  # 如果解析失败，原样显示

            # 紫色显示工具调用的函数名和参数
            print(f"  \033[95m{name}\033[0m({arg_str[1:-1]})")

# 处理并打印流式响应的内容
def process_and_print_streaming_response(response):
    content = ""
    last_sender = ""

    # 遍历响应的每个片段
    for chunk in response:
        if "sender" in chunk:
            last_sender = chunk["sender"]  # 保存消息的发送者

        if "content" in chunk and chunk["content"] is not None:
            if not content and last_sender:
                # 蓝色显示发送者名称，并实时打印消息内容
                print(f"\033[94m{last_sender}：\033[0m", end=" ", flush=True)
                last_sender = ""
            print(chunk["content"], end="", flush=True)
            content += chunk["content"]

        if "tool_calls" in chunk and chunk["tool_calls"] is not None:
            print("\n工具调用信息：")  # 提示工具调用信息
            for tool_call in chunk["tool_calls"]:
                f = tool_call["function"]
                name = f["name"]
                if not name:
                    continue
                # 紫色显示工具调用的函数名
                print(f"  \033[95m{name}\033[0m()", flush=True)

        if "delim" in chunk and chunk["delim"] == "end" and content:
            print()  # 换行表示消息结束
            content = ""

        if "response" in chunk:
            # 返回最终完整的响应
            return chunk["response"]

# 主循环函数，实现与智能体的交互
def run_demo_loop(
        openai_client,
        starting_agent,
        context_variables=None,
        stream=False,
        debug=False) -> None:
    client = Swarm(openai_client)  # 初始化 Swarm 客户端
    print("启动 Swarm agent")
    print('输入 "退出" 或 "离开" 以结束对话。')

    messages = []  # 存储用户与智能体的对话消息
    agent = starting_agent  # 设置当前使用的智能体

    # 用户可以不断与智能体交互的循环
    while True:
        user_input = input("用户: ").strip()  # 获取用户输入并去除多余空格

        # 检查是否输入了退出关键词
        if user_input.lower() in {"退出", "离开", "exit", "quit"}:
            print("结束聊天，再见！")
            break  # 结束循环

        # 将用户输入添加到消息列表
        messages.append({"role": "user", "content": user_input})

        # 使用 Swarm 客户端与智能体进行交互
        response = client.run(
            agent=agent,
            messages=messages,
            context_variables=context_variables or {},
            stream=stream,
            debug=debug,
        )

        if stream:
            # 如果启用了流式处理，调用流处理函数
            response = process_and_print_streaming_response(response)
        else:
            # 否则直接打印消息
            pretty_print_messages(response.messages)

        # 更新消息和当前智能体
        messages.extend(response.messages)
        agent = response.agent

# 初始化 Ollama 客户端
client = OllamaClient(model=OLLAMA_DATA.get("model"), url=OLLAMA_DATA.get("api_url"))
client_openai = client.get_client()

# 启动主循环，使用分诊智能体作为起始智能体
run_demo_loop(
    openai_client=client_openai,
    starting_agent=triage_agent,
    context_variables=context_variables,
    debug=True
)
