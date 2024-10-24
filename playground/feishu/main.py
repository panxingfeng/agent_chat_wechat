from flask import Flask, request, jsonify
import json

from playground.feishu.aes_cipher_client import AESCipher
from playground.feishu.feishu_message_handler import FeishuMessageHandler
from playground.feishu.user import FeishuUser
from server.client.loadmodel.Ollama.OllamaClient import OllamaClient

# 实例化 Flask 应用
app = Flask(__name__)

# 实例化消息处理类和用户类
feishu_user = FeishuUser()
feishu_handler = FeishuMessageHandler(feishu_user)
client = OllamaClient()

# 接收 POST 请求，并返回其中的 challenge 字段或处理事件
@app.route("/", methods=["POST"])
def event():
    try:
        data = request.json
        decrypted_data = {}

        # 检查是否有加密的消息内容
        if "encrypt" in data:
            try:
                cipher = AESCipher()
                decrypted_message = cipher.decrypt_string(data["encrypt"])
                decrypted_data = json.loads(decrypted_message)
                print(decrypted_data)
            except Exception as e:
                print(e)

        # 获取事件类型
        event_type = decrypted_data.get('header', {}).get('event_type')
        # 获取消息的内容
        event_data = decrypted_data.get('event', {})

        # 处理 URL 验证请求
        if 'challenge' in decrypted_data:
            return jsonify({"challenge": decrypted_data['challenge']})

        # 处理消息接收事件
        feishu_handler.handle_message(event_data, event_type)

    except ValueError as ve:
        print(str(ve))
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"处理失败: {str(e)}")
        return jsonify({"error": "处理失败", "details": str(e)}), 500

    return jsonify({"message": "事件未被处理"})

if __name__ == "__main__":
    app.run(port=8070)
