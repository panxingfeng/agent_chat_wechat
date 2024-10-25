from lark_oapi.api.im.v1 import *
import lark_oapi as lark

from config.config import FEISHU_DATA


class SendMessage:
    def __init__(self, log_level=lark.LogLevel.INFO):
        self.app_id = FEISHU_DATA.get('app_id')
        self.app_secret = FEISHU_DATA.get('app_secret')
        self.client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .log_level(log_level) \
            .build()

    def send_message(self, message_params) -> dict:
        """
        发送消息给指定用户
        :param client: 飞书客户端
        :param receive_id: 接收消息的用户 open_id
        :param msg_type: 消息类型, 比如 "text"
        :param content: 消息内容 (JSON 格式字符串)
        :param receive_id_type: ID 类型, 默认为 "open_id"
        :return: 发送结果（字典形式）
        """
        # 构造请求对象
        receive_id_type = message_params.get('receive_id_type')
        receive_id = message_params.get('receive_id')
        msg_type = message_params.get('msg_type')
        content = message_params.get('content')
        request = CreateMessageRequest.builder() \
            .receive_id_type(receive_id_type) \
            .request_body(CreateMessageRequestBody.builder()
                          .receive_id(receive_id)
                          .msg_type(msg_type)
                          .content(content)
                          .build()) \
            .build()

        # 发起请求
        response = self.client.im.v1.message.create(request)

        # 处理失败返回
        if not response.success():
            error_message = f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
            lark.logger.error(error_message)
            return {"success": False, "error": error_message}

        # 处理业务结果
        result = lark.JSON.marshal(response.data, indent=4)
        lark.logger.info(result)
        return {"success": True, "data": result}
