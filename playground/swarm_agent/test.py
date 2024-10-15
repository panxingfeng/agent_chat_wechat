from swarm import Swarm, Agent
from openai import OpenAI

from config.config import CHATGPT_DATA

client_openai = OpenAI(
    api_key=CHATGPT_DATA.get("key"),
    base_url=CHATGPT_DATA.get("url"),
)

#使用本地部署的ollama
# client = OllamaClient(model=OLLAMA_DATA.get("model"), url=OLLAMA_DATA.get("url"))
# client_openai = client.get_client()

client = Swarm(client=client_openai)


def get_weather(location):
    location = location
    return f"{location}天气晴，26度"

agent_a = Agent(
    name="Agent A",
    instructions="You are a helpful agent.",
    functions=[get_weather],
    model=CHATGPT_DATA.get("model")
    # model=OLLAMA_DATA.get("model") #使用ollama
)

agent_b = Agent(
    name="Agent B",
    instructions="Only speak in Haikus.",
    model=CHATGPT_DATA.get("model")
    # model=OLLAMA_DATA.get("model") #使用ollama
)

response = client.run(
    agent=agent_a,
    messages=[{"role": "user", "content": "北京的天气"}],
)

print(response.messages[-1]["content"])  # 输出内容：北京天气晴，气温26度
