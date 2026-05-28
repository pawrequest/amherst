from pprint import pprint

from pycommence import PyCommence
from pycommence.core.pagination import Pagination


def get_data():
    with (PyCommence('Hire') as pycmc):
        pag = Pagination(limit=100, offset=0)
        csr = pycmc.cursor('Hire')
        data = csr.read_rows(pagination=pag)
    pprint(list(data))


if __name__ == '__main__':
    get_data()
