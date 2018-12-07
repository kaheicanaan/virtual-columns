from typing import Dict, List, Tuple
from .Const import OPERATOR_POOL


class Checker:
    @staticmethod
    def logic_syntax_checker(point_logic: Dict[str, List[str]]) -> Tuple[bool, Dict[str, any]]:
        def _single_logic_checker(single_logic: List[str]):
            # real point
            if len(single_logic) == 0:
                return

            # virtual point
            point_list: List[str] = list()
            for element in single_logic:
                if element not in OPERATOR_POOL:
                    point_list.append(element)
                else:
                    # here we assume all operation take 2 arguments
                    try:
                        point_list.pop(-1)
                        point_list.pop(-1)
                        point_list.append('dummy')
                    except IndexError:
                        raise SyntaxError('Invalid logic (more operators than points)')

            # return length of remained point list, it should be zero for normal logic
            if len(point_list) > 1:
                raise SyntaxError('Invalid logic (more points than operators)')

        # check logic loop
        abnormal_point_logic_list = dict()
        for point, logic in point_logic.items():
            try:
                _single_logic_checker(logic)
            except (SyntaxError, IndexError) as e:
                abnormal_point_logic_list.update({point: e})

        return len(abnormal_point_logic_list) == 0, abnormal_point_logic_list
