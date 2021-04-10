from typing import Union, List
from argparse import ArgumentParser
from pathlib import Path
from inspect import getmembers, isfunction

from . import parsers
from . import cli_functions



def add_subparsers(parser: ArgumentParser, parent_parser: ArgumentParser) -> None:
    """Adds sub parser to parser and returns it"""
    subparsers = parser.add_subparsers(title="function", dest="function", required=True)

    for subparser_constructors in getmembers(parsers, isfunction):
        # add name of sub parser tp parser
        parser = subparsers.add_parser(
            subparser_constructors[0], parents=[parent_parser]
        )

        # add subparser specific args
        subparser_constructors[1](parser)


def run_cli_function(function: str, **kwargs) -> None:
    """Runs function available from cli"""
    cli_functions_dict = dict(getmembers(cli_functions, isfunction))
    cli_functions_dict[function](**kwargs)
    
def main():
    parser = ArgumentParser(
        description="Process some regular sectional curvature for one relator groups"
    )

    parent_parser = ArgumentParser(add_help=False)

    parent_parser.add_argument(
        "--output-dir", type=Path, help="Path to store output files"
    )

    parent_parser.add_argument('--cycles', dest='cycles', action='store_true')
    
    add_subparsers(parser, parent_parser)

    args = parser.parse_args()

    run_cli_function(**args.__dict__)


if __name__ == "__main__":
    main()
