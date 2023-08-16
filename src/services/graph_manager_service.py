"""Service takes care of the graph management and the graph operations."""
from typing import List
from nameko.rpc import rpc, RpcProxy
from nameko_redis import Redis

from src.utils.io import randomIdentifier, permissionsToInt

GRAPH_KEY_PATTERN = "graph:{graph_id}"
USER_KEY_PATTERN = "user:{username}:graphs"
USER_PERMISSIONS_KEY_PATTERN = "graph:{graph_id}:permissions"


class GraphManagerService:
    name = "graph_manager_service"

    redis = Redis("development", decode_responses=True, encoding="utf-8")
    code_execution_service = RpcProxy("code_execution_service")
    llm_service = RpcProxy("llm_service")

    # All RPC methods return Status, Message

    @rpc
    def get_serialized_graph(self, graph_id: str):
        """Get graph by id from Redis."""
        graph_id_key = GRAPH_KEY_PATTERN.format(graph_id=graph_id)
        if not self.redis.exists(graph_id_key):
            return False, f"Graph with id {graph_id} does not exist"
        if not self.redis.hexists(graph_id_key, "serialized_graph"):
            return (
                False,
                f"Graph with id {graph_id} does not have a serialized graph",
            )
        return True, self.redis.hget(graph_id_key, "serialized_graph")

    @rpc
    def say_hello(self, name: str):
        """Say hello to the name."""
        return True, f"Hello {name}"

    @rpc
    def create_graph(self, username: str):
        """Create graph in Redis."""
        graph_id = randomIdentifier(length=32)
        graph_id_key = GRAPH_KEY_PATTERN.format(graph_id=graph_id)
        user_key = USER_KEY_PATTERN.format(username=username)
        user_permissions_key = USER_PERMISSIONS_KEY_PATTERN.format(
            graph_id=graph_id
        )

        # First add the graph to the user's list of graphs
        self.redis.sadd(user_key, graph_id)

        # Then add the graph to the graph list
        self.redis.hset(graph_id_key, "owner", username)

        # Add the user as the owner of the graph
        self.redis.hset(
            user_permissions_key, username, permissionsToInt(True, True, True)
        )

        return True, graph_id

    @rpc
    def store_serialized_graph(self, graph_id: str, serialized_graph: str):
        """Store serialized graph in Redis."""
        graph_id_key = GRAPH_KEY_PATTERN.format(graph_id=graph_id)

        # Check if the graph exists
        if not self.redis.exists(graph_id_key):
            return False, f"Graph with id {graph_id} does not exist"

        self.redis.hset(graph_id_key, "serialized_graph", serialized_graph)
        return True, f"Stored updates to graph {graph_id}"

    @rpc
    def delete_graph(self, graph_id):
        """Delete graph from Redis."""
        graph_id_key = GRAPH_KEY_PATTERN.format(graph_id=graph_id)

        # Check if the graph exists
        if not self.redis.exists(graph_id_key):
            return False, f"Graph with id {graph_id} does not exist"

        # Remove the graph from the owner's list of graphs
        owner = self.redis.hget(graph_id_key, "owner")
        user_key = USER_KEY_PATTERN.format(username=owner)
        self.redis.srem(user_key, graph_id)

        # Delete the graph
        self.redis.delete(graph_id_key)
        self.redis.delete(
            USER_PERMISSIONS_KEY_PATTERN.format(graph_id=graph_id)
        )
        return True, f"Deleted graph {graph_id}"

    @rpc
    def list_graphs(self, username: str):
        """List all graphs in Redis."""
        user_key = USER_KEY_PATTERN.format(username=username)
        if not self.redis.exists(user_key):
            return False, f"User with username {username} does not exist"

        graph_ids = self.redis.smembers(
            USER_KEY_PATTERN.format(username=username)
        )
        return True, list(graph_ids)

    @rpc
    def share_graph(self, graph_id: str, target_user: str, permissions: int):
        """Share graph with another user."""
        graph_id_key = GRAPH_KEY_PATTERN.format(graph_id=graph_id)
        graph_permissions_key = USER_PERMISSIONS_KEY_PATTERN.format(
            graph_id=graph_id
        )

        # Check if the graph exists
        if not self.redis.exists(graph_id_key):
            return False, f"Graph with id {graph_id} does not exist"

        # # Check if the target user exists
        # if not self.redis.exists(
        #     USER_KEY_PATTERN.format(username=target_user)
        # ):
        #     return (
        #         False,
        #         f"Target user with username {target_user} does not exist",
        #     )

        # Add the target user to the graph's permissions
        self.redis.hset(
            graph_permissions_key, target_user, permissionsToInt(*permissions)
        )

        return True, f"Shared graph {graph_id} with user {target_user}"
