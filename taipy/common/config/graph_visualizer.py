import matplotlib.pyplot as plt
import networkx as nx

def visualize_scenario_graph(config):
    G = nx.DiGraph()

    for node in config['nodes']:
        G.add_node(node['id'], label=node['label'])
    for edge in config['edges']:
        G.add_edge(edge['from'], edge['to'], label=edge['label'])

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    plt.show()
