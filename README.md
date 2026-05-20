# robot_template

[Cookiecutter](https://cookiecutter.readthedocs.io/) template for bootstrapping
a new robot package that uses [`robot_agent`](../robot_agent) as its runtime.

## Usage

```bash
pip install cookiecutter
cookiecutter https://github.com/mtbui2010/robot_template
```

Cookiecutter then prompts:

| Prompt                | Default                          | Meaning                                                          |
|-----------------------|----------------------------------|------------------------------------------------------------------|
| `project_name`        | `My Robot`                       | Human-readable name; appears in README / FastAPI title.          |
| `package_name`        | derived from `project_name`      | Importable Python package (lowercase, underscores).              |
| `description`         | `A robot agent ...`              | One-line summary for pyproject.toml.                             |
| `author`              | `Your Name`                      | pyproject.toml `authors`.                                        |
| `version`             | `0.1.0`                          | Initial package version.                                         |
| `skills`              | `find,pick,place`                | Comma-separated skill names — one mock file generated per skill. |
| `default_port`        | `8001`                           | Default `PORT` in Makefile.                                      |
| `robot_agent_relpath` | `../robot_agent`                 | Relative path to robot_agent (for `pip install -e`).             |
| `pyconnect_relpath`   | `../pyconnect`                   | Relative path to pyconnect (for `pip install -e`).               |

## What you get

After running the cookiecutter, you'll have a directory named after your
`package_name` containing:

```
<package_name>/
├── Makefile                  # install / run / cli / terminate / doctor / help
├── README.md                 # tailored quickstart for the new robot
├── pyproject.toml            # editable-installable package; registers
│                             #   [project.scripts] <package_name> = "<package_name>.__main__:cli"
├── .gitignore
├── .vscode/launch.json       # F5 debug uvicorn from VSCode
└── <package_name>/
    ├── __init__.py
    ├── main.py               # UI entry: create_app('<package_name>', data_dir=<here>/data)
    ├── __main__.py           # CLI entry: from robot_agent.cli import main
    ├── data/                 # runtime state (connections.json, logs/, ...)
    ├── configs/
    │   ├── skills_config.py  # SKILL_CONFIGS — populated from your skills list
    │   ├── tasks.py          # optional runtime config (ARM_CONFIGS, ENV, ...)
    │   └── guide.py          # optional planner guide stub
    ├── skills/
    │   ├── __init__.py       # auto_wrap_skills(SKILL_CONFIGS, pkg='<package_name>')
    │   └── <skill>.py        # one mock implementation per skill, ready to edit
    └── template_skills/      # reference implementations (external / pure-ROS2)
```

## After generation

```bash
cd <package_name>
make install      # pip install -e robot_agent, pyconnect, then this package
make doctor      # pre-flight: ROS2, imports, data dir
make run         # UI / HTTP: uvicorn <package_name>.main:app --port <default_port>
```

You also get two non-UI ways to drive the robot, ready out of the box:

```bash
# CLI (registered as console-script via [project.scripts])
<package_name> find::apple
<package_name> --list
make cli ARGS="find::apple"             # convenience wrapper that sources ROS

# Python API
python -c "from <package_name>.skills.find import find; print(find('apple'))"
```

All three modes share the same `bootstrap()` core from
[`robot_agent.runtime`](../robot_agent/robot_agent/runtime.py) — only the
outer shell differs. Run **one mode at a time** against a real robot.

## Adding more skills later

Each skill = one file under `<package_name>/skills/<skill>.py` plus one line in
`<package_name>/configs/skills_config.py`. Re-run the cookiecutter is **not**
necessary — just create the file and edit `SKILL_CONFIGS`.

## Why a template instead of forking kcare_robot?

`kcare_robot` is a full implementation with hardware-specific quirks. Forking
it forces a new robot to inherit (and then prune) those quirks. This template
gives a clean baseline that follows the same contract with `robot_agent`.
