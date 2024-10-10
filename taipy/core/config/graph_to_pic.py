import matplotlib.pyplot as plt
import networkx as nx

class ScenarioConfig:
    def __init__(self):
        self.nodes = ['Start', 'Task1', 'Task2', 'Task3', 'End']
        self.edges = [('Start', 'Task1'), ('Task1', 'Task2'), ('Task2', 'Task3'), ('Task3', 'End')]

    def draw(self):
        """ Draws the graph on screen """
        graph = nx.DiGraph()
        graph.add_nodes_from(self.nodes)
        graph.add_edges_from(self.edges)
        
        pos = nx.spring_layout(graph)
        nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=2000, 
                edge_color='gray', font_size=10, font_weight='bold', arrows=True)

        plt.title("Scenario Config Execution DAG")
        plt.show()

    def export_graph(self, file_name='scenario_config.png', file_format='png'):
        """
        Exports the graph as a picture file (default: PNG format).
        
        Args:
            file_name (str): The name of the output file.
            file_format (str): The format of the output file (e.g., png, jpg).
        """
        graph = nx.DiGraph()

        graph.add_nodes_from(self.nodes)
        graph.add_edges_from(self.edges)

        pos = nx.spring_layout(graph)

        nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=2000, 
                edge_color='gray', font_size=10, font_weight='bold', arrows=True)

        plt.title("Scenario Config Execution DAG")
        plt.savefig(file_name, format=file_format, bbox_inches='tight')

        plt.clf()

        print(f"Graph exported successfully as {file_name}")

