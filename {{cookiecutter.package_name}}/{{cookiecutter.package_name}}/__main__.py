"""CLI entry point for the {{cookiecutter.package_name}} package.

Exposed via ``[project.scripts]`` in ``pyproject.toml``::

    {{cookiecutter.package_name}} = "{{cookiecutter.package_name}}.__main__:cli"

Usage::

    {{cookiecutter.package_name}} <skill>::<inputs> [key=value ...]
    {{cookiecutter.package_name}} --list
"""

from robot_agent.cli import main


def cli() -> int:
    return main(robot_pkg='{{cookiecutter.package_name}}')


if __name__ == '__main__':
    raise SystemExit(cli())
