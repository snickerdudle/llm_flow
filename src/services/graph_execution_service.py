from nameko.rpc import rpc


class GraphExecutionService:
    name = "graph_execution_service"

    @rpc
    def execute_graph(self, graph_data):
        # Implement the logic to execute the graph
        # For this example, we'll just simulate the execution
        # by returning a message.
        return f"Executing graph with data: {graph_data}"
