from nameko.rpc import rpc
from nameko_redis import Redis
from src.services.graph_manager_service import (
    USER_PERMISSIONS_KEY_PATTERN,
    GRAPH_KEY_PATTERN,
)

# Mock user data for simplicity
# In a real-world scenario, this data might be fetched from a database or another service.
USER_DATA = {
    "user1_token": {"username": "user1", "permissions": set(["view", "edit"])},
    "user2_token": {"username": "user2", "permissions": set(["view"])},
}


class AuthService:
    name = "auth_service"

    redis = Redis("development", decode_responses=True, encoding="utf-8")

    @rpc
    def authenticate(self, token):
        print("authenticate", token)
        user = USER_DATA.get(token)
        if user:
            return True, user["username"]
        return False, None

    @rpc
    def authorize(self, user, action, data=None):
        print("authorize", user, action)

        if action in ["create", "list"]:
            # Don't need to check permissions, and don't need graph_id
            return True, True

        elif action == "share":
            # Need to check permissions, and need graph_id
            if data is None:
                return False, None

            graph_id = data.get("graph_id")

            if graph_id is None:
                return False, None

            # Get the owner of the graph and compare it to the user
            graph_id_key = GRAPH_KEY_PATTERN.format(graph_id=graph_id)
            owner = self.redis.hget(graph_id_key, "owner")

            if owner is None:
                return False, None

            if owner != user:
                return True, False

            return True, True

        if action in ["view", "edit", "delete", "run", "share"]:
            # Need to check permissions, and need graph_id
            if data is None:
                return False, None

            graph_id = data.get("graph_id")
            if graph_id is None:
                return False, None

            permissions_key = USER_PERMISSIONS_KEY_PATTERN.format(
                graph_id=graph_id
            )

            if not self.redis.hexists(permissions_key, user):
                # If user isn't mentioned in the permissions, they don't have access
                return True, False

            permissions = int(self.redis.hget(permissions_key, user))

            if action == "view":
                return True, (permissions & 1 == 1)
            elif action in ["edit", "delete"]:
                return True, (permissions & 2 == 2)
            elif action == "run":
                return True, (permissions & 4 == 4)
            else:
                return False, None
