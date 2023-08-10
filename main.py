# Sample code for running an example Graph
from src.graph.graph import Graph


def main():
    """
     A        H
    / \      /
    B  C    /
    |  | \ /
    D  E  F
    \ / \ /
        G
    """
    graph = Graph()

    graph.addBlock("A")
    graph.addBlock("B")
    graph.addBlock("C")
    graph.addBlock("D")
    graph.addBlock("E")
    graph.addBlock("F")
    graph.addBlock("G")
    graph.addBlock("H")

    graph.connectBlocks("A", "B")
    graph.connectBlocks("A", "C")
    graph.connectBlocks("B", "D")
    graph.connectBlocks("C", "E")
    graph.connectBlocks("H", "F")
    graph.connectBlocks("C", "F")
    graph.connectBlocks("D", "G")
    graph.connectBlocks("E", "G")
    graph.connectBlocks("F", "G")

    print(graph.getBlockEvaluationOrder())

    graph.runAllBlocks()


if __name__ == "__main__":
    main()
