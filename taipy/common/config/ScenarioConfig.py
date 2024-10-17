import matplotlib.pyplot as plt
import networkx as nx


class ScenarioConfig:
    def __init__(self):
        self.graph = nx.DiGraph()  # Create a directed graph

    def add_node(self, node):
        """Add a node to the graph."""
        self.graph.add_node(node)

    def add_edge(self, from_node, to_node):
        """Add an edge between two nodes."""
        self.graph.add_edge(from_node, to_node)

    def export_graph_as_image(self, file_path):
        """Export the graph as an image."""
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(self.graph)  # Positioning the nodes
        nx.draw(self.graph, pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=10,
                font_weight='bold')

        # Save the graph as an image
        plt.savefig(file_path)
        plt.close()  # Close the plot to avoid display
        print(f"Graph exported as image: {file_path}")


if __name__ == "__main__":
    config = ScenarioConfig()

    # Add vertices (nodes)
    config.add_node("Node1")
    config.add_node("Node2")
    config.add_node("Node3")
    config.add_node("Node4")

    # Add edges (connections)
    config.add_edge("Node1", "Node2")
    config.add_edge("Node1", "Node3")
    config.add_edge("Node2", "Node4")
    config.add_edge("Node3", "Node4")

    # Export the graph as an image
    config.export_graph_as_image("scenario_graph.png")
