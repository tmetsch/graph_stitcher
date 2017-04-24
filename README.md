# Graph stitching

This tool is a little framework to determine possible merges between two graphs
based on a set of required additional relationships (aka stitches / edges).
Based on a set of possible resulting candidate graphs we validate which of the
candidates graphs is the "best".

An example use case is a packaging problem: e.g. set of entities need to be
placed in an container which already contains a set of different entities.

Let's assume the entities to be placed can be described using a *request* graph
(as in entities having a relationship) and the existing *container* can be
described as a graph as well (entities having relationships and are already
ranked). Nodes & edges in the existing container should be ranked to indicate
how loaded/busy they are.

Adding a new set of entities (e.g. a lamp described by the lamp bulb & fitting)
to the existing container (e.g. a house) automatically requires certain
relationships to be added (e.g. the power cable which is plugged into the
socket). But not all possible relationship setups might be good as e.g. adding
another consumer (the lamp) to a certain power socket might impact other
consumers (the microwave) of the same socket as the fuse might give up. How
loaded the power socket is can be expressed through the previously mentioned
rank.

Hence **stitching** two graphs together is done by adding relationships (edges)
between certain types of nodes from the *container* and the *request*. As
multiple stitches are possible we need to know determine and validate (adhering
conditions like compositions and attribute requirements) the possible
candidates and determine the best. Defining the best one can be done using a
very simple principle. A good stitch is defined by:

* all new relationships are satisfied
* the resulting graph is stable and none of the existing nodes (entities) are
impacted by the requested once.

Through the pluggable architecture of this tool we can now implement
different algorithms on how to determine if a resulting graph is good
& stable:

* through a simple rule saying for a node of type A, the maximum number of
  incoming dependencies is Y
* through a simple rule saying for a node of type B, that it cannot take more
  incoming relationships when it's rank is over an threshold K.
* (many more .e.g implement your own)

This tool obviously can also be used to enhance the placement of workload after
a scheduling decision has been made (based on round-robin, preemptive,
priority, fair share, fifo, ... algorithms) within clusters.

## graph stitcher's internals

As mentioned above graph stitcher is pluggable, to test different algorithms of
**graph stitching** & validation of the same. Hence it has a pluggable
interface for the *stitch()* and *validate()* routine (see *BaseStitcher*
class).

To stitch two graphs the tool needs to know which relationships are needed:

    Type of source node | Type of target node
    -----------------------------------------
    type_a              | type_x
    ...                 | ...

These are stored in the file (stitch.json). Sample graphs & tests can be found
in the **tests** directory as well.

There is a *conditional_filter()* function implemented which can do some basic
filtering. Implementing your own is possible by passing conditions and the
*conditional_filter()* routine you want to use as parameters to the *stich()*
call.

The basic filter support the following operations:

  * based on required (exception: not equal operation) target attributes -
    example below: node a requires it's stitched target to have an attribute
    'foo' with value 'y'
    * this can also be done with: not equal, larger than, less than or by a
      regular expression.
  * the notion that two nodes require the same or different target - example
    below: node 1 & 2 need to have the same stitched target node and node 3 & 4
    need to have different stitched target nodes.
  * the notion that stitched target nodes (not) share a common attribute - 
    example below: node x & y need to be stitched to target nodes which share 
    the same attribute value for the attribute with the name 'group'.

The following dictionary can be passed in as a composition condition:

    {
     'attributes': [('eq', ('a', ('foo', 'y'))),
                    ('neq', ('a', ('foo', 5))),
                    ('lt', ('a', ('foo', 4))),
                    ('lg', ('a', ('foo', 7))),
                    ('regex', ('a', ('foo', '^a')))],
     'compositions': [('same', ('1', '2')),
                      ('diff', ('3', '4')),
                      ('share', ('group', ['x', 'y'])),
                      ('nshare', ('group', ['a', 'b']))]
    }

This graph stitcher is mostly developed to test & play around. Also to check if
[evolutionary algorithms](https://en.wikipedia.org/wiki/Evolutionary_algorithm)
can be developed to determine the best resulting graph. More details on the 
algorithms in place can be found in the [/docs](/docs/algorithms.md) directory.

## Running it

Just do a:

    $ ./run_me.py

You will hopefully see something similar to the following diagram. The *k*,
*l*, *m* nodes form the request. All other nodes represent the container (node
colors indicate the rank, node forms the different types). The stitches are
dotted lines. Each graph is a candidate solution, the results of the
validation are shown as titles of the graphs.

![output](./figure_1.png?raw=true "Output")

To test the evolutionary algorithm run:

    $ ./run_me.py -a evolutionary

Please note that it might not always find a set of good solutions, as the 
container and the request are pretty small. Also note that currently the 
fitness function expresses a fitness for the given conditions; and does not 
include a fitness value for the validation phase.

To test the bidding algorithm in which the container nodes try to find the 
optimal solution run:

    $ ./run_me.py -a bidding
