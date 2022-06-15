# The Dollar Game
A graph-based single-player game inspired by one [Numberphile video](https://youtu.be/U33dsEcKgeQ).
## Description
 A given game is represented by a [connected graph](https://en.wikipedia.org/wiki/Connectivity_(graph_theory)) consisting of nodes (people) and edges (connections).\
Let two people having a connection be called _neigbours_. Each node (person) in this network has a value (some integer amount of money). 

## Actions
Every person can perform two actions:
- <b>give</b>: reduce its own value by a number of its neighbours and increase each of those neigbours' values by one;
- <b>take</b>: vice versa.


## Objective
By executing a sequence of actions with the least possible length distribute money in the network in such a way that no person has debt (a negative value). 


## Tutorial
### Game mode
_Note: has <b>orange</b> outline outline when the game is in progress and green outline in case of the victory._

This window has two regions: the one with the indicators and the second with the game itself (boxed in a thin light blue rectangle).

As is was mentioned above, the game is represented by a graph with people as nodes and connections between them as edges. A number to the south-east of a node shows its value (red if it is negative and white otherwise). By hovering a node and scrolling up/down one can execute the <b>give</b>/<b>take</b> action on this node.

Outside of the game field there are:
- <b>GENUS</b>: [pararmeter] $E-N+1$, where $E$ and $N$ are the number of edges and nodes respectively (we will need it later);
- <b>BANK</b>: [parameter] simply the sum of all values;
- <b>MOVES</b>: [counter] the number of moves executed by the player so far;
- <b>Best</b>: [] (is showed only if the game has been played before) the least number of moves which led to the victory;
- <b>Save</b>: [button] saves the game to the disk (also saves the sequence of moves if pressed after winning)


### Sandbox mode
_Note: has <b>magenta</b> outline._

The game can be created inside of the thin light blue rectangle. Click an empty region to create a node, use your mousewheel while hovering a node to change the latter's value. Left click and hold a node, then release on the other node to create an edge. You can also delete nodes and edges by yada-yada.

### Options window
_Note: has <b>limeish</b> outline._

### Open window
...