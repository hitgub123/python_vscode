from neo4j import GraphDatabase
import os, sys

sys.path.extend(
    [os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_util"))]
)
from model import model_util
# Neo4j 连接配置
URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "neo4jneo4j"

# LLM 配置（使用 Hugging Face 的 T5 模型，支持日语）
llm = model_util.get_model()

# Neo4j 操作类
class MovieGraphRAG:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # 创建电影和演员节点及关系
    def create_movie_graph(self, tx, actor_name, movie_title, role, genre):
        query = (
            "MERGE (a:Actor {name: $actor_name}) "
            "MERGE (m:Movie {title: $movie_title, genre: $genre}) "
            "MERGE (a)-[:ACTED_IN {role: $role}]->(m)"
        )
        tx.run(query, actor_name=actor_name, movie_title=movie_title, role=role, genre=genre)

    # 查询与演员相关的电影信息
    def find_actor_context(self, tx, actor_name):
        query = (
            "MATCH (a:Actor {name: $actor_name})-[:ACTED_IN]->(m:Movie) "
            "RETURN m.title AS title, m.genre AS genre, collect(a.name) AS actors"
        )
        result = tx.run(query, actor_name=actor_name)
        return [record for record in result]

    # 添加数据
    def add_movie_data(self, actor_name, movie_title, role, genre):
        with self.driver.session() as session:
            session.execute_write(self.create_movie_graph, actor_name, movie_title, role, genre)

    # 获取上下文并序列化为文本
    def get_actor_context(self, actor_name):
        with self.driver.session() as session:
            results = session.execute_read(self.find_actor_context, actor_name)
            context = []
            for record in results:
                context.append(
                    f"电影: {record['title']}，类型: {record['genre']}，演员: {', '.join(record['actors'])}"
                )
            return "\n".join(context) if context else "未找到相关信息"

# RAG 流程
def rag_query(actor_name, question):
    # 初始化 Neo4j
    graph = MovieGraphRAG(URI, USERNAME, PASSWORD)

    # 获取知识图谱上下文
    context = graph.get_actor_context(actor_name)
    
    # 构建 LLM 提示
    prompt = f"""
    上下文：
    {context}
    
    用户问题：{question}
    
    请根据上下文回答问题，答案简洁且准确。
    """
    
    # 使用 LLM 生成答案
    response = llm.invoke(prompt)
    
    # 关闭 Neo4j 连接
    graph.close()
    
    return response

# 主程序
def main():
    # 初始化 Neo4j 数据
    graph = MovieGraphRAG(URI, USERNAME, PASSWORD)

    # 添加示例数据
    # graph.add_movie_data("Keanu Reeves", "The Matrix", "Neo")
    # graph.add_movie_data("Keanu Reeves", "John Wick", "John Wick")
    # graph.add_movie_data("Carrie-Anne Moss", "The Matrix", "Trinity")    
    
    # 示例查询
    question = "Carrie-Anne Moss出演了哪些电影？"
    answer = rag_query("Carrie-Anne Moss", question)
    print(f"问题: {question}")
    print(f"回答: {answer}")

if __name__ == "__main__":
    main()