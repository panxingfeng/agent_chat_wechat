import json
import lark_oapi as lark
from lark_oapi.api.contact.v3 import *

from config.config import FEISHU_DATA


class FeishuUser:
    def __init__(self):
        """
        初始化 FeishuUser 类，设置 App ID 和 App Secret。
        """
        self.app_id = FEISHU_DATA.get('app_id')
        self.app_secret = FEISHU_DATA.get('app_secret')
        self.client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .log_level(lark.LogLevel.DEBUG) \
            .build()
        self.token = FEISHU_DATA.get('tenant_access_token')

    def get_user_info_by_id(self, user_id: str, user_id_type: str = "open_id"):
        """
        通过用户 ID 获取用户信息
        :param user_id: 用户的 ID（open_id 或 user_id）
        :param user_id_type: ID 类型，默认为 "open_id"
        :param token: 用户访问 token，默认为 None
        :return: 用户信息字典
        """
        # 构造请求对象
        request = GetUserRequest.builder() \
            .user_id(user_id) \
            .user_id_type(user_id_type) \
            .department_id_type("open_department_id") \
            .build()

        # 构造请求选项
        option = lark.RequestOption.builder().user_access_token(self.token).build()

        # 发起请求
        response = self.client.contact.v3.user.get(request, option)

        # 处理失败返回
        if not response.success():
            error_message = (
                f"获取用户信息失败, 错误代码: {response.code}, "
                f"错误消息: {response.msg}, log_id: {response.get_log_id()}"
            )
            lark.logger.error(error_message)
            return {"success": False, "error": error_message}

        # 将用户信息转换为字典格式
        user_info = json.loads(lark.JSON.marshal(response.data))
        return {"success": True, "data": user_info}

    def format_user_info(self, user_info):
        """
        格式化用户主要信息
        :param user_info: 用户信息字典
        :return: name、gender、mobile、department_ids、job_title、is_tenant_manager
        """
        user = user_info['user']

        return {
            "name": user.get('name', 'N/A'),
            "gender": 'man' if user.get('gender') == 1 else 'women' if user.get('gender') == 0 else '未知',
            "mobile": user.get('mobile', 'N/A'),
            "department_ids": ', '.join(user.get('department_ids', [])),
            "job_title": user.get('job_title', 'N/A'),
            "is_tenant_manager": True if user.get('is_tenant_manager') else False,
            }
