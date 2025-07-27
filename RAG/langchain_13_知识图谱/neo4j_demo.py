from neo4j import GraphDatabase

# Neo4j 数据库连接配置
URI = "neo4j://127.0.0.1:7687"  # 替换为你的 Neo4j 实例 URI
USERNAME = "neo4j"            # 替换为你的用户名
PASSWORD = "neo4jneo4j"         # 替换为你的密码

# 定义一个类来管理 Neo4j 连接和操作
class MovieGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # 创建电影和演员节点，以及出演关系
    def create_movie_graph(self, tx, actor_name, movie_title, role):
        query = (
            "MERGE (a:Actor {name: $actor_name}) "
            "MERGE (m:Movie {title: $movie_title}) "
            "MERGE (a)-[:ACTED_IN {role: $role}]->(m)"
        )
        tx.run(query, actor_name=actor_name, movie_title=movie_title, role=role)

    # 查询演员出演的电影
    def find_actor_movies(self, tx, actor_name):
        query = (
            "MATCH (a:Actor {name: $actor_name})-[:ACTED_IN]->(m:Movie) "
            "RETURN m.title AS title"
        )
        result = tx.run(query, actor_name=actor_name)
        return [record["title"] for record in result]

    # 执行创建操作
    def add_movie_data(self, actor_name, movie_title, role):
        with self.driver.session() as session:
            session.execute_write(self.create_movie_graph, actor_name, movie_title, role)

    # 执行查询操作
    def get_actor_movies(self, actor_name):
        with self.driver.session() as session:
            movies = session.execute_read(self.find_actor_movies, actor_name)
            return movies

# 主程序
def main():
    # 初始化 Neo4j 连接
    graph = MovieGraph(URI, USERNAME, PASSWORD)

    # 添加示例数据
    graph.add_movie_data("Keanu Reeves", "The Matrix", "Neo")
    graph.add_movie_data("Keanu Reeves", "John Wick", "John Wick")
    graph.add_movie_data("Carrie-Anne Moss", "The Matrix", "Trinity")

    # 查询 Keanu Reeves 出演的电影
    movies = graph.get_actor_movies("Keanu Reeves")
    print(f"Keanu Reeves acted in: {movies}")

    # 关闭连接
    graph.close()

if __name__ == "__main__":
    main()