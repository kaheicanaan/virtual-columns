from typing import Dict, List, Callable, Any
import pandas as pd
import numpy as np


class UserDefinedFunction:
    """
    Define customized function here. Function MUST takes list of numpy array as input with condition:
    1. for pandas operation:
    each element is a numpy array with shape (n, 1)
    2. for dict operation:
    each element is a numpy array with shape (1, 1)
    """
    @staticmethod
    def __to_numpy_array(arg_list: List[Any]) -> List[np.ndarray]:
        """
        Convert list of element with types
        1. pd.Series of length n
        2. float
        to numpy array with shape (n, 1) for user defined function input
        :param arg_list:
        :return:
        """
        if any(isinstance(element, pd.Series) for element in arg_list):
            # series handling
            ret_list = list()
            # determine length of output array
            max_mength = 0
            for element in arg_list:
                if isinstance(element, pd.Series):
                    max_mength = max(max_mength, len(element))

            for element in arg_list:
                if isinstance(element, pd.Series):
                    ret_list.append(np.reshape(element.values, (max_mength, 1)))
                else:
                    # element is a constant (probably float)
                    np_arr = np.empty((max_mength, 1))
                    np_arr.fill(element)
                    ret_list.append(np_arr)
            return ret_list
        else:
            # dict handling, all element are length 1
            return [np.reshape(element, (1, 1)) for element in arg_list]

    # ========== User Defined Function ==========

    @staticmethod
    def nanmedian(arg_list: List[Any]):
        data = UserDefinedFunction.__to_numpy_array(arg_list)
        arr = np.concatenate(data, axis=1)
        return np.nanmedian(arr, axis=1)

    @staticmethod
    def nanmean(arg_list: List[Any]):
        data = UserDefinedFunction.__to_numpy_array(arg_list)
        arr = np.concatenate(data, axis=1)
        return np.nanmean(arr, axis=1)

    # ========== User Defined Function END ==========

    def __init__(self):
        self.__user_function: Dict[str, Callable] = dict()
        for content in dir(self):
            if content.startswith('_'):
                continue
            else:
                self.__user_function.update({content: getattr(self, content)})

    def add_user_defined_function(self, name: str, func: Callable):
        self.__user_function.update({name: func})

    def get_function(self, func_name: str) -> Callable:
        if func_name in self.__user_function:
            return self.__user_function[func_name]
        else:
            raise Warning('Function {} is not defined yet'.format(func_name))
