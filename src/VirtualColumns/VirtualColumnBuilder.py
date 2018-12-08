from typing import Dict, List, Tuple, Any, Union, Callable
from .ComputationGraph import Node, GraphManager
from .Checker import Checker
from .Const import *
import pandas as pd


class VirtualColumnBuilder:
    def __init__(self, mode='with_full_logic'):
        self.__logic: Dict[str, List[str]] = None
        self.graph_manager: GraphManager = GraphManager()
        self.__operator: Dict[str, ] = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y,
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y,
            '>': lambda x, y: x > y,
            '<': lambda x, y: x < y,
            '>=': lambda x, y: x >= y,
            '<=': lambda x, y: x <= y
        }

    def build_dependency_graph(self, point_logic: Dict[str, List[str]]) -> Tuple[bool, Dict[str, Any]]:
        # checker
        is_valid_logic, error_points = Checker.logic_syntax_checker(point_logic)
        if not is_valid_logic:
            return is_valid_logic, error_points

        self.__logic = point_logic
        self.graph_manager.build_graph_from_scratch(self.__logic)
        self.graph_manager.sort_by_topological_order()

        return is_valid_logic, error_points

    def plot_dependency_graph(self):
        pass

    def reset_dependency_graph(self) -> None:
        self.__logic = None
        self.graph_manager = GraphManager()

    def rebuild_dependency_graph(self, point_logic: Dict[str, List[str]]) -> Tuple[bool, Dict[str, Any]]:
        self.reset_dependency_graph()
        self.build_dependency_graph(point_logic)

    def build_virtual_columns(self, data: Union[pd.DataFrame, dict]) -> Union[pd.DataFrame, dict]:
        def to_stack(tagged_value) -> Union[pd.Series, float, bool]:
            if 'c:' in tagged_value:
                return float(tagged_value[2:])
            else:
                raise Warning('Unknown tagged value:', tagged_value)
        def do_numerical_operation(value1, value2, opt):
            # todo: handle invalid type opeartion. e.g. 10 * True should return 10 * 1.0 = 10.0
            return self.__operator[opt](value1, value2)


        data_type = 'df' if isinstance(data, pd.DataFrame) else 'dict'
        for column in self.graph_manager.topological_order:
            if len(self.__logic[column]) == 0:
                # not a virtual column
                continue
            print(column, self.__logic[column])
            stack = list()
            for element in self.__logic[column]:
                if element in OPERATOR_POOL:
                    value_2 = stack.pop()
                    value_1 = stack.pop()
                    stack.append(do_numerical_operation(value_1, value_2, element))
                elif ':' in element:
                    stack.append(to_stack(element))
                else:
                    stack.append(data[element])

            if data_type == 'df':
                data[column] = stack.pop()
            else:
                data.update({column: stack.pop()})

        return data

