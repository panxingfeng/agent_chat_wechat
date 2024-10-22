from server.rag.v1.VectorStore.vectorstore import VectorStore
from server.rag.v1.chatmodel.ollama_model import OllamaModel
from server.rag.v1.embedding.embedding_model import EmbeddingModel
from server.rag.v1.tool.load_file import ReadFiles


def run_rag(question: str, knowledge_base_path: str, k: int = 1) -> str:
    """
    :param question: 用户提出的问题
    :param knowledge_base_path: 知识库的路径，包含文档的文件夹路径
    :param k: 返回与问题最相关的k个文档片段，默认为1
    :return: 返回ollama模型生成的回答
    """
    # 加载并切分文档
    docs = ReadFiles(knowledge_base_path).get_content(max_token_len=600, cover_content=150)
    vector = VectorStore(docs)

    # 创建向量模型客户端
    embedding = EmbeddingModel()
    vector.get_vector(EmbeddingModel=embedding)

    # 将向量和文档保存到本地
    vector.persist(path='file/storage')

    # 打印数据信息
    vector.print_info()

    # 在数据库中检索最相关的文档片段
    content = vector.query(question, EmbeddingModel=embedding, k=k)[0]

    # 使用大模型进行回复
    chat = OllamaModel()
    answer = chat.chat(question, [], content)

    return answer


result = run_rag('AgentChatBot是一个什么类型的项目', knowledge_base_path='file')

print("回答内容:" + result)
