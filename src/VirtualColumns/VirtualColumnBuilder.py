from typing import Dict, List, Tuple, Any
from .ComputationGraph import Node, GraphManager
from .Checker import Checker


class VirtualColumnBuilder:
    def __init__(self, mode='with_full_logic'):
        self.__logic: Dict[str, List[str]] = None
        self.__graph_manager: GraphManager = GraphManager()

    def build_dependency_graph(self, point_logic: Dict[str, List[str]]) -> Tuple[bool, Dict[str, Any]]:
        # checker
        is_valid_logic, error_points = Checker.logic_syntax_checker(point_logic)
        if not is_valid_logic:
            return is_valid_logic, error_points

        self.__logic = point_logic
        self.__graph_manager.build_graph_from_scratch(self.__logic)
        self.__graph_manager.sort_by_topological_order()

        return is_valid_logic, error_points

    def plot_dependency_graph(self):
        pass

    def reset_dependency_graph(self) -> None:
        self.__graph_manager = GraphManager()

    def build_virtual_points(self):
        pass
