import os
from typing import List, Dict
import numpy as np
import uuid

class VectorStore:
    def __init__(self, document: List[str] = None) -> None:
        """
        初始化向量存储类，存储文档和对应的向量表示，并生成唯一的文档ID。
        :param document: 文档列表，默认为空。
        """
        if document is None:
            document = []
        self.document = document  # 存储文档内容
        self.vectors = []  # 存储文档的向量表示
        self.doc_ids = []  # 存储文档的唯一ID
        self.vector_ids = []  # 存储向量块的唯一ID

        # 为每个文档生成唯一ID
        self.doc_ids = [str(uuid.uuid4()) for _ in self.document]

    def get_vector(self, EmbeddingModel) -> List[Dict[str, List[float]]]:
        """
        使用传入的 Embedding 模型将文档向量化，并生成唯一的向量块ID。
        :param EmbeddingModel: 传入的用于生成向量的模型。
        :return: 返回文档对应的向量列表，每个向量都附带一个ID。
        """
        # 为每个文档生成向量并生成唯一向量块ID
        self.vectors = [EmbeddingModel.get_embedding(doc) for doc in self.document]
        self.vector_ids = [str(uuid.uuid4()) for _ in self.vectors]
        # 返回包含向量及其对应ID的字典
        return [{"vector_id": vec_id, "vector": vector} for vec_id, vector in zip(self.vector_ids, self.vectors)]

    def persist(self, path: str = 'storage'):
        """
        将文档、向量、文档ID和向量ID持久化到本地目录中，以便后续加载使用。
        :param path: 存储路径，默认为 'storage'。
        """
        if not os.path.exists(path):
            os.makedirs(path)  # 如果路径不存在，创建路径
        # 保存向量为 numpy 文件
        np.save(os.path.join(path, 'vectors.npy'), self.vectors)
        # 将文档内容和文档ID存储到文本文件中
        with open(os.path.join(path, 'documents.txt'), 'w', encoding='utf-8') as f:
            for doc, doc_id in zip(self.document, self.doc_ids):
                f.write(f"{doc_id}\t{doc}\n")
        # 将向量ID存储到文本文件中
        with open(os.path.join(path, 'vector_ids.txt'), 'w', encoding='utf-8') as f:
            for vector_id in self.vector_ids:
                f.write(f"{vector_id}\n")

    def load_vector(self, path: str = 'storage'):
        """
        从本地加载之前保存的文档、向量、文档ID和向量ID数据。
        :param path: 存储路径，默认为 'storage'。
        """
        # 加载保存的向量数据
        self.vectors = np.load(os.path.join(path, 'vectors.npy')).tolist()
        # 加载文档内容和文档ID
        with open(os.path.join(path, 'documents.txt'), 'r', encoding='utf-8') as f:
            self.document = []
            self.doc_ids = []
            for line in f.readlines():
                doc_id, doc = line.strip().split('\t', 1)
                self.doc_ids.append(doc_id)
                self.document.append(doc)
        # 加载向量ID
        with open(os.path.join(path, 'vector_ids.txt'), 'r', encoding='utf-8') as f:
            self.vector_ids = [line.strip() for line in f.readlines()]

    def get_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """
        计算两个向量的余弦相似度。
        :param vector1: 第一个向量。
        :param vector2: 第二个向量。
        :return: 返回两个向量的余弦相似度，范围从 -1 到 1。
        """
        dot_product = np.dot(vector1, vector2)
        magnitude = np.linalg.norm(vector1) * np.linalg.norm(vector2)
        if not magnitude:
            return 0
        return dot_product / magnitude

    def query(self, query: str, EmbeddingModel, k: int = 1) -> List[Dict[str, str]]:
        """
        根据用户的查询文本，检索最相关的文档片段。
        :param query: 用户的查询文本。
        :param EmbeddingModel: 用于将查询向量化的嵌入模型。
        :param k: 返回最相似的文档数量，默认为 1。
        :return: 返回包含文档ID和文档内容的最相似文档列表。
        """
        # 将查询文本向量化
        query_vector = EmbeddingModel.get_embedding(query)
        # 计算查询向量与每个文档向量的相似度
        similarities = [self.get_similarity(query_vector, vector) for vector in self.vectors]
        # 获取相似度最高的 k 个文档索引
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        # 返回对应的文档ID和内容
        result = [{"doc_id": self.doc_ids[idx], "document": self.document[idx]} for idx in top_k_indices]
        print(result)
        return result

    def print_info(self):
        """
        输出存储在 VectorStore 中的文档、向量、文档ID和向量ID的详细信息。
        """
        print("===== 存储的信息 =====")
        for i, (doc_id, doc, vector_id, vector) in enumerate(zip(self.doc_ids, self.document, self.vector_ids, self.vectors)):
            print(f"文档 {i+1}:")
            print(f"  文档ID: {doc_id}")
            print(f"  文档内容: {doc}")
            print(f"  向量ID: {vector_id}")
            print(f"  向量表示: {vector}")
            print("=======================")

