import os

import click
import jinja2
from terminaltables import AsciiTable

from envs.exceptions import EnvsValueException
from . import env
from . import ARGUMENTS, ENVS_RESULT_FILENAME
from .util import convert_module, import_mod, list_envs_module

SETTINGS_TEMPLATE = jinja2.Environment(loader=jinja2.PackageLoader(
    'envs', 'templates')).get_template('settings.jinja2')


@click.group()
def envs():
    pass


@envs.command(ARGUMENTS.CONVERT_SETTINGS, help='Converts an existing settings file so it uses envs.')
@click.option('--settings-file', prompt=True,
              help='Settings Module? ex. settings or yourapp.settings')
def convert_settings(settings_file):
    attr_list = convert_module(import_mod(settings_file))
    template = SETTINGS_TEMPLATE.render(attr_list=attr_list)
    new_settings_filename = input(
        'What should we name this new settings file? (DO NOT NAME IT THE SAME AS THE ORIGINAL BECAUSE THERE ARE NO IMPORTS): ')
    if not new_settings_filename:
        raise ValueError('Settings filename is required.')
    with open(new_settings_filename, 'w') as f:
        f.write(template)
    click.echo(click.style(f'Your new settings file {new_settings_filename}', fg='green'))


@envs.command(ARGUMENTS.LIST_ENVS, help='Shows a list of env instances set in a settings file.')
@click.option('--settings-file', prompt=True,
              help='Settings Module? ex. settings or yourapp.settings')
@click.option('--keep-result', prompt=True, help=f'Keep the result file ({ENVS_RESULT_FILENAME})?', default=False)
def list_envs(settings_file, keep_result):
    envs_result = list_envs_module(settings_file)
    table_data = [
        ['Env Var', 'Var Type', 'Has Default', 'Environment Value'],
    ]
    table_data.extend(
        [[row.get('key'), row.get('var_type'), bool(row.get('default')), row.get('value')] for row in envs_result])
    try:
        click.echo(AsciiTable(table_data).table)
    finally:
        if not keep_result:
            os.remove(ENVS_RESULT_FILENAME)


@envs.command(ARGUMENTS.CHECK_ENVS, help='Make sure that the defined envs with no default value have a value set in the environment.')
@click.option('--settings-file', prompt=True,
              help='Settings Module? ex. settings or yourapp.settings')
def check_envs(settings_file):
    envs_result = list_envs_module(settings_file)
    try:
        for row in envs_result:
            value = env(row.get('key'), row.get('default'), var_type=row.get('var_type'))
            if value is None:
                raise EnvsValueException(f'{row.get("key")}: Environment Variable Not Set')
    finally:
        if os.path.exists(ENVS_RESULT_FILENAME):
            os.remove(ENVS_RESULT_FILENAME)
