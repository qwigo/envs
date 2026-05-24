import ast
import json
import os
import sys
from decimal import Decimal
from typing import Any, Optional

from .exceptions import EnvsValueException

__version__ = '1.3'


class CLIArguments:
    LIST_ENVS = 'list-envs'
    CHECK_ENVS = 'check-envs'
    CONVERT_SETTINGS = 'convert-settings'


ARGUMENTS = CLIArguments()

# Per-process filename prevents races between concurrent test runs / processes.
ENVS_RESULT_FILENAME = f'.envs_result_{os.getpid()}'


def validate_boolean(value: Any) -> bool:
    true_vals = ('True', 'true', 1, '1')
    false_vals = ('False', 'false', 0, '0')
    if value in true_vals:
        return True
    if value in false_vals:
        return False
    raise ValueError('This value is not a boolean value.')


class Env:
    valid_types = {
        'string': None,
        'boolean': validate_boolean,
        'list': list,
        'tuple': tuple,
        'integer': int,
        'float': float,
        'dict': dict,
        'decimal': Decimal,
    }

    def __call__(
        self,
        key: str,
        default: Optional[Any] = None,
        var_type: str = 'string',
        allow_none: bool = True,
    ) -> Any:
        if ARGUMENTS.LIST_ENVS in sys.argv or ARGUMENTS.CHECK_ENVS in sys.argv:
            with open(ENVS_RESULT_FILENAME, 'a') as f:
                json.dump({'key': key, 'var_type': var_type, 'default': default, 'value': os.getenv(key)}, f)
                f.write(',')
        value = os.getenv(key, default)
        if var_type not in self.valid_types:
            raise ValueError(
                f'The var_type argument should be one of the following {",".join(self.valid_types)}')
        if value is None:
            if not allow_none:
                raise EnvsValueException(f'{key}: Environment Variable Not Set')
            return value
        return self.validate_type(value, self.valid_types[var_type], key)

    def validate_type(self, value: Any, klass: Any, key: str) -> Any:
        if not klass:
            return value
        if klass in (validate_boolean, Decimal):
            return klass(value)
        if isinstance(value, klass):
            return value
        return klass(ast.literal_eval(value))


env = Env()
