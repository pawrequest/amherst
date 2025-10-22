import json
import os
from dataclasses import dataclass, field

from pandas import Series, read_excel

from .dflt import DFLT_CONST, DFLT_PATHS
from office_tools.excel import df_overwrite_wb


# from word.dde import items_from_hire


def an_id(id_or_serial):
    return len(str(id_or_serial)) == 4


def get_id_and_serial(id_or_serial, df):
    try:
        if an_id(id_or_serial):
            id_num = id_or_serial
            # serial = df[df[DFLT_STRS.ID] == id_num][DFLT_STRS.SERIAL].values[0]
            serial = df[df[DFLT_CONST.ID] == id_num][DFLT_CONST.SERIAL].values[0]
        else:
            # id_num = df[df[DFLT_STRS.SERIAL] == id_or_serial][DFLT_STRS.ID].values[0]
            id_num = df[df[DFLT_CONST.SERIAL] == id_or_serial][DFLT_CONST.ID].values[0]
            serial = id_or_serial
    except Exception as e:
        raise e
    # except ValueError:
    #     print(f"Error: {id_or_serial} not found in {DFLT_STRS.WB}")
    # except KeyError:
    #     print(f"Error: {DFLT_STRS.ID} or {DFLT_STRS.SERIAL} not found in {DFLT.WB}")

    else:
        return id_num, serial


def handle_row(row):
    if row.empty:
        raise ValueError('Asset not found')
    if row.shape[0] > 1:
        raise ValueError('More than one asset found')
    return row.iloc[0]


@dataclass
class Asset:
    id_number: str = field
    serial_number: str = field
    fw_version: str | None = None
    model: str | None = None

    def __eq__(self, other):
        return self.id_number == other.id_number and self.serial_number == other.serial_number


class AssetContext:
    def __init__(self, workbook_ast=None, sheet=None, header_row=None, out_file=None):
        self.workbook_ast = workbook_ast or DFLT_PATHS.AST_WB
        self.out_file = out_file or DFLT_PATHS.AST_OUT
        self.json_file = self.out_file.with_suffix('.json')  # JSON file path with new suffix
        self.sheet = sheet or DFLT_CONST.AST_SHEET
        self.header_row = header_row or DFLT_CONST.AST_HEAD

        if os.path.exists(self.json_file):
            with open(self.json_file) as json_file:
                data = json.load(json_file)
            self.assets = data['df_a']
        else:
            self.assets = read_excel(self.workbook_ast, sheet_name=self.sheet, header=self.header_row)

        self.assets['Number'] = self.assets['Number'].astype(str)

        if out_file and not out_file.exists():
            self.assets.to_excel(out_file, index=False)

    def __enter__(self):
        self.asset_manager = AssetManager(self.assets)
        return self.asset_manager

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_dfs_to_json()
        # if input("Save changes? (y/n)").lower() != 'y':
        #     return
        df_overwrite_wb(input_workbook=self.workbook_ast, sheet=self.sheet, header_row=self.header_row,
                        out_file=self.out_file, df=self.assets)

    def save_dfs_to_json(self):
        data = {
            'df_a': self.assets.to_json(),
        }
        with open(self.json_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)


class AssetManager:

    def __init__(self, df_a):
        self.df_a = df_a

    def row_from_id_or_serial(self, id_or_serial: str) -> Series:
        if an_id(id_or_serial):
            row = self.df_a.loc[self.df_a[DFLT_CONST.ID] == id_or_serial]
        else:
            row = self.df_a.loc[self.df_a[DFLT_CONST.SERIAL] == id_or_serial]
        assert row.shape[0] == 1
        return handle_row(row)

    def set_field_by_id_or_serial(self, id_or_serial: str, field_name: str, value):
        if an_id(id_or_serial):
            self.df_a.loc[self.df_a[DFLT_CONST.ID] == id_or_serial, field_name] = value
        else:
            self.df_a.loc[self.df_a[DFLT_CONST.SERIAL] == id_or_serial, field_name] = value

    def field_from_id_or_serial(self, id_or_serial: str, fieldname: str):
        try:
            if an_id(id_or_serial):
                return self.df_a.loc[self.df_a[DFLT_CONST.ID] == id_or_serial, fieldname].values[0]
            else:
                return self.df_a.loc[self.df_a[DFLT_CONST.SERIAL] == id_or_serial, fieldname].values[0]
        except IndexError:
            raise ValueError(f'Field {fieldname} not found for {id_or_serial}')
        except Exception as e:
            raise e

    def check_fw(self, id_or_serial: str, fw_version=None):
        fw_1 = self.field_from_id_or_serial(id_or_serial=id_or_serial, fieldname=DFLT_CONST.FW)
        if fw_version is None:
            assert fw_1
        else:
            assert fw_1 == fw_version
        ...
