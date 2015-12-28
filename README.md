# graph sticher

This tool is a little framework to determine possible merges between two graphs
based on a set of required additional relationships (aka as stcihes / edges).
Based on a set of possible resulting candidate graphs we validate which of the
candidates graphs is the "best".

An example use case is a packaging problem: e.g. set of entities need to be
placed in an container which already contains a set of different entities.

Let's assume the entities to be placed can be described using a *request* graph
(as in entities having a relationship) and the existing *container* can be
described as a graph as well (entities having relationships and are already
scored). Nodes & edges in the existing container should be scored to indicate
how loaded/busy they are.

Adding a new set of entities (e.g. a lamp described by the lamp bulb & fitting)
to the existing container (e.g. a house) automatically requires certain
relationships to be added (e.g. the power cable which is plugged into the
socket). But not all possible relationship setups might be good as e.g. adding
another consumer (the lamp) to a certain power socket might impact other
consumers (the microwave) of the same socket as the fuse might give up. How
loaded the power socket is can be expressed through the previously mentioned
score.

Hence **stiching** two graph together is done by adding relationships (edges)
between certain types of nodes from the *container* and the *request*. As
multiple stiches are possible we need to know determine and validate (adhering
conditions like compositions and attribute requirements) the possible
candidates and determine the best. Defining the best one can be done using a
very simple principle. A good stich is defined by:

* all new relationships are satisfied
* the resulting graph is stable and none of the existing nodes (entities) are
impacted by the requested once.

Through the pluggable architecture of graph sticher we can now implement
different algorithms on how to determine if a resulting graph is good
& stable:

* through a simple rule saying for a node of type A, the maximum number of
  incoming dependencies is Y
* through a simple rule saying for a node of type B, that it cannot take more
  incoming relationships when it's score is over an threshold K.
* (many more .e.g implement your own)

This tool obviously can also be used to enhance the placement of workload after
a scheduling decision has been made (based on round-robin, preemptive,
priority, fair share, fifo, ... algorithms) within clusters.

## graph sticher's internals

As mentioned above graph sticher is pluggable to test different algorithms of
weaving/validating two graphs together. Hence it has a pluggable interface for
the *stich()* and *validate()* function (see BaseSticher class).

Too stich two graphs it needs to know how and which relationships are needed:

    Type of source node | Type of target node
    -----------------------------------------
    type_a              | type_x
    ...                 | ...

These are stored in the file (stich.json). Sample graphs & tests can be found
in the **tests** directory as well.

graph sticher is mostly developed to test & play around. Also to check if
[evolutionary algorithms](https://en.wikipedia.org/wiki/Evolutionary_algorithm)
can be developed to determine the best resulting graph.

## Running it

Just do a:

    $ ./run_me.py

You will hopefully see something similar to this:

![output](./figure_1.png?raw=true "Output")
