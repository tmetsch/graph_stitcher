

import matplotlib.pyplot as plt
import networkx as nx


def show(landscapes, new_nodes, results, prog='neato', size=(2, 4)):
    """
    Display the results using matplotlib.
    """
    f, axarr = plt.subplots(size[0], size[1], figsize=(18, 10))
    f.set_facecolor('white')
    x = 0
    y = 0
    i = 0
    for candidate in landscapes:
        axarr[x, y].axis('off')
        axarr[x, y].set_title(results[i])
        axarr[x, y].set_axis_bgcolor("white")
        _plot_sub_plot(candidate, new_nodes, prog, axarr[x, y])
        y += 1
        if y > 3:
            y = 0
            x += 1
        i += 1
    plt.show()


def _plot_sub_plot(graph, new_nodes, prog, ax):
    pos = nx.graphviz_layout(graph, prog=prog)

    green_nodes = []
    yellow_nodes = []
    red_nodes = []
    blue_nodes = []
    for node, values in graph.nodes(data=True):
        if node in new_nodes:
            blue_nodes.append(node)
        elif 'score' in values and values['score'] > 7:
            red_nodes.append(node)
        elif 'score' in values and values['score'] < 7 and values['score'] > 3:
            yellow_nodes.append(node)
        else:
            green_nodes.append(node)

    # draw nodes with score between 0-3 green, 3-7 yellow, 7-10 red
    nx.draw_networkx_nodes(graph, pos, nodelist=green_nodes, node_color='g',
                           alpha=0.8, ax=ax)
    nx.draw_networkx_nodes(graph, pos, nodelist=yellow_nodes, node_color='y',
                           alpha=0.8, ax=ax)
    nx.draw_networkx_nodes(graph, pos, nodelist=red_nodes, node_color='r',
                           alpha=0.8, ax=ax)
    # new nodes are blue
    nx.draw_networkx_nodes(graph, pos, nodelist=blue_nodes, node_color='b',
                           alpha=0.2, ax=ax)

    # draw the edges
    nx.draw_networkx_edges(graph, pos, ax=ax)

    # draw edges
    nx.draw_networkx_labels(graph, pos, ax=ax)
