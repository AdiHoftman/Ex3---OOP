import json
import math
import random as random
from typing import List
from GraphAlgoInterface import GraphAlgoInterface
from DiGraph import DiGraph
from queue import PriorityQueue
from PriorityNode import PriorityNode
from GraphInterface import GraphInterface
import matplotlib.pyplot as plt
from src.node import NodeData


class GraphAlgo(GraphAlgoInterface):

    def __init__(self, graph: DiGraph = None):
        self.g = graph

    def get_graph(self) -> DiGraph:
        """
        :return: the directed graph on which the algorithm works on.
        """
        return self.g

    def load_from_json(self, file_name: str) -> bool:
        """
        Loads a graph from a json file.
        @param file_name: The path to the json file
        @returns True if the loading was successful, False o.w.
        """
        with open(file_name) as file:
            self.g = DiGraph()
            g_f = json.load(file)
            nodes_load = g_f.get("Nodes")
            edges_load = g_f.get("Edges")
            for node in nodes_load:
                if node.get("pos") is None:
                    self.g.add_node(node.get("id"))
                else:
                    position = str(node.get("pos")).split(",")
                    self.g.add_node(node.get("id"))
                    self.g.nodes[node.get("id")].set_position(float(position[0]), float(position[1]))
            for edge in edges_load:
                src = edge.get("src")
                w = edge.get("w")
                dest = edge.get("dest")
                self.g.add_edge(src, dest, w)
            return True

    def save_to_json(self, file_name: str) -> bool:
        """
       Saves the graph in JSON format to a file
       @param file_name: The path to the out file
       @return: True if the save was successful, False o.w.
       """
        with open(file_name, 'w') as file:
            if self.g is not None:
                save = dict()
                save["Edges"] = list()
                save["Nodes"] = list()

                for n in self.g.nodes.values():
                    if n.position is not None:
                        save["Nodes"].append({"pos": n.position, "id": n.key})
                    else:
                        save["Nodes"].append({"id": n.key})

                for s in self.g.outE.keys():
                    for d, w in self.g.all_out_edges_of_node(s).items():
                        save["Edges"].append({"src": s, "w": w, "dest": d})
                json.dump(save, file)
                return True
            else:
                return False

    def reset_weights_to(self, prm: float) -> None:
        """
         resets all weights of nodes in the graph to a given value.
         @param prm - the value to reset to.
        """
        nodes = self.g.get_all_v()
        for n in nodes.keys():
            nodes[n].set_weight(prm)

    def min_neighbor(self, id1) -> int:
        """
         finds the min weight neighbor to a node around it (directionally).
         @param id1
         @return the min src node that n is neighbor to.
        """
        neighs = self.g.all_in_edges_of_node(id1)
        nodes = self.g.get_all_v()
        min_weight = nodes[id1].get_weight()
        min_key = id1
        for n in neighs.keys():
            if nodes[n].get_weight() != -1:
                if nodes[n].get_weight() < min_weight and nodes[n].get_weight() + neighs[n] == nodes[id1].get_weight():
                    min_key = n
                    min_weight = nodes[n].get_weight()
        return min_key

    def shortest_path_dist(self, id1: int, id2: int) -> float:
        """
         using the Dijkstra algorithm. The function resets all tags to -1 using resetWeightsTo(-1).
         An iterator sets every node's weight to the distance from the source starting from 0 on source node.
         @param id1 - start node
         @param id2 - end (target) node
         @return  the shortest path's distance to a destination node from the source node
        """
        nodes = self.g.get_all_v()
        if id1 not in nodes.keys() or id2 not in nodes.keys():
            return -1
        if id1 == id2:
            return 0
        edges = self.g.all_out_edges_of_node(id1)
        if edges is None:
            return -1
        self.reset_weights_to(-1)
        nodes[id1].set_weight(0)
        neighs = PriorityQueue()
        for n in edges.keys():
            if n != id1:
                nodes[n].set_weight(edges[n])
                neighs.put(PriorityNode(nodes[n].get_weight(), nodes[n]))
        while not neighs.empty():
            n = neighs.get()
            node = n.get_item()
            if node == nodes[id2]:
                return nodes[id2].get_weight()
            edges = self.g.all_out_edges_of_node(node.get_key())
            if edges is not None:
                for i in edges.keys():
                    if nodes[i].get_weight() == -1 or edges[i] + node.get_weight() < nodes[i].get_weight():
                        nodes[i].set_weight(edges[i] + node.get_weight())
                        neighs.put(PriorityNode(nodes[i].get_weight(), nodes[i]))
        return nodes[id2].get_weight()

    def shortest_path(self, id1: int, id2: int) -> (float, list):
        """
         using Dijkstra's algorithm.
         using shortest_path_dist(id1, id2) all the nodes has weights set to the distance from the source to them.
         if there's no such path the function returns null. else, the function
         adds each time a node to a list from the destination node to the source using the weight to decide the path
         (the path must go through each minimal neighbor weight from n to 0 once,
          - n being the distance to destination node).
         @param id1 - start node
         @param id2 - end (target) node
         @return  the shortest path as a list and distance to the destination node from the source node.
        """
        if self.g is not None:
            distance = self.shortest_path_dist(id1, id2)
            if distance == -1:
                return math.inf, None
            path_mirror = [id1]
            if distance == 0:
                return 0, path_mirror
            path_mirror.remove(id1)
            curr = id2
            while curr != id1:
                path_mirror.append(curr)
                curr = self.min_neighbor(curr)
            path_mirror.append(curr)
            path = list(reversed(path_mirror))
            return distance, path
        else:
            return math.inf, None

    def bfs_search(self, id1: int, invert: bool) -> list:
        """
        using the BFS algorithm to get the nodes connected in the graph.
        @param id1: The node id
        @param invert: the way we search in the graph (if True then inverted way, else regularly)
        @return: The list of nodes in the SCC
        """
        nodes = {visited: False for visited in self.g.get_all_v().keys()}
        q = [id1]
        nodes[id1] = True
        comps = [id1]
        while q:
            curr = q.pop()
            if invert:
                neighs = self.g.all_in_edges_of_node(curr)
            else:
                neighs = self.g.all_out_edges_of_node(curr)
            if neighs is not None:
                neighs = neighs.keys()
                for i in neighs:
                    if not nodes[i]:
                        nodes[i] = True
                        q.append(i)
                        comps.append(i)
        return comps

    def connected_component(self, id1: int) -> list:
        """
        Finds the Strongly Connected Component(SCC) that node id1 is a part of.
        @param id1: The node id
        @return: The list of nodes in the SCC
        """
        if self.g is not None:
            nodes = self.g.get_all_v()
            comp1 = self.bfs_search(id1, True)
            comp2 = self.bfs_search(id1, False)

            if id1 not in nodes.keys():
                return []
            else:
                return list(set(comp1) & set(comp2))
        else:
            return None

    def connected_components(self) -> List[list]:
        """
        Finds all the Strongly Connected Component(SCC) in the graph.
        @return: The list all SCC
        """
        if self.g is not None:
            nodes = self.g.get_all_v()
            all_connected = []
            key_set = [*nodes.keys()]
            for n in key_set:
                neighs = self.connected_component(n)
                for i in neighs:
                    if i != n:
                        key_set.remove(i)
                if neighs is not None:
                    all_connected.append(neighs)
            return all_connected
        else:
            return None

    def plot_graph(self) -> None:
        """
        Plots the graph.
        If the nodes have a position, the nodes will be placed there.
        Otherwise, they will be placed in a random but elegant manner.
        @return: None
        """
        nodes = self.g.get_all_v()
        node_list = [*nodes.values()]

        for node in node_list:
            comp1 = self.connected_component(node.get_key())
            for node2 in comp1:
                if nodes[node2].get_position() is None:
                    nodes[node2].set_position(random.uniform(30, 40), random.uniform(30, 40))
                pos = nodes[node2].get_position()
                plt.scatter(pos[0], pos[1], color='c')
                if node2 != node.get_key():
                    node_list.remove(nodes[node2])
        for node in nodes.keys():
            if self.g.all_out_edges_of_node(node) is not None:
                for edges in self.g.all_out_edges_of_node(node).keys():
                    if node != edges:
                        pos1 = nodes[node].get_position()
                        pos2 = nodes[edges].get_position()
                        x1 = pos1[0]
                        y1 = pos1[1]
                        x2 = pos2[0]
                        y2 = pos2[1]
                        plt.arrow(x1, y1, (x2 - x1), (y2 - y1), length_includes_head=True, width=0.000000003,
                                  head_width=0.0002, color = 'black')

        plt.title("My Graph", color = "c")
        plt.show()
