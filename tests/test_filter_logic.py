from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field

from pycommence.filters import CmcFilter, FieldFilter, SortOrder

Logic = Literal['Or', 'And']

FilPair = tuple[CmcFilter, Logic, CmcFilter]
FilSet = FilPair | tuple[FilPair, Logic, FilPair]

# FilNode = FieldFilter | list[FieldFilter, Logic, FieldFilter]
# FilNode1 = CmcFilter | list[CmcFilter | FilNode1, Logic, CmcFilter | FilNode1]
# type Nested2[T] = T | list[Nested2[T]]
# FilLog = CmcFilter | list[CmcFilter, Logic, CmcFilter]
type afil = CmcFilter | list[CmcFilter, Logic, CmcFilter]
# type afil = afil | list[afil, Logic, afil]


# FilNode = list[FilLog]


@dataclass
class FA:
    filters: afil = Field(default_factory=list)

    # filter1: CmcFilter
    # filter2: CmcFilter
    # filter3: CmcFilter
    # filter4: CmcFilter
    # filter5: CmcFilter
    # filter6: CmcFilter
    # filter7: CmcFilter
    # filter8: CmcFilter
    #
    logic12: Logic = 'And'
    logic13: Logic = 'And'
    logic34: Logic = 'And'
    logic25: Logic = 'And'
    logic56: Logic = 'And'
    logic57: Logic = 'And'
    logic78: Logic = 'And'


def test_nested_filters():
    fil1 = FieldFilter(column='col1', value='val1')
    fil2 = FieldFilter(column='col2', value='val2')
    fil3 = FieldFilter(column='col3', value='val3')
    fil4 = FieldFilter(column='col4', value='val4')
    fil5 = FieldFilter(column='col5', value='val5')
    fil6 = FieldFilter(column='col6', value='val6')
    fil7 = FieldFilter(column='col7', value='val7')
    fil8 = FieldFilter(column='col8', value='val8')

    logicA = 'And'
    logicB = 'Or'
    logicC = 'And'
    logicD = 'Or'
    logicE = 'And'
    logicF = 'Or'
    logicG = 'And'

    node1 = [fil1, logicA, fil2]
    node2 = [fil3, logicC, fil4]
    node3 = [node1, logicB, node2]

    node4 = [fil5, logicE, fil6]
    node5 = [fil7, logicG, fil8]
    node6 = [node4, logicF, node5]

    node7 = [node3, logicD, node6]

    fa = FA(filters=node7)
    print(fa)


####################################################


class LogicNode(BaseModel):
    logic: Logic
    children: list[FilterNode | LogicNode]


class FilterNode(BaseModel):
    filter: CmcFilter


Node = LogicNode | FilterNode


class FilterArray(BaseModel):
    """Array of Cursor Filters with nested logic."""

    root: Node
    sorts: tuple[tuple[str, SortOrder], ...] = Field(default_factory=tuple)

    def __str__(self):
        return f'Filters:\n{self._str_recursive(self.root)}\nSorted by {self.view_sort_text}'

    def _str_recursive(self, node: Node, depth=0) -> str:
        indent = '  ' * depth
        if isinstance(node, FilterNode):
            return f'{indent}{node.filter.view_filter_str()}'
        else:
            logic_str = f'{indent}[{node.logic}]\n'
            child_strs = [self._str_recursive(child, depth + 1) for child in node.children]
            return logic_str + '\n'.join(child_strs)

    @property
    def sorts_txt(self):
        return ', '.join([f'{col}, {order.value}' for col, order in self.sorts])

    @property
    def view_sort_text(self):
        return f'[ViewSort({self.sorts_txt})]'

    def add_filter(self, cmc_filter: CmcFilter, parent_logic: LogicNode):
        parent_logic.children.append(FilterNode(filter=cmc_filter))

    def add_logic(self, logic: Logic, parent_logic: LogicNode) -> LogicNode:
        new_logic_node = LogicNode(logic=logic, children=[])
        parent_logic.children.append(new_logic_node)
        return new_logic_node

    @classmethod
    def from_root(cls, root: Node, sorts=None):
        sorts = sorts or ()
        return cls(root=root, sorts=sorts)


# Create filters
filter1 = FieldFilter(column='col1', value='val1')
filter2 = FieldFilter(column='col2', value='val2')
filter3 = FieldFilter(column='col3', value='val3')
filter4 = FieldFilter(column='col4', value='val4')
filter5 = FieldFilter(column='col5', value='val5')
filter6 = FieldFilter(column='col6', value='val6')
filter7 = FieldFilter(column='col7', value='val7')
filter8 = FieldFilter(column='col8', value='val8')

# Create logic tree
root_logic = LogicNode(logic='And', children=[])

# Group (filter1 AND filter2)
logic_a = LogicNode(logic='And', children=[FilterNode(filter=filter1), FilterNode(filter=filter2)])
# Group (filter3 AND filter4)
logic_c = LogicNode(logic='And', children=[FilterNode(filter=filter3), FilterNode(filter=filter4)])
# Group (logic_a OR logic_c)
logic_b = LogicNode(logic='Or', children=[logic_a, logic_c])

# Group (filter5 AND filter6)
logic_e = LogicNode(logic='And', children=[FilterNode(filter=filter5), FilterNode(filter=filter6)])
# Group (filter7 AND filter8)
logic_g = LogicNode(logic='And', children=[FilterNode(filter=filter7), FilterNode(filter=filter8)])
# Group (logic_e OR logic_g)
logic_f = LogicNode(logic='Or', children=[logic_e, logic_g])

# Root logic combining all groups
root_logic.children = [logic_b, logic_f]

# Create FilterArray
filter_array = FilterArray.from_root(root=root_logic)


# Print structure
def test_do():
    print(filter_array)
