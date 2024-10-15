import re

from config.templates.data.bot import CHATBOT_PROMPT_DATA, BOT_DATA


class PromptGenerator:
    def __init__(self, template):
        """
        初始化模板生成器，并存储模板内容。
        """
        self.template = template
        self.placeholders = self._extract_placeholders(template)

    def _extract_placeholders(self, template):
        """
        提取模板中的占位符。
        """
        return re.findall(r"{(.*?)}", template)

    def generate(self, **kwargs):
        """
        根据传入的参数动态填充模板。
        如果某个占位符缺失，则用 <key缺失> 填充。
        """
        # 构造要填充的数据字典
        data = {key: kwargs.get(key, f"<{key}缺失>") for key in self.placeholders}

        # 使用模板填充数据
        return self.template.format(**data)


if __name__ == "__main__":
    prompt_generator = PromptGenerator(CHATBOT_PROMPT_DATA["description"])

    filled_prompt = prompt_generator.generate(
        name=BOT_DATA["chat"].get("name"),
        capabilities=BOT_DATA["chat"].get("capabilities"),
        welcome_message=BOT_DATA["chat"]["default_responses"].get("welcome_message"),
        unknown_command=BOT_DATA["chat"]["default_responses"].get("unknown_command"),
        language_support=BOT_DATA["chat"].get("language_support"),
    )

    print(filled_prompt)
