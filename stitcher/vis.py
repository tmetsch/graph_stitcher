
"""
Visualize possible stitches with the outcome of the validator.
"""

import math

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

TYPE_FORMAT = {'a': '^', 'b': 's', 'c': 'v'}


def show(graphs, new_nodes, results, prog='neato', size=None,
         type_format=None):
    """
    Display the results using matplotlib.
    """
    if not size:
        size = _get_size(len(graphs))
    fig, axarr = plt.subplots(size[0], size[1], figsize=(18, 10))
    fig.set_facecolor('white')
    x_val = 0
    y_val = 0
    index = 0

    if size[0] == 1:
        axarr = np.array(axarr).reshape((1, size[1]))

    for candidate in graphs:
        # axarr[x_val, y_val].axis('off')
        axarr[x_val, y_val].xaxis.set_major_formatter(plt.NullFormatter())
        axarr[x_val, y_val].yaxis.set_major_formatter(plt.NullFormatter())
        axarr[x_val, y_val].xaxis.set_ticks([])
        axarr[x_val, y_val].yaxis.set_ticks([])
        axarr[x_val, y_val].set_title(results[index])
        axarr[x_val, y_val].set_axis_bgcolor("white")
        if not type_format:
            type_format = TYPE_FORMAT
        _plot_sub_plot(candidate, new_nodes, prog, type_format,
                       axarr[x_val, y_val])
        y_val += 1
        if y_val > size[1] - 1:
            y_val = 0
            x_val += 1
        index += 1
    fig.tight_layout()
    plt.show()


def _plot_sub_plot(graph, new_nodes, prog, type_format, axes):
    """
    Plot a single candidate graph.
    """
    pos = nx.nx_agraph.graphviz_layout(graph, prog=prog)

    # draw the nodes
    for node, values in graph.nodes(data=True):
        shape = 'o'
        if values['type'] in type_format:
            shape = type_format[values['type']]
        color = 'g'
        alpha = 0.8
        if node in new_nodes:
            color = 'b'
            alpha = 0.2
        elif 'rank' in values and values['rank'] > 7:
            color = 'r'
        elif 'rank' in values and values['rank'] < 7 and values['rank'] > 3:
            color = 'y'
        nx.draw_networkx_nodes(graph, pos, nodelist=[node], node_color=color,
                               node_shape=shape, alpha=alpha, ax=axes)

    # draw the edges
    dotted_line = []
    normal_line = []
    for src, trg in graph.edges():
        if src in new_nodes and trg not in new_nodes:
            dotted_line.append((src, trg))
        else:
            normal_line.append((src, trg))
    nx.draw_networkx_edges(graph, pos, edgelist=dotted_line, style='dotted',
                           ax=axes)
    nx.draw_networkx_edges(graph, pos, edgelist=normal_line, ax=axes)

    # draw labels
    nx.draw_networkx_labels(graph, pos, ax=axes)


def _get_size(n_items):
    """
    Calculate the size of the subplot layouts based on number of items.
    """
    n_cols = math.ceil(math.sqrt(n_items))
    n_rows = math.floor(math.sqrt(n_items))
    if n_cols * n_rows < n_items:
        n_cols += 1
    return int(n_rows), int(n_cols)
