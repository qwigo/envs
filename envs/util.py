import ast
import importlib
import json
import os
import sys

from . import Env, ENVS_RESULT_FILENAME

VAR_TYPES = tuple(Env.valid_types.keys())


def import_util(imp: str):
    """Lazily imports a util (class, function, or variable) from a dotted string."""
    mod_name, obj_name = imp.rsplit('.', 1)
    mod = importlib.import_module(mod_name)
    return getattr(mod, obj_name)


def convert_module(module):
    attr_list = []
    for k, v in module.__dict__.items():
        if k.isupper():
            convert = bool(int(input(f'Convert {k}? (1=True,0=False): ')))
            attr_dict = {'name': k, 'convert': convert}
            if convert:
                raw = input(f'Default Value? (default: {v}): ')
                default_val = ast.literal_eval(raw) if raw else v
                attr_dict['default_val'] = default_val

                var_type = input('Variable Type Choices (ex. boolean,string,list,tuple,integer,float,dict): ')
                if var_type not in VAR_TYPES:
                    raise ValueError(f'{var_type} not in {VAR_TYPES}')
                attr_dict['var_type'] = var_type
            attr_list.append(attr_dict)
    return attr_list


def import_mod(module: str):
    try:
        return importlib.import_module(module)
    except ModuleNotFoundError:
        cwd = os.getcwd()
        sys.path.insert(0, cwd)
        try:
            return importlib.import_module(module)
        except ModuleNotFoundError:
            # Restore path only on failure; on success cwd must remain so the
            # imported module can resolve its own relative imports.
            sys.path.remove(cwd)
            raise


def list_envs_module(module: str):
    with open(ENVS_RESULT_FILENAME, 'w') as f:
        f.write('[')
    try:
        import_mod(module)
    except Exception:
        os.remove(ENVS_RESULT_FILENAME)
        raise
    with open(ENVS_RESULT_FILENAME, 'a') as f:
        f.write('{}]')
    with open(ENVS_RESULT_FILENAME, 'r') as f:
        envs_result = json.load(f)
        envs_result.pop()
    return envs_result
