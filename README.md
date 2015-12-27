# graph weaver

This tool is a little framework to determine possible merges between two graphs
based on a set of required relationships (edges). Based on a set of possible
resulting graphs we validate which of the candidate graphs is the "best".

An example use case is a packaging problem: e.g. set of entities need to be
placed in an container (read a landscape from now on) which already contains a
set of different entities.

Let's assume the entities to be placed can be described using a *request* graph
(as in entities having a relationship) and the existing *landscape* can be
described as a graph as well (entities having relationships and are already
scored). Nodes & edges in the existing landscape should be scored to indicate
how loaded/busy they are.

Adding a new set of entities (e.g. a lamp described by the lamp bulb & fitting)
to the existing landscape (e.g. a house) automatically requires certain
relationships to be added (e.g. the power cable which is plugged into the
socket). But not all possible relationship setups might be good as e.g. adding
another consumer (the lamp) to a certain power socket might impact other
consumers (the microwave) of the same socket as the fuse might give up. How
loaded the power socket is can be expressed through the previously mentioned
score.

Hence **weaving** two graph together is done by adding relationships (edges)
between certain types of nodes from the *landscape* and the *request*. As
multiple weaves are possible we need to know determine and validate the
possible candidates and determine the best. Defining the best one can be done
using a very simple principle. A good weave is defined by:

* all new relationships are satisfied
* the resulting graph is stable and none of the existing nodes (entities) are
impacted by the requested once.

Through the pluggable architecture of graph weaver we can now implement
different algorithms on how to determine if a resulting landscape is good
& stable:

* through a simple rule saying for a node of type A, the maximum number of
  incoming dependencies is Y
* through a simple rule saying for a node of type B, that it cannot take more
  incoming relationships when it's score is over an threshold K.
* (many more .e.g implement your own)

This tool obviously can also be used to enhance the placement of workload after
a scheduling decision has been made (based on round-robin, preemptive,
priority, fair share, fifo, ... algorithms) within HPC/Cloud/Grid clusters.

## graph weaver's internals

As mentioned above graph weaver is pluggable to test different algorithms of
weaving/validating two graphs together. Hence it has a pluggable interface for
the *weave()* and *validate()* function (see BaseWeaver class).

To weave two graphs it needs to know how and which relationships are needed:

    Type of source node | Type of target node
    -----------------------------------------
    type_a              | type_x
    ...                 | ...

These are stored in the file (weave.json). Sample graphs & tests can be found
in the **tests** directory as well.

graph weaver is mostly developed to test & play around. Also to check if
[evolutionary algorithms](https://en.wikipedia.org/wiki/Evolutionary_algorithm)
can be developed to determine the best resulting graph.

## Running it

Just do a:

    $ ./run_me.py

You will hopefully see something similar to this:

![output](./figure_1.png?raw=true "Output")
