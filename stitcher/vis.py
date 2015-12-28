

import matplotlib.pyplot as plt
import networkx as nx

# TODO: auto scale subplots


def show(graphs, new_nodes, results, prog='neato', size=(2, 4)):
    """
    Display the results using matplotlib.
    """
    f, axarr = plt.subplots(size[0], size[1], figsize=(18, 10))
    f.set_facecolor('white')
    x = 0
    y = 0
    i = 0
    for candidate in graphs:
        # axarr[x, y].axis('off')
        axarr[x, y].xaxis.set_major_formatter(plt.NullFormatter())
        axarr[x, y].yaxis.set_major_formatter(plt.NullFormatter())
        axarr[x, y].xaxis.set_ticks([])
        axarr[x, y].yaxis.set_ticks([])
        axarr[x, y].set_title(results[i])
        axarr[x, y].set_axis_bgcolor("white")
        _plot_sub_plot(candidate, new_nodes, prog, axarr[x, y])
        y += 1
        if y > 3:
            y = 0
            x += 1
        i += 1
    f.tight_layout()
    plt.show()


def _plot_sub_plot(graph, new_nodes, prog, ax):
    pos = nx.graphviz_layout(graph, prog=prog)

    green_nodes = []
    yellow_nodes = []
    red_nodes = []
    blue_nodes = []
    for node, values in graph.nodes(data=True):
        shape = 'o'
        if values['type'] == 'a':
            shape = '^'
        if values['type'] == 'b':
            shape = 's'
        if values['type'] == 'c':
            shape = 'v'
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
                               node_shape=shape, alpha=alpha, ax=ax)

        if node in new_nodes:
            blue_nodes.append(node)
        elif 'rank' in values and values['rank'] > 7:
            red_nodes.append(node)
        elif 'rank' in values and values['rank'] < 7 and values['rank'] > 3:
            yellow_nodes.append(node)
        else:
            green_nodes.append(node)

    # draw the edges
    dotted_line = []
    normal_line = []
    for s, t in graph.edges():
        if s in new_nodes and t not in new_nodes:
            dotted_line.append((s, t))
        else:
            normal_line.append((s, t))
    nx.draw_networkx_edges(graph, pos, edgelist=dotted_line, style='dotted',
                           ax=ax)
    nx.draw_networkx_edges(graph, pos, edgelist=normal_line, ax=ax)

    # draw labels
    nx.draw_networkx_labels(graph, pos, ax=ax)
