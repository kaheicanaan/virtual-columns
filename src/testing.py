from VirtualColumns import VirtualColumnBuilder

from pprint import pprint
import pandas as pd
import numpy as np


all_point_logic = {
    # 'a_1': ['i', '+', 'j'],  # invalid operation (wrong syntax), should be popped
    # 'a_2': ['i', 'j', '+', '-'],  # invalid operation (more operators than points), should be popped
    # 'a_3': ['i', 'j', 'k', '+'],  # invalid operation (more points than operators), should be popped
    'b': ['i', 'c:3600', '/'],  # divided by a constant
    'c': ['i', 'j', 'k', '+', '*'],  # various operations
    'd': ['i', 'e', '+'],  # sum of other 2 points (1 of them is a virtual point)
    'e': ['j', 'k', '+', 'i', '-'],  # sum of other 3 points
    'g': ['j', 'k', '+'],  # sum of other 2 points
    'h': [],  # real point, bool
    'i': [],  # real point
    'j': [],  # real point
    'k': [],  # real point
    'l': ['m', 'c:10.0', '>'],  # float > float
    'm': ['g', 'h', '*'],  # float * bool
    'n': ['c:1'],  # constant column (float)
    'o': ['n', 'c:1', 'j', 'k', 'f:nanmean:3', '+']  # (1) numeric operation, (2) function
}

df = pd.DataFrame(np.random.randn(100), columns=['k'])
df['j'] = 10
df['i'] = 100
df['h'] = True
df['h'][4] = False
print(df.head())
print(df.dtypes)

vc = VirtualColumnBuilder()
is_valid, error_msg = vc.build_dependency_graph(all_point_logic)
pprint(error_msg)
pprint(vc.graph_manager.column_properties)
print(vc.graph_manager.topological_order)

if is_valid:
    df = vc.build_virtual_columns(df)
    print(df.head().T)
