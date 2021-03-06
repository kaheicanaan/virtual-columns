from .Const import *
from typing import List, Dict, Tuple, Set
from copy import deepcopy


class Node:
    def __init__(self, name: str):
        # point attr
        self.__name: str = name
        self.__edges: List[Node] = list()
        self.__is_virtual_point: bool = None

        # graph attr
        self.visited: bool = False

    def add_edge(self, node: 'Node'):
        self.__edges.append(node)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def number_of_edges(self) -> int:
        return len(self.__edges)

    @property
    def edges(self) -> List['Node']:
        return self.__edges

    @property
    def is_virtual_point(self) -> bool:
        return self.__is_virtual_point

    @is_virtual_point.setter
    def is_virtual_point(self, virtual: bool):
        # ensure point is not re-assigned
        assert self.__is_virtual_point is None
        self.__is_virtual_point = virtual


class GraphManager:
    def __init__(self):
        self.__point_node_caches: Dict[str, Node] = dict()  # store address of point node
        self.__topological_order: List[str] = list()  # for topological order (all points)

        self.__sub_tree: List[str] = list()  # for dependency (limit to expected output)

    def build_graph_from_scratch(self, point_logic):
        for single_point_logic in point_logic.items():
            self._add_logic_to_graph(single_point_logic)

    @property
    def nodes(self) -> Dict[str, Node]:
        return deepcopy(self.__point_node_caches)

    @property
    def column_properties(self) -> Dict[str, dict]:
        ret = dict()
        for name, node in self.__point_node_caches.items():
            ret.update({
                name: {'edges': node.number_of_edges, 'is_virtual': node.is_virtual_point}
            })
        return ret

    def _add_logic_to_graph(self, single_logic: Tuple[str, List[str]]):
        target, logic = single_logic
        # check if target a physical point
        # for physical point, logic list should be empty
        target_node = self._get_or_create(target)
        if len(logic) == 0:
            # mark it as physical point
            target_node.is_virtual_point = False
        else:
            # mark it as virtual point
            target_node.is_virtual_point = True

        dependent_points = [point for point in logic if self.__is_value(point)]
        for point in dependent_points:
            point_node = self._get_or_create(point)
            # add dependency of "point" to "target"
            target_node.add_edge(point_node)

    def _get_or_create(self, point_name: str) -> Node:
        # todo: here maybe we can handle the const / function node
        # (i.e. return different node even if there are the same)
        if point_name not in self.__point_node_caches:
            self.__point_node_caches.update({point_name: Node(point_name)})
        return self.__point_node_caches[point_name]

    def __is_value(self, name: str) -> bool:
        if name in OPERATOR_POOL:
            return False
        else:
            return True

    def sort_by_topological_order(self) -> None:
        self.__reset_visit_node()
        self.__topological_order = list()
        # O(n) searching to visit all node
        for node in self.__point_node_caches.values():
            if node.visited:
                continue
            else:
                # if a node is unvisited, visit it and all of its unvisited children
                self.__visit_all_node(node)

    @property
    def topological_order(self) -> List[str]:
        return self.__topological_order[:]

    def __reset_visit_node(self) -> None:
        for point, node in self.__point_node_caches.items():
            node.visited = False

    def __visit_all_node(self, node: Node):
        # recursively visit all nodes (points only) in graph
        for child in node.edges:
            if child.visited:
                continue
            else:
                self.__visit_all_node(child)
        node.visited = True
        if self.__is_point(node.name):
            self.__topological_order.append(node.name)
        return

    def __is_point(self, name: str) -> bool:
        return True if ':' not in name else False

    def get_dependency(self, expected_output: List[str]) -> Tuple[List[str], List[str]]:
        # implementation: refer to sort_by_topological_order()
        self.__reset_visit_node()
        self.__sub_tree = list()
        required_nodes = [self.__point_node_caches[col] for col in expected_output]
        # O(n) searching to visit all children
        for node in required_nodes:
            if node.visited:
                continue
            else:
                # if a node is unvisited, visit it and all of its unvisited children
                self.__get_all_leave(node)

        # return (1) leaves for query and (2) sub-tree for virtual column building
        leaves = [leaf for leaf in self.__sub_tree if self.__point_node_caches[leaf].is_virtual_point is False]
        return leaves, self.__sub_tree

    def __get_all_leave(self, node: Node):
        # implementation: refer to __visit_all_node()
        # recursively visit and return all children
        for child in node.edges:
            if child.visited:
                continue
            else:
                self.__get_all_leave(child)
        node.visited = True
        if self.__is_point(node.name):
            self.__sub_tree.append(node.name)
        return
