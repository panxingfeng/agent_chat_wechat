from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

""" 模型介绍
MiniCPM 3.0 是一个 4B 参数量的语言模型，相比 MiniCPM1.0/2.0，功能更加全面，综合能力大幅提升，多数评测集上的效果比肩甚至超越众多 7B-9B 模型。

支持工具调用🛠️（Function Calling）和代码解释器💻（Code Interpreter）：Berkeley Function Calling Leaderboard (BFCL) 上取得 9B 规模以下 SOTA，超越 GLM-4-9B-Chat、Qwen2-7B-Instruct。
超强的推理能力🧮：数学能力方面，MathBench 上的效果超越 GPT-3.5-Turbo 以及多个 7B-9B 模型。在非常具有挑战性的 LiveCodeBench 上，效果超越 Llama3.1-8B-Instruct。
出色的中英文指令遵循能力🤖：英文指令遵循 IFEval、中文指令遵循 FollowBench-zh 效果超越 GLM-4-9B-Chat、Qwen2-7B-Instruct。
长文本能力：原生支持 32k 上下文长度，32k 长度内大海捞针全绿。提出 LLMxMapReduce ，理论可处理的上下文长度达到 +∞，在综合性长文本评测基准 InfiniteBench 平均得分超越GPT-4、KimiChat等标杆模型。
RAG能力：我们发布了 MiniCPM RAG 套件。基于 MiniCPM 系列模型的 MiniCPM-Embedding、MiniCPM-Reranker 在中文、中英跨语言检索测试中取得 SOTA 表现；针对 RAG 场景的 MiniCPM3-RAG-LoRA 在开放域问答等多项任务上超越 Llama3-8B、Baichuan2-13B 等模型。
"""


class ResponseWrapper:
    """包装API返回的响应内容，支持 .content 访问。"""

    def __init__(self, content):
        self.content = content


class MiniCPMClient:
    """GPU:流畅运行要求8G+  8G推理比较久,大概40-60来秒,具体看型号"""
    def __init__(self,
                 model_path="OpenBMB/MiniCPM3-4B",
                 device="cuda",
                 cache_dir="../model"):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True,
            cache_dir=cache_dir,
            local_files_only=True
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map=self.device,
            trust_remote_code=True,
            cache_dir=cache_dir,
            local_files_only=True
        )

    def invoke(self, messages, max_tokens=1024, top_p=0.7, temperature=0.7):
        model_inputs = self.tokenizer.apply_chat_template(
            messages,
            return_tensors="pt",
            add_generation_prompt=True
        ).to(self.device)

        model_outputs = self.model.generate(
            model_inputs,
            max_new_tokens=max_tokens,
            top_p=top_p,
            temperature=temperature
        )

        output_token_ids = [
            model_outputs[i][len(model_inputs[i]):] for i in range(len(model_inputs))
        ]

        content = self.tokenizer.batch_decode(
            output_token_ids, skip_special_tokens=True
        )[0]

        return ResponseWrapper(content)


# 测试示例
if __name__ == "__main__":
    client = MiniCPMClient()
    prompt = "你是一个乐于助人的助手"
    message = "推荐5个北京的景点"
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": message}
    ]

    response = client.invoke(messages)

    print(response.content)
