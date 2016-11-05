
"""
Visualize possible stitches with the outcome of the validator.
"""

import math
import random
import time
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from mpl_toolkits.mplot3d import Axes3D

SPACE = 25
TYPE_FORMAT = {'a': '^', 'b': 's', 'c': 'v'}


def show(graphs, request, titles, prog='neato', size=None,
         type_format=None, save=False):
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
        axarr[x_val, y_val].set_title(titles[index])
        axarr[x_val, y_val].set_axis_bgcolor("white")
        if not type_format:
            type_format = TYPE_FORMAT
        _plot_subplot(candidate, request.nodes(), prog, type_format,
                      axarr[x_val, y_val])
        y_val += 1
        if y_val > size[1] - 1:
            y_val = 0
            x_val += 1
        index += 1
    fig.tight_layout()
    if save:
        plt.savefig('foo' + str(time.time()) + '.png')
    else:
        plt.show()
    plt.close()


def _plot_subplot(graph, new_nodes, prog, type_format, axes):
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


def show_3d(graphs, request, titles, prog='neato', save=False):
    """
    Show the candidates in 3d - the request elevated above the container.
    """
    fig = plt.figure(figsize=(18, 10))
    fig.set_facecolor('white')
    i = 0

    size = _get_size(len(graphs))

    for graph in graphs:
        axes = fig.add_subplot(size[0], size[1], i+1, projection='3d')
        axes.set_title(titles[i])
        axes._axis3don = False

        _plot_3d_subplot(graph, request, prog, axes)

        i += 1
    fig.tight_layout()
    if save:
        plt.savefig('foo' + str(time.time()) + '.png')
    else:
        plt.show()
    plt.close()


def _plot_3d_subplot(graph, request, prog, axes):
    """
    Plot a single candidate graph in 3d.
    """
    cache = {}

    tmp = graph.copy()
    for node in request.nodes():
        tmp.remove_node(node)

    pos = nx.nx_agraph.graphviz_layout(tmp, prog=prog)

    # the container
    for item in tmp.nodes():
        axes.plot([pos[item][0]], [pos[item][1]], [0], linestyle="None",
                  marker="o", color='gray')
        axes.text(pos[item][0], pos[item][1], 0, item)

    for src, trg in tmp.edges():
        axes.plot([pos[src][0], pos[trg][0]],
                  [pos[src][1], pos[trg][1]],
                  [0, 0], color='gray')

    # the new nodes
    for item in graph.nodes():
        if item in request.nodes():
            for nghb in graph.neighbors(item):
                if nghb in tmp.nodes():
                    x_val = pos[nghb][0]
                    y_val = pos[nghb][1]
                    if (x_val, y_val) in cache.values():
                        x_val = pos[nghb][0] + random.randint(10, SPACE)
                        y_val = pos[nghb][0] + random.randint(10, SPACE)
                    cache[item] = (x_val, y_val)

                    # edge
                    axes.plot([x_val, pos[nghb][0]],
                              [y_val, pos[nghb][1]],
                              [SPACE, 0], color='blue')

            axes.plot([x_val], [y_val], [SPACE], linestyle="None", marker="o",
                      color='blue')
            axes.text(x_val, y_val, SPACE, item)

    for src, trg in request.edges():
        if trg in cache and src in cache:
            axes.plot([cache[src][0], cache[trg][0]],
                      [cache[src][1], cache[trg][1]],
                      [SPACE, SPACE], color='blue')


def _get_size(n_items):
    """
    Calculate the size of the subplot layouts based on number of items.
    """
    n_cols = math.ceil(math.sqrt(n_items))
    n_rows = math.floor(math.sqrt(n_items))
    if n_cols * n_rows < n_items:
        n_cols += 1
    return int(n_rows), int(n_cols)
