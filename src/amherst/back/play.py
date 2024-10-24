from typing import Literal

from amherst.models.maps import CURSOR_MAP


def afunny():
    valid_values = list(CURSOR_MAP.keys())
    FooArgname = Literal[*valid_values]
    assert FooArgname == Literal['Hire', 'Sale', 'Customer']
    print(FooArgname)


if __name__ == '__main__':
    ...
