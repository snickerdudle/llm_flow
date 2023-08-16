"""Service takes care of the graph management and the graph operations."""
from nameko.rpc import rpc, RpcProxy
from nameko_redis import Redis


class GraphService:
    name = "graph_service"

    redis = Redis("development", decode_responses=True, encoding="utf-8")
    code_execution_service = RpcProxy("code_execution_service")
    llm_service = RpcProxy("llm_service")

    @rpc
    def get_serialized_graph_by_id(self, graph_id: str):
        """Get graph by id from Redis."""
        graph_id_key = f"graph_{graph_id}"
        if not self.redis.exists(graph_id_key):
            return None
        return self.redis.get(graph_id_key)

    @rpc
    def say_hello(self, name: str):
        """Say hello to the name."""
        return f"Hello {name}"

    @rpc
    def store_serialized_graph(self, graph_id: str, serialized_graph: str):
        """Store serialized graph in Redis."""
        graph_id_key = f"graph_{graph_id}"
        self.redis.set(graph_id_key, serialized_graph)
