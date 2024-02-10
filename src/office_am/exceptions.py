# todo handle!!
from functools import wraps

# import pandas as pd

def get_user_input(prompt):
    return input(prompt)


def id_exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
    wrapper: func
    return wrapper



class NotFoundException(Exception):
    def __init__(self, value, found_values):
        self.value = value
        self.found_values = found_values

#
# class SerialNotFound(NotFoundException):
#     def __str__(self):
#         if self.found_values.size == 0 or pd.isna(self.found_values[0]):
#             return f"No serial number found for ID {self.value}"
#         return f"Multiple serial numbers found for ID {self.value}: {', '.join(map(str, self.found_values))}"

#
# class IDNotFound(NotFoundException):
#                                                                                                                                                                                                                                                                                                             # ans = input("No ID found for serial {self.value}. Enter new ID or enter to skip: ")
#                                                                                                                                                                                                                                                                                                             # if not ans:
#                                                                                                                                                                                                                                                                                                             #     pass
#                                                                                                                                                                                                                                                                                                             # else:
#                                                                                                                                                                                                                                                                                                             #     raise
#     def __str__(self):
#
#         if self.found_values.size == 0 or pd.isna(self.found_values[0]):
#             return f"No ID found for serial {self.value}"
#         return f"Multiple IDs found for serial {self.value}: {', '.join(map(str, self.found_values))}"

#
# def convert(df, value, key_column, result_column, exception_class=NotFoundException, replacement_value=None):
#     if replacement_value is not None:
#         return replacement_value
#     result_values = get_matching(df=df, key_column=key_column, result_column=result_column, value=value)
#     if result_values.size == 0 or pd.isna(result_values[0]):
#         raise exception_class(value, result_values)
#     if result_values.size != 1:
#         raise exception_class(value, result_values)
#     return result_values[0]
