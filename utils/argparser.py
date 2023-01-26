import shlex

from argparse import Namespace, ArgumentParser
from typing import Union


class DefaultArguments(ArgumentParser):
    def error(self, message: str):
        raise RuntimeError(message)


class Arguments:
    def __init__(self, posix: bool = False, allow_abbrev: bool = False, **kwargs):
        self.parser = DefaultArguments(allow_abbrev=allow_abbrev, add_help=False, **kwargs)
        self.posix = posix

    def add_argument(self, *inputs, **kwargs) -> None:
        """ Shortcut to argparse.add_argument """
        self.parser.add_argument(*inputs, **kwargs)

    def parse_args(self, text: str) -> tuple[Union[Namespace, str], bool]:
        """ Shortcut to argparse.parse_args with shlex implemented """
        try:
            args = self.parser.parse_args(
                shlex.split(text if text else "", posix=self.posix)
            )
        except Exception as e:
            return (f"ArgumentError: {e}", False)
        return (args, True)
