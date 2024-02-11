from pycommence.wrapper.cmc_db import get_csr
from pycommence import dynamic as dy
TEST_HIRE_NAME = 'test - 10/11/2023 ref 42744'
TEST_SALE_NAME = 'test - 2/10/2024 ref 784'


def test_get_schema():
    csr = get_csr('Hire')
    schema = csr.get_schema
    print(schema)
    ...

def test_create_dynamic():
    HireModel = dy.create_pydantic_model_from_db('Hire')
    csr = get_csr('Hire')
    rec = csr.get_record(TEST_HIRE_NAME)
    hire = HireModel.model_validate(rec)
    ...

    ...