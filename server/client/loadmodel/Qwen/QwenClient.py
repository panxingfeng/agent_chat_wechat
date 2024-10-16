import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class ResponseWrapper:
    """包装API返回的响应内容，支持 .content 访问。"""
    def __init__(self, content):
        self.content = content

class QwenClient:
    """
    num=1:调用本地部署的Qwen2.5-1.5B大模型，模型的配置信息在config/config.py中
    示例模板: messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": message}
    ]
    GPU:运行要求4G+显存，速度看显卡的型号

    num=2:调用本地部署的Qwen2.5-0.5B大模型，模型的配置信息在config/config.py中
    示例模板: messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": message}
    ]
    GPU:运行要求2G+显存，速度看显卡的型号
    """
    def __init__(self, num, cache_dir="../../../model"):
        global model_path
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if num == 1:
            model_path = "QwenModel/Qwen2.5-0.5B-Instruct"
        elif num == 2:
            model_path = "QwenModel/Qwen2.5-1.5B-Instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True,
            cache_dir=cache_dir,
            local_files_only=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto",
            cache_dir=cache_dir,
            local_files_only=True
        )

    def invoke(self, prompt, message, max_tokens=512, temperature=0.7, top_p=0.9):
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": message}
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        generated_ids = self.model.generate(
            input_ids=model_inputs["input_ids"],
            attention_mask=model_inputs["attention_mask"],
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )

        response = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)

        # 只保留模型的回答内容
        cleaned_response = response.split("assistant")[-1].strip()

        return ResponseWrapper(cleaned_response)


# 测试示例
if __name__ == "__main__":
    client = QwenClient(num=1)
    message = "如何学习好python"
    prompt = "你是一个乐于助人的机器人"
    # 生成并打印模型的回复
    response = client.invoke(prompt=prompt,message=message)
    print(response.content)
