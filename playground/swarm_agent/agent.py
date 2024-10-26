from swarm import Agent  # 导入 Agent 类

from config.config import OLLAMA_DATA  # 导入配置信息
from playground.swarm_agent.common import triage_instructions  # 导入分诊智能体的指令
from playground.swarm_agent.response import (
    check_order_status,  # 检查订单状态
    escalate_to_agent,  # 升级至人工客服
    case_resolved,  # 标记案件为已解决
    validate_return_request,  # 验证退货请求
    initiate_refund,  # 启动退款流程
    change_order_item  # 更改订单项目
)
from playground.swarm_agent.prompt import (
    ORDER_QUERY_POLICY,  # 订单查询策略
    STARTER_PROMPT,  # 初始提示信息
    RETURN_EXCHANGE_POLICY,  # 退换货政策
    OUT_OF_STOCK_POLICY  # 缺货处理策略
)

# 转移到订单查询智能体
def transfer_to_order_query():
    return order_query

# 转移到退换货智能体
def transfer_to_return_exchange():
    return return_exchange

# 转移到缺货处理智能体
def transfer_to_out_of_stock():
    return out_of_stock

# 转移到分诊智能体
def transfer_to_triage():
    return triage_agent

# 分诊智能体，负责初步分类用户请求
triage_agent = Agent(
    name="Triage Agent",  # 分诊智能体
    instructions=triage_instructions,  # 分诊指令
    functions=[transfer_to_order_query, transfer_to_return_exchange],  # 转移功能
    model=OLLAMA_DATA.get("model")  # 使用的模型
)

# 订单查询智能体，负责订单相关的查询
order_query = Agent(
    name="Order Query Agent",  # 订单查询智能体
    instructions=STARTER_PROMPT + ORDER_QUERY_POLICY,  # 初始提示 + 查询策略
    functions=[
        check_order_status,  # 检查订单状态
        escalate_to_agent,  # 升级至人工客服
        case_resolved,  # 案件解决
    ],
    model=OLLAMA_DATA.get("model")  # 使用的模型
)

# 退换货处理智能体，负责处理退换货相关请求
return_exchange = Agent(
    name="Return Exchange Agent",  # 退换货处理智能体
    instructions=STARTER_PROMPT + RETURN_EXCHANGE_POLICY,  # 初始提示 + 退换货策略
    functions=[
        validate_return_request,  # 验证退货请求
        initiate_refund,  # 启动退款流程
        change_order_item,  # 更改订单项目
        escalate_to_agent,  # 升级至人工客服
        case_resolved,  # 案件解决
    ],
    model=OLLAMA_DATA.get("model")  # 使用的模型
)

# 缺货处理智能体，负责处理缺货问题
out_of_stock = Agent(
    name="Out of Stock Agent",  # 缺货处理智能体
    instructions=STARTER_PROMPT + OUT_OF_STOCK_POLICY,  # 初始提示 + 缺货策略
    functions=[
        change_order_item,  # 更改订单项目
        escalate_to_agent,  # 升级至人工客服
        case_resolved,  # 案件解决
    ],
    model=OLLAMA_DATA.get("model")  # 使用的模型
)
