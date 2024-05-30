from typing import Tuple, List, Union, Set, Dict, Any
import networkit as nk
import pygraphviz as pgv
from math import floor, inf
from networkit import graphio
import json
import threading


class SocialGraph:
    """
    Represents a Social Graph
    """

    TOP_RANKS_N = 10
    EDGE_THRESHOLD = 0.1
    GRAPH_FORMAT = graphio.Format.GraphML
    GRAPH_EDGE_SEP_LEN = 0.1

    def __init__(self, filepath: str, load: bool = False) -> None:
        self.__graphfile = f"{filepath}.graphml"
        self.__nodemapfile = f"{filepath}.json"
        # Thread safe
        self.__lock = threading.RLock()
        # Importance
        self.__node_to_importance = dict()
        self.__node_top_ranks = list()
        # Social path
        self.__sssp_cache = dict()
        # Update optimisation
        self.__need_update = False
        # Graph
        self.__user_to_node = dict()
        self.__node_to_user = dict()
        self.__max_edge_weight = 1
        if load:
            self.__load()
            self.__need_update = True
        else:
            self.__graph = nk.Graph(weighted=True, directed=True)

    # --debug ---

    def overview(self):
        nk.overview(self.__graph)

    # --- end debug ---

    # --- Save and restore ---

    def save(self):
        """Save the graph in a file."""
        with self.__lock:
            # normalize edges
            self.__normalize_edges_weight()
            # save the graph
            graphio.writeGraph(self.__graph, self.__graphfile, self.GRAPH_FORMAT)
            # save the link between node and user_id
            with open(self.__nodemapfile, mode="w") as fp:
                json.dump(self.__node_to_user, fp)

    def __load(self):
        """Load the graph from a file."""
        with self.__lock:
            self.__graph = nk.readGraph(self.__graphfile, self.GRAPH_FORMAT)
            with open(self.__nodemapfile, mode="r") as fp:
                data = json.load(fp)
            self.__node_to_user.clear()
            self.__user_to_node.clear()
            for node, user_id in data.items():
                node = int(node)
                self.__node_to_user[node] = user_id
                self.__user_to_node[user_id] = node

    # --- End save and restore ---

    def __normalize_edges_weight(self):
        """Scale all edges weight between 0 and 1 and remove useless edges."""
        for src, dst in self.__graph.iterEdges():
            weight = self.__graph.weight(src, dst)
            weight /= self.__max_edge_weight
            if weight < self.EDGE_THRESHOLD:
                self.__graph.removeEdge(src, dst)
            else:
                self.__graph.setWeight(src, dst, weight)
            self.__max_edge_weight = 1

    def update(self):
        """Update the algorithm result cache."""
        with self.__lock:
            if not self.__need_update:
                return

            self.__normalize_edges_weight()

            if len(self.__node_to_user) > 0:
                # run the page rank algorithm on the graph
                page_rank = nk.centrality.PageRank(self.__graph)
                page_rank.run()

                # get the result
                ranking = page_rank.ranking()

                # init an array to store the nodes in the top rank
                top_ranks_n = min(len(ranking), self.TOP_RANKS_N)
                top_ranks = [0 for i in range(top_ranks_n)]

                # update node importance and store top rank
                for rank, (node, score) in enumerate(ranking):
                    self.__node_to_importance[node] = (rank, score)
                    if rank < top_ranks_n:
                        top_ranks[rank] = node

                # update top_ranks list
                self.__node_top_ranks = top_ranks

            # Clear the sssp cache
            self.__sssp_cache.clear()
            # the graph is updated now!
            self.__need_update = False

    def __get_user_node(self, user_id: int) -> int:
        """
        This function returns the node number of the user in the graph.
        If the user is not in this graph, a new one will be created.
        """
        if user_id in self.__user_to_node:
            return self.__user_to_node[user_id]
        node = self.__graph.addNode()
        self.__node_to_user[node] = user_id
        self.__user_to_node[user_id] = node
        return node

    def __increase_node_weight(self, src: int, dst: int, weight: float):
        self.__graph.increaseWeight(src, dst, weight)
        curr_weight = self.__graph.weight(src, dst)
        if self.__max_edge_weight < curr_weight:
            self.__max_edge_weight = curr_weight

    def handle_message(
        self, message: Tuple[int, List[int], float], messages: List[Tuple[int, float]]
    ):
        """
        Updates the graph in response to incoming messages.
        message respect this format: (author_id, [target_users_id...], time)
        messages is a list of tuple in this format: (author_id, time)
        """
        with self.__lock:
            author_id, target, time = message

            author_node = self.__get_user_node(author_id)

            # add direct user target
            for user_id in set(target):
                if user_id == author_id:
                    continue
                user_node = self.__get_user_node(user_id)
                self.__increase_node_weight(author_node, user_node, 1)
                w = self.__graph.weight(author_node, user_node)

            # add relative weight to others messages in the channel
            for i, (m_author_id, _) in enumerate(messages):
                if m_author_id == author_id:
                    continue
                weight = 1 / (2 * (i + 1))
                m_author_node = self.__get_user_node(m_author_id)
                self.__increase_node_weight(author_node, m_author_node, weight)

            # the graph need an update now!
            self.__need_update = True

    def __get_node_from_root(self, root: int, max_nodes: int) -> Set[int]:
        """
        Returns a list of node with less depth than the specified from the root
        node.
        """
        nodes = list()
        deque = [root]

        while len(deque) > 0 and len(nodes) <= max_nodes:
            node = deque.pop(0)
            if node not in nodes:
                nodes.append(node)
                sort_key = lambda e: self.__graph.weight(node, e)
                neighbors = sorted(self.__graph.iterNeighbors(node), key=sort_key)
                for neighbor in neighbors:
                    deque.append(neighbor)

        return nodes

    def __get_pgv_edge_attr(self, node_src: int, node_dst: int) -> Dict[str, Any]:
        """Returns the attributs of the edge for pygraphviz"""
        # weight
        weight_src_dst = self.__graph.weight(node_src, node_dst)
        weight_dst_src = self.__graph.weight(node_dst, node_src)
        weight_mean = (weight_src_dst + weight_dst_src) / 2
        # color props
        prop_src_dst = weight_src_dst / (weight_src_dst + weight_dst_src)
        prop_dst_src = 1 - prop_src_dst
        # arrow
        if prop_src_dst != 0 and prop_dst_src != 0:
            arrow = "both"
        elif prop_src_dst != 0 and prop_dst_src == 0:
            arrow = "forward"
        elif prop_src_dst == 0 and prop_dst_src != 0:
            arrow = "back"
        else:
            arrow = "none"
        # define color
        if arrow == "both":
            prop = max(0, prop_src_dst - self.GRAPH_EDGE_SEP_LEN / 2)
            color = f"black;{prop}:red;{self.GRAPH_EDGE_SEP_LEN}:black"
        else:
            color = "black"
        # create and return attributs as dict
        res = dict()
        res["weight"] = weight_mean
        res["penwidth"] = "2"
        res["color"] = color
        res["dir"] = arrow
        return res

    def to_pygraphviz(self, user_id: int, max_nodes: int = 10) -> pgv.AGraph:
        """
        The pygraphviz graph centered on the specified user is returned.
        The displayed nodes are filtered to provide a useful graph.
        """
        with self.__lock:
            nk_node_root = self.__get_user_node(user_id)
            nk_nodes = list(self.__get_node_from_root(nk_node_root, max_nodes))

            graph = pgv.AGraph()

            # define graph properties
            graph.graph_attr["root"] = user_id
            #graph.graph_attr["size"] = "9.375"
            graph.node_attr["style"] = "filled"
            graph.node_attr["colorscheme"] = "orrd9"

            # store max weight
            weight_max = -inf

            # create nodes and edges
            for nk_node_user in nk_nodes:
                user_id = self.__node_to_user[nk_node_user]
                # create the node with color
                node_color = floor((self.get_importance(user_id) * 8) + 1)
                label_color = "black" if node_color < 6 else "white"
                graph.add_node(user_id, fillcolor=str(node_color), fontcolor=label_color)
                for neighbor_id in self.get_interactions(user_id):
                    # skip if it's not is our nodes list
                    nk_node_neighbor = self.__user_to_node[neighbor_id]
                    if nk_node_neighbor not in nk_nodes:
                        continue
                    # skip if the edge exists
                    if graph.has_edge(user_id, neighbor_id):
                        continue
                    # get edge attributs
                    edge_attr = self.__get_pgv_edge_attr(nk_node_user, nk_node_neighbor)
                    # update max edge
                    if edge_attr["weight"] > weight_max:
                        weight_max = edge_attr["weight"]
                    # create the edge
                    graph.add_edge(user_id, neighbor_id, **edge_attr)

            # update graph edges size
            max_penwidth = 5
            for edge in graph.edges_iter():
                penwidth = max(
                    (float(edge.attr["weight"]) * max_penwidth) / weight_max, 1
                )
                edge.attr["penwidth"] = str(penwidth)

            return graph

    def get_importance(self, user_id: int) -> float:
        """
        This function returns a score indicating the importance of The
        importance is a value ranging from 0 to 1. If no data is available for
        the user, 0 will be returned.
        """
        with self.__lock:
            user_node = self.__get_user_node(user_id)
            if user_node in self.__node_to_importance:
                rank = self.__node_to_importance[user_node][0]+1
                return (len(self.__node_to_importance)-rank) / len(self.__node_to_importance)
            return 0

    def get_rank(self, user_id: int) -> Union[int, None]:
        """
        This function returns the user's rank in the graph. If the user does
        not have importance, the function will return 'None'.
        """
        with self.__lock:
            user_node = self.__get_user_node(user_id)

            if user_node in self.__node_to_importance:
                return self.__node_to_importance[user_node][0]

            return None

    def get_top_ranks(self) -> List[int]:
        """
        Returns a list of user IDs that are in the top ranks.
        """
        with self.__lock:
            return [self.__node_to_user[node] for node in self.__node_top_ranks]

    def get_social_path(self, user_id_src: int, user_id_dst: int) -> List[int]:
        """
        Returns the list of user id's from the source user to the target user.
        """
        with self.__lock:
            user_node_src = self.__get_user_node(user_id_src)
            user_node_dst = self.__get_user_node(user_id_dst)

            if (user_id_src, user_id_dst) in self.__sssp_cache:
                return self.__sssp_cache[(user_id_src, user_id_dst)]
            else:
                sssp = nk.distance.BFS(
                    self.__graph, user_node_src, target=user_node_dst
                )
                sssp.run()
                sc_path = [
                    self.__node_to_user[node] for node in sssp.getPath(user_node_dst)
                ]
                self.__sssp_cache[(user_id_src, user_id_dst)] = sc_path
                return sc_path

    def get_interactions(self, user_id: int, max_users: int = 10) -> List[Tuple[int]]:
        """
        This function returns a list of users with whom the specified user has
        had interactions.
        Each item in the list is a tuple in the format (user_id, weight).
        """
        with self.__lock:
            user_node = self.__get_user_node(user_id)

            result = []

            for node, weight in self.__graph.iterNeighborsWeights(user_node):
                reverse_weight = self.__graph.weight(node, user_node)
                node_user = self.__node_to_user[node]
                result.append((node_user, (weight + reverse_weight) / 2))

            # sort the user by mean weight
            result = sorted(result, key=lambda e: e[1])[:max_users]

            # get only the users id
            result = [e[0] for e in result]

            return result

    def get_interest(self, user1: int, user2: int):
        """Returns the interest of user1 to user2 between 0 and 1."""
        with self.__lock:
            node_user1 = self.__get_user_node(user1)
            node_user2 = self.__get_user_node(user2)
            weight_src_dst = self.__graph.weight(node_user1, node_user2)
            weight_dst_src = self.__graph.weight(node_user2, node_user1)
            weight_sum = weight_src_dst + weight_dst_src
            if weight_sum == 0:
                return 0
            return weight_src_dst / weight_sum
