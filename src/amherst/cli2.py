import argparse

# from loguru import logger



def parse_ship_args():
    from amherst.models.commence_adaptors import CategoryName

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=CategoryName, choices=list(CategoryName))
    arg_parser.add_argument('record_name', type=str)
    args = arg_parser.parse_args()
    return args


def shipper_cli():
    import asyncio
    import os

    os.environ.setdefault('FLASKWEBGUI_LOG_LEVEL', 'ERROR')
    args = parse_ship_args()
    # logger.info(f'starting shipper for {args.category} {args.record_name}')

    from amherst.ui_runner2 import pycommence_shipper

    asyncio.run(pycommence_shipper(args.category, args.record_name))


if __name__ == '__main__':
    shipper_cli()
