import json
from nameko.rpc import RpcProxy
from nameko.web.handlers import http
from werkzeug.wrappers import Request, Response


def json_response(code=200, error_message=None, data=None):
    status = "OK"
    if code != 200:
        status = "Error"
    return_json = {"status": status}

    if error_message is not None:
        return_json["message"] = error_message
    if data is not None:
        return_json["data"] = data

    return Response(
        json.dumps(return_json), status=code, mimetype="application/json"
    )


class GatewayService:
    name = "gateway_service"

    auth_service = RpcProxy("auth_service")
    graph_manager_service = RpcProxy("graph_manager_service")
    graph_execution_service = RpcProxy("graph_execution_service")

    @http("GET", "/<string:action>")
    def route_get(self, request, action):
        """A simple HTTP endpoint that accepts a token and an action and returns a message."""
        if not request.is_json:
            return json_response(
                code=400, error_message="Request must be JSON"
            )

        # Get the token from the request body
        data = request.get_json()
        token = data.get("token")
        graph_id = data.get("graph_id")
        print(f"Got action {action} and token {token}")

        # Authenticate and authorize the user
        authenticated, username = self.auth_service.authenticate(token)
        if not authenticated:
            return json_response(
                code=403, error_message="Authentication failed"
            )
        status, authorized = self.auth_service.authorize(
            username, action, data
        )
        if not status:
            return json_response(
                code=500, error_message="Authorization failed"
            )
        if not authorized:
            return json_response(
                code=403,
                error_message=f"{username} is not authorized for {action} on graph {graph_id}",
            )

        # After successful authentication and authorization, you can proceed
        # with the actual logic.
        match action:
            case "create":
                return self.handle_create(username)
            case "view":
                return self.handle_view(request.get_json())
            case "edit":
                return self.handle_edit(request.get_json())
            case "delete":
                return self.handle_delete(request.get_json())
            case "list":
                return self.handle_list(username)
            case "run":
                return self.handle_run(request.get_json())
            case "share":
                return self.handle_share(request.get_json())
            case _:
                return Response(f"Unknown action {action}", status=400)

    def handle_create(self, username):
        """Handle the create action."""
        status, message = self.graph_manager_service.create_graph(username)
        if not status:
            return json_response(code=404, error_message=message)
        return json_response(data={"graph_id": message})

    def handle_view(self, data):
        """Handle the view action."""
        status, message = self.graph_manager_service.get_serialized_graph(
            data["graph_id"]
        )
        if not status:
            return json_response(code=404, error_message=message)
        return json_response(
            data={"graph_id": data["graph_id"], "serialized_graph": message}
        )

    def handle_edit(self, data):
        """Handle the edit action."""
        status, message = self.graph_manager_service.store_serialized_graph(
            data["graph_id"], data["serialized_graph"]
        )
        if not status:
            return json_response(code=404, error_message=message)
        return json_response(data={"graph_id": data["graph_id"]})

    def handle_delete(self, data):
        """Handle the delete action."""
        status, message = self.graph_manager_service.delete_graph(
            data["graph_id"]
        )
        if not status:
            return json_response(code=404, error_message=message)
        return json_response(data={"graph_id": data["graph_id"]})

    def handle_list(self, username):
        """Handle the list action."""
        status, message = self.graph_manager_service.list_graphs(username)
        if not status:
            return json_response(code=404, error_message=message)
        # Turn the list into a JSON string
        return json_response(data={"graphs": message})

    def handle_run(self, data):
        """Handle the run action."""
        status, message = self.graph_execution_service.execute_graph(
            data["graph_id"]
        )
        if not status:
            return json_response(code=404, error_message=message)
        return json_response(data={"graph_id": data["graph_id"]})

    def handle_share(self, data):
        """Handle the share action."""
        status, message = self.graph_manager_service.share_graph(
            data["graph_id"], data["target_user"], data["permissions"]
        )
        if not status:
            return json_response(code=404, error_message=message)
        return json_response(data={"graph_id": data["graph_id"]})
