import os
import sys
import unittest
from decimal import Decimal
import json
from unittest.mock import patch
from unittest import mock

from envs import env, ENVS_RESULT_FILENAME
from envs.exceptions import EnvsValueException


_SETUP_KEYS = [
    'VALID_INTEGER', 'INVALID_INTEGER', 'VALID_STRING',
    'VALID_BOOLEAN', 'VALID_BOOLEAN_FALSE', 'INVALID_BOOLEAN',
    'VALID_LIST', 'INVALID_LIST', 'VALID_TUPLE', 'INVALID_TUPLE',
    'VALID_DICT', 'INVALID_DICT', 'VALID_FLOAT', 'INVALID_FLOAT',
    'VALID_DECIMAL', 'INVALID_DECIMAL', 'EMPTY',
]


class EnvTestCase(unittest.TestCase):
    def setUp(self):
        os.environ.setdefault('VALID_INTEGER', '1')
        os.environ.setdefault('INVALID_INTEGER', '["seven"]')
        os.environ.setdefault('VALID_STRING', 'seven')
        os.environ.setdefault('VALID_BOOLEAN', 'True')
        os.environ.setdefault('VALID_BOOLEAN_FALSE', 'false')
        os.environ.setdefault('INVALID_BOOLEAN', 'seven')
        os.environ.setdefault('VALID_LIST', "['1','2','3']")
        os.environ.setdefault('INVALID_LIST', "1")
        os.environ.setdefault('VALID_TUPLE', "('True','FALSE')")
        os.environ.setdefault('INVALID_TUPLE', '1')
        os.environ.setdefault('VALID_DICT', "{'first_name':'Suge'}")
        os.environ.setdefault('INVALID_DICT', 'Aaron Rogers')
        os.environ.setdefault('VALID_FLOAT', "5.0")
        os.environ.setdefault('INVALID_FLOAT', '[5.0]')
        os.environ.setdefault('VALID_DECIMAL', "2.39")
        os.environ.setdefault('INVALID_DECIMAL', "FOOBAR")

    def tearDown(self):
        for key in _SETUP_KEYS + ['ZERO_COUNT', 'FALSY_BOOL']:
            os.environ.pop(key, None)
        if os.path.exists(ENVS_RESULT_FILENAME):
            os.remove(ENVS_RESULT_FILENAME)

    # --- existing tests (vm removed) ---

    def test_integer_valid(self):
        self.assertEqual(1, env('VALID_INTEGER', var_type='integer'))

    def test_integer_invalid(self):
        with self.assertRaises(TypeError):
            env('INVALID_INTEGER', var_type='integer')

    def test_wrong_var_type(self):
        with self.assertRaises(ValueError):
            env('INVALID_INTEGER', var_type='set')

    def test_string_valid(self):
        self.assertEqual('seven', env('VALID_STRING'))

    def test_boolean_valid(self):
        self.assertEqual(True, env('VALID_BOOLEAN', var_type='boolean'))

    def test_boolean_valid_false(self):
        self.assertEqual(False, env('VALID_BOOLEAN_FALSE', var_type='boolean'))

    def test_boolean_invalid(self):
        with self.assertRaises(ValueError):
            env('INVALID_BOOLEAN', var_type='boolean')

    def test_list_valid(self):
        self.assertEqual(['1', '2', '3'], env('VALID_LIST', var_type='list'))

    def test_list_invalid(self):
        with self.assertRaises(TypeError):
            env('INVALID_LIST', var_type='list')

    def test_tuple_valid(self):
        self.assertEqual(('True', 'FALSE'), env('VALID_TUPLE', var_type='tuple'))

    def test_tuple_invalid(self):
        with self.assertRaises(TypeError):
            env('INVALID_TUPLE', var_type='tuple')

    def test_dict_valid(self):
        self.assertEqual({'first_name': 'Suge'}, env('VALID_DICT', var_type='dict'))

    def test_dict_invalid(self):
        with self.assertRaises(SyntaxError):
            env('INVALID_DICT', var_type='dict')

    def test_float_valid(self):
        self.assertEqual(5.0, env('VALID_FLOAT', var_type='float'))

    def test_float_invalid(self):
        with self.assertRaises(TypeError):
            env('INVALID_FLOAT', var_type='float')

    def test_decimal_valid(self):
        self.assertEqual(Decimal('2.39'), env('VALID_DECIMAL', var_type='decimal'))

    def test_decimal_invalid(self):
        with self.assertRaises(ArithmeticError):
            env('INVALID_DECIMAL', var_type='decimal')

    def test_defaults(self):
        self.assertEqual(env('HELLO', 5, var_type='integer'), 5)
        self.assertEqual(env('HELLO', 5.0, var_type='float'), 5.0)
        self.assertEqual(env('HELLO', [], var_type='list'), [])
        self.assertEqual(env('HELLO', {}, var_type='dict'), {})
        self.assertEqual(env('HELLO', (), var_type='tuple'), ())
        self.assertEqual(env('HELLO', 'world'), 'world')
        self.assertEqual(env('HELLO', False, var_type='boolean'), False)
        self.assertEqual(env('HELLO', 'False', var_type='boolean'), False)
        self.assertEqual(env('HELLO', 'true', var_type='boolean'), True)
        self.assertEqual(env('HELLO', Decimal('3.14'), var_type='decimal'), Decimal('3.14'))

    def test_without_defaults_allow_none(self):
        self.assertEqual(env('HELLO'), None)
        self.assertEqual(env('HELLO', var_type='integer'), None)
        self.assertEqual(env('HELLO', var_type='float'), None)
        self.assertEqual(env('HELLO', var_type='list'), None)

    def test_without_defaults_disallow_none(self):
        with self.assertRaises(EnvsValueException):
            env('HELLO', allow_none=False)
        with self.assertRaises(EnvsValueException):
            env('HELLO', var_type='integer', allow_none=False)
        with self.assertRaises(EnvsValueException):
            env('HELLO', var_type='float', allow_none=False)
        with self.assertRaises(EnvsValueException):
            env('HELLO', var_type='list', allow_none=False)

    def test_empty_values(self):
        os.environ.setdefault('EMPTY', '')
        self.assertEqual(env('EMPTY'), '')
        with self.assertRaises(SyntaxError):
            env('EMPTY', var_type='integer')
        with self.assertRaises(SyntaxError):
            env('EMPTY', var_type='float')
        with self.assertRaises(SyntaxError):
            env('EMPTY', var_type='list')
        with self.assertRaises(SyntaxError):
            env('EMPTY', var_type='dict')
        with self.assertRaises(SyntaxError):
            env('EMPTY', var_type='tuple')
        with self.assertRaises(ValueError):
            env('EMPTY', var_type='boolean')
        with self.assertRaises(ArithmeticError):
            env('EMPTY', var_type='decimal')

    # --- n4: package exposes __version__ ---

    def test_version_string(self):
        import envs
        self.assertTrue(hasattr(envs, '__version__'))
        self.assertIsInstance(envs.__version__, str)

    # --- n2: VAR_TYPES is a stable snapshot, not a live dict_keys view ---

    def test_var_types_is_tuple(self):
        from envs.util import VAR_TYPES
        self.assertIsInstance(VAR_TYPES, tuple)

    # --- M1: import_mod must not permanently mutate sys.path on failed import ---

    def test_import_mod_restores_sys_path_on_failure(self):
        from envs.util import import_mod
        original_path = list(sys.path)
        with self.assertRaises(ModuleNotFoundError):
            import_mod('nonexistent_module_xyz_99999')
        self.assertEqual(original_path, sys.path)

    # --- C2: list_envs_module must clean up temp file on import error ---

    def test_list_envs_module_cleans_up_on_error(self):
        from envs.util import list_envs_module
        with self.assertRaises(Exception):
            list_envs_module('nonexistent_module_xyz_99999')
        self.assertFalse(os.path.exists(ENVS_RESULT_FILENAME))

    # --- C1: check_envs must not raise EnvsValueException for falsy-but-set values ---

    @mock.patch('envs.cli.os.remove')
    @mock.patch('envs.cli.list_envs_module')
    def test_check_envs_does_not_raise_for_falsy_integer(self, mock_list, mock_remove):
        from click.testing import CliRunner
        from envs.cli import envs as cli_envs
        mock_list.return_value = [{'key': 'ZERO_COUNT', 'var_type': 'integer', 'default': 0}]
        os.environ['ZERO_COUNT'] = '0'
        runner = CliRunner()
        result = runner.invoke(
            cli_envs,
            ['check-envs', '--settings-file', 'envs.test_settings_falsy'],
        )
        self.assertEqual(result.exit_code, 0)

    # --- M5: check_envs cleans up temp file even when it raises ---

    @mock.patch('envs.cli.list_envs_module')
    def test_check_envs_cleans_up_result_file_on_missing_var(self, mock_list):
        from click.testing import CliRunner
        from envs.cli import envs as cli_envs
        mock_list.return_value = [{'key': 'MISSING_VAR', 'var_type': 'string', 'default': None}]
        os.environ.pop('MISSING_VAR', None)
        with open(ENVS_RESULT_FILENAME, 'w') as f:
            f.write('[]')
        runner = CliRunner()
        runner.invoke(
            cli_envs,
            ['check-envs', '--settings-file', 'envs.test_settings_falsy'],
        )
        self.assertFalse(
            os.path.exists(ENVS_RESULT_FILENAME),
            'temp file should be removed even when check_envs raises',
        )


# --- CLI test for list-envs ---

@mock.patch.object(sys, 'argv', ['list-envs'])
def test_list_envs():
    from click.testing import CliRunner
    from envs.cli import envs as cli_envs

    os.environ.setdefault('DEBUG', 'True')
    runner = CliRunner()
    result = runner.invoke(
        cli_envs,
        ['list-envs', '--settings-file', 'envs.test_settings', '--keep-result', 'True'],
        catch_exceptions=False,
    )

    output_expected = [
        {"default": None, "value": None, "var_type": "string", "key": "DATABASE_URL"},
        {"default": False, "value": "True", "var_type": "boolean", "key": "DEBUG"},
        {"default": [], "value": None, "var_type": "list", "key": "MIDDLEWARE"},
        {},
    ]

    with open(ENVS_RESULT_FILENAME, 'r') as f:
        output_actual = json.load(f)

    os.remove(ENVS_RESULT_FILENAME)
    os.environ.pop('DEBUG', None)

    assert result.exit_code == 0
    assert output_actual == output_expected


if __name__ == '__main__':
    unittest.main()
