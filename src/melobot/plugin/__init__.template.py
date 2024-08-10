from os import listdir as _VAR1
from pathlib import Path as _VAR2

from melobot.bot import get_bot as _VAR3
from melobot.plugin.load import plugin_get_attr as _VAR4

_VAR5 = _VAR2(__file__).parent
_VAR6 = set(fname.split(".")[0] for fname in _VAR1(_VAR5))


def __getattr__(name):
    if name in _VAR6:
        raise AttributeError
    else:
        return _VAR4(_VAR3, _VAR5.parts[-1], name)
