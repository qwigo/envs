import re
from setuptools import setup, find_packages


def get_version():
    with open('envs/__init__.py') as f:
        match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if match:
            return match.group(1)
    raise RuntimeError('Cannot find __version__ in envs/__init__.py')


def parse_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


setup(
    name='envs',
    description='Easy access of environment variables from Python with support for strings, booleans, list, tuples, and dicts.',
    url='https://github.com/bjinwright/envs',
    author='Brian Jinwright',
    license='Apache License 2.0',
    keywords='environment variables',
    python_requires='>=3.6',
    extras_require={
        'cli': parse_requirements('requirements_cli.txt'),
    },
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    version=get_version(),
    entry_points='''
        [console_scripts]
        envs=envs.cli:envs
        ''',
)
