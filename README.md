# Virtual columns

This repository aims to simplify the features generating work during data preprocessing.

Data from IoT sensors could be very 'unstructured' in the sense that
1. different sensors use different unit (e.g. kW and W, ºC and K) even if they are measuring the same physical quantity
2. quantities are measured indirectly (e.g. power is needed but only ampere and voltage are given)

Here we provide a systematic way to create and manage virtual data.

## Installation
To install the latest version:

```commandline
git clone repo-url
pip install /path/to/repo/src
```

#### Try virtual_column_builder
```commandline
$ python
```

```python
>>> import virtual_columns
>>> 
>>> data = {'a': 1, 'b': 2}
>>> method = {'a': [], 'b': [], 'c': ['a', 'b', '-']}
>>> 
>>> vc = virtual_columns.VirtualColumnBuilder()
>>> vc.build_dependency_graph(method)
(True, {})

>>> target_columns = ['a', 'c']
>>> to_be_queried, output_cols = vc.determine_required_columns(target_columns)
>>> to_be_queried
['a', 'b']
>>> output_cols
['a', 'b', 'c']

>>> data = vc.build_virtual_columns(data, output_cols)
>>> data
{'a': 1, 'b': 2, 'c': -1}
```
Done!

## Preparation
To create the required virtual columns from data, you need to prepare
1. input data
2. calculation methods
3. user defined function (for complicated function)

### input data
- [x] pandas implementation
- [x] dictionary implementation

Input data takes the following forms for batched and streaming data set.

#### pandas DataFrame
For batched data (historical data), base columns are 'physical' data

base data:

|     |  a  |  b  |
|:---:|:---:|:---:|
|  0  |  1  |  2  |
|  1  |  1  |  2  |
|  2  |  1  |  2  |
|  3  |  1  |  2  |

#### dictionary
For streaming data, key values are 'physical' data

base data:

```python
{'a': 1, 'b': 2}
```

### calculation methods
- [x] basic numerical and boolean opeartion
- [ ] more numerical operation: ^ (power), 
- [ ] more boolean operation: & (and), | (or), ^ (xor)
- [x] user defined function

We use post-order traversal* representation for numerical operation logic. 
Logic are store as a dictionary with column name as key and corresponding logic as value. 
Note that for 'physical' data, logic is represented by a empty list 

Here are some example:

```python
# column: post-order traversal representation
method = {
    # physical data
    'a': [],
    'b': [],
    # virtual data, c = a - b
    'c': ['a', 'b', '-'],
    # d = c * (a + b)
    'd': ['c', 'a', 'b', '+', '*']
}
```

*: for UDF with != 2 arguments, we cannot represent the graph in post-order traversal form.

#### operands and operators
There are 2 types of operands. We can distinguish them according to their syntax.
1. physical data: "column_name"
2. constant value: "c:100", integer or float with "c:" as prefix

We separate operator into 2 types, according to the number of arguments their take.
1. Pre-defined operator (takes 2 arguments): +, -, *, /, ==, !=, >, <, >=, <=.
2. user defined function: f:sum:3, function name defined in virtual_columns.UserDefinedFunction with "f:" as prefix and ":{number of arguments}" as suffix

More details about user defined function (UDF) will be provided in later section.

#### Nested details
- [x] data dependencies
- [ ] handle loop dependence

##### dependency
It is very common that a virtual column also depends on other virtual columns. 
Some virtual columns have to be calculated before others. 
This module will automatically handle the column dependencies (as long as there is no loop dependence).

##### data type
Some operations will return boolean.

Some numerical operation might involve both number and boolean, we treat True as 1.0 and False as 0.0.

### user defined function (UDF)
For complicated operation, it is suggested that we use UDF for better readability.
Please go to virtual_columns.UserDefinedFunction for more details. (to be filled)

## How to use
Please study the sample code below about the module's functionality.
Logic flow are given by:
1. feed calculation methods into VirtualColumnBuilder (VC)
2. tell VC what target columns are 
3. VC returns columns that needed to be queried, the output columns in topological order
4. query required data and feed it into VC
5. VC returns data with target columns

Dictionary implementation is used here for simplicity.
```python
from virtual_columns import VirtualColumnBuilder
from pprint import pprint
import pandas as pd
import numpy as np
import random

# all calculation method are defined here
all_point_logic = {
    # 'a_1': ['i', '+', 'j'],  # invalid operation (wrong syntax)
    # 'a_2': ['i', 'j', '+', '-'],  # invalid operation (more operators than points)
    # 'a_3': ['i', 'j', 'k', '+'],  # invalid operation (more points than operators)
    'b': ['i', 'c:3600', '/'],  # divided by a constant
    'c': ['i', 'j', 'k', '+', '*'],  # various operations
    'd': ['i', 'e', '+'],  # sum of other 2 points (1 of them is a virtual point)
    'e': ['j', 'k', '+', 'i', '-'],  # sum of other 3 points
    'g': ['j', 'k', '+'],  # sum of other 2 points
    'h': [],  # 'physical' point, bool
    'i': [],  # 'physical' point
    'j': [],  # 'physical' point
    'k': [],  # 'physical' point
    'l': ['m', 'c:10.0', '>'],  # float > float (comparison)
    'm': ['g', 'h', '*'],  # float * bool (cross type operation)
    'n': ['m', 'c:1', 'j', 'k', 'f:nanmean:3', '+']  # (1) numeric operation, (2) function
}

# virtual columns core
vc = VirtualColumnBuilder()

# build dependency graph based on given calculation method 
# return validility and error message
# is_valid: whether the calculation methods are valid (syntax)
# error_msg: indicate virtual columns with error, and possible errors
is_valid, error_msg = vc.build_dependency_graph(all_point_logic)

if not is_valid:
    pprint(error_msg)
    exit()

# column details: 
# (1) edges: number of children (dependence)
# (2) is_virtual: whether it is a virtual data (None implies constant)
pprint(vc.graph_manager.column_properties)

# topological order (dependency order)
print(vc.graph_manager.topological_order)

# get data with virtual data
# let say we need column 'n'
target_cols = ['n']
to_be_queried, output_cols = vc.determine_required_columns(target_cols)

# base columns to be queried are: ['j', 'k', 'h']
# output columns (in topological order): ['j', 'k', 'g', 'h', 'm', 'n']
# user should query the requried data according to to_be_queried

# input data: {'k': -0.06442726426445117, 'j': 10, 'h': True}
data = {
    'k': random.gauss(0, 1),
    'j': 10,
    'h': True
}

data = vc.build_virtual_columns(data, output_cols)
if isinstance(data, pd.DataFrame):
    print(data.head().T)
else:
    pprint(data)

# output data: 
# {'g': 9.93557273573555,
# 'h': True,
# 'j': 10,
# 'k': -0.06442726426445117,
# 'm': 9.93557273573555,
# 'n': 13.5807636476474}
print(data)

# not shown here, we can provide UDF in for extra calculation method
# demo only, not working
vc.udf.add_user_defined_function('nanstd', np.nanstd)
```

## To do list

#### Handle loop dependence
Implement loop dependence detection in virtual_columns.Checker

#### Vistualize dependencies
It seems quite difficult because the dependency graph is NOT a binary tree (due to multi-argument UDF).
