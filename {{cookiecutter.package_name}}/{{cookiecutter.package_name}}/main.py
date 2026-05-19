"""Entry point for the {{cookiecutter.package_name}} agent.

Run with:

    cd {{cookiecutter.package_name}}/
    make run                # port {{cookiecutter.default_port}}
    make run PORT=9999      # alternative port (for running multiple robots)

Or directly with uvicorn:

    uvicorn {{cookiecutter.package_name}}.main:app --host 0.0.0.0 --port {{cookiecutter.default_port}} --reload

VSCode debug: open this folder in VSCode and hit F5 — .vscode/launch.json
runs the same uvicorn command with breakpoints active.
"""

from pathlib import Path

from robot_agent import create_app

DATA_DIR = Path(__file__).parent / 'data'

app = create_app(robot_pkg='{{cookiecutter.package_name}}', data_dir=DATA_DIR)
