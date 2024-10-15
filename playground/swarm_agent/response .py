def check_order_status(order_id, customer_id):
    return f"用户<{customer_id}>订单<{order_id}>状态：已发货，预计明天送达。"


def validate_return_request():
    return "符合退换货政策，可以继续处理。"


def initiate_refund():
    return "退款已启动，预计 3-5 个工作日内到账。"


def change_order_item():
    return "订单商品已成功更换。"


def case_resolved():
    return "问题已解决。无更多问题。"


def escalate_to_agent(reason=None):
    return f"升级至客服代理: {reason}" if reason else "升级至客服代理"
