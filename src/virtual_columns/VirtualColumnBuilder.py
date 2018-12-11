from typing import Dict, List, Tuple, Any, Union, Callable
from .ComputationGraph import Node, GraphManager
from .Checker import Checker
from .Const import *
from .UserDefinedFunction import UserDefinedFunction
import pandas as pd


class VirtualColumnBuilder:
    def __init__(self, mode='with_full_logic'):
        self.__logic: Dict[str, List[str]] = None
        self.graph_manager: GraphManager = GraphManager()
        self.udf: UserDefinedFunction = UserDefinedFunction()
        self.__numeric_operator: Dict[str, Callable] = {
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
        return self.build_dependency_graph(point_logic)

    def determine_required_columns(self, expected_output: List[str]) -> List[str]:
        # return all dependency, in topological order
        return self.graph_manager.get_dependency(expected_output)

    def build_virtual_columns(self, data: Union[pd.DataFrame, dict], expected_output: List[str])\
            -> Union[pd.DataFrame, dict]:
        def to_stack(tagged_value) -> Union[pd.Series, float, bool]:
            if 'c:' in tagged_value:
                return float(tagged_value[2:])
            else:
                raise Warning('Unknown tagged value:', tagged_value)

        def do_numerical_operation(value1, value2, opt):
            # todo: handle invalid type opeartion. e.g. 10 * True should return 10 * 1.0 = 10.0
            return self.__numeric_operator[opt](value1, value2)

        # ===== build virtual columns =====
        # check whether input is a dictionary
        is_dict = isinstance(data, dict)

        # sequentially build virtual column
        for column in expected_output:
            if len(self.__logic[column]) == 0:
                # not a virtual column
                continue

            # perform numeric operation / apply function
            operand_stack = list()
            for element in self.__logic[column]:
                if element in OPERATOR_POOL:
                    # normal operator takes 2 operands only
                    value_2 = operand_stack.pop()
                    value_1 = operand_stack.pop()
                    operand_stack.append(do_numerical_operation(value_1, value_2, element))
                elif 'f:' in element:
                    tag, func, args = element.split(':')
                    arg_list = list()
                    # pop n operands
                    for i in range(int(args)):
                        arg_list.append(operand_stack.pop())
                    # reverse list [arg3, arg2, arg1] -> [arg1, arg2, arg3]
                    arg_list.reverse()
                    # apply user defined function
                    values = self.udf.get_function(func)(arg_list)
                    if is_dict:
                        values = values[0]
                    operand_stack.append(values)
                elif 'c:' in element:
                    # append float to stack
                    operand_stack.append(to_stack(element))
                else:
                    # append pd.Series (for pandas operation) / any single object (for dictionary operation) to stack
                    operand_stack.append(data[element])

            # assign virtual column into data set
            data[column] = operand_stack.pop()

        return data

