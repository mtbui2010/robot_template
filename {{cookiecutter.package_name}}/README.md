# {{cookiecutter.project_name}}

{{cookiecutter.description}}

Built on [`robot_agent`](../robot_agent). Generated from the
[`robot_template`](../robot_template) cookiecutter.

## Quickstart

```bash
make install      # editable-install pyconnect, robot_agent, this package
make doctor      # pre-flight: ROS2, skill imports, data dir
make run         # UI / HTTP: uvicorn on port {{cookiecutter.default_port}}
```

`make help` lists all targets.

## Three execution modes

| Mode | Use case | Boots ROS | Needs `make run` |
|---|---|---|---|
| **UI / HTTP** (`make run`) | Dashboard, REST clients, multi-user | uvicorn start | yes (this IS the server) |
| **CLI** (`{{cookiecutter.package_name}} find::apple`) | One-off ops, shell scripting | once per call | no |
| **Python API** (`from {{cookiecutter.package_name}}.skills.X import fn`) | Scripts, notebooks, tests | lazy, on first call | no |

All three share the same `bootstrap()` from
[`robot_agent.runtime`](../robot_agent/robot_agent/runtime.py); only the
outer shell differs. **One mode at a time** — two clients steering the
same robot is unsafe.

### CLI

```bash
{{cookiecutter.package_name}} find::apple
{{cookiecutter.package_name}} find::apple count=3 verbose=true
{{cookiecutter.package_name}} --list
{{cookiecutter.package_name}} --help

# Or via Makefile (auto-sources ROS):
make cli ARGS="find::apple"
```

`name::value` → `inputs=value`; additional `key=value` tokens are coerced
(bool / int / float / JSON). Output is JSON on stdout; exit code 0 iff
`isdone: true`.

### Python API

```python
from {{cookiecutter.package_name}}.skills.find import find
from {{cookiecutter.package_name}}.skills.pick import pick

ret = find(inputs='apple')        # first call: ~3s bootstrap
if ret['isdone']:
    pick(inputs='apple')          # reuses the same ROS node

find('apple')                     # short form — first positional → inputs=
```

This works because
[`{{cookiecutter.package_name}}/skills/__init__.py`](./{{cookiecutter.package_name}}/skills/__init__.py)
calls `auto_wrap_skills(SKILL_CONFIGS, pkg='{{cookiecutter.package_name}}')`,
which decorates each public skill so missing `node=` triggers
`bootstrap('{{cookiecutter.package_name}}')` (idempotent).

## Layout

```
{{cookiecutter.package_name}}/
├── Makefile                       # install / run / cli / terminate / doctor / test
├── pyproject.toml                 # editable-installable; [project.scripts]
│                                  #   {{cookiecutter.package_name}} = "{{cookiecutter.package_name}}.__main__:cli"
├── .vscode/launch.json            # F5 debug in VSCode
└── {{cookiecutter.package_name}}/
    ├── main.py                    # UI entry: create_app(pkg, data_dir)
    ├── __main__.py                # CLI entry: from robot_agent.cli import main
    ├── data/                      # runtime state (not committed)
    │   ├── connections.json       # devices registry
    │   ├── skills.json            # skill registry
    │   ├── skill_configs_override.json
    │   └── logs/
    ├── configs/
    │   ├── skills_config.py       # SKILL_CONFIGS: maps skill name → module:func
    │   ├── tasks.py               # optional runtime values (ENV, ARM_CONFIGS, ...)
    │   └── guide.py               # optional planner guide
    ├── skills/
    │   ├── __init__.py            # auto_wrap_skills(SKILL_CONFIGS, pkg=...)
    │   └── <skill>.py             # one file per skill
    └── template_skills/           # reference implementations (external / pure-ROS2)
```

## Adding a new skill

1. Create `{{cookiecutter.package_name}}/skills/<my_skill>.py`:
   ```python
   from robot_agent.skills import log_data

   def my_skill(node, **params) -> dict:
       log_data({'msg': f'my_skill called with {params}'})
       return {'isdone': True, 'msg': 'ok'}
   ```
2. Register it in `{{cookiecutter.package_name}}/configs/skills_config.py`:
   ```python
   SKILL_CONFIGS['my_skill'] = (f'{_PKG}.my_skill', 'my_skill')
   ```
3. `POST /skills/reload` (or restart) — the agent picks it up.

## Skill contract

```python
def skill(node, **params) -> dict:
    """
    Args:
        node:    live pyconnect.ros.custom_node.CustomNode (subclass of rclpy.node.Node),
                 already spinning in a MultiThreadedExecutor.
        params:  JSON body of POST /skill/<name> unpacked as kwargs.

    Returns:
        dict with at least 'isdone': bool. All other keys are free-form
        and may be inspected by the planner / displayed in the UI.

    Inside the skill, access registered devices via:
        node.agents['<agent_name>'].send(...)     # services / publishers
        node.agents['<agent_name>'].get()         # subscribers (latest sample)
    """
```

See [`template_skills/`](./{{cookiecutter.package_name}}/template_skills) for
three reference patterns: external (HTTP), pure-ROS2, and pyconnect-wrapped.

## Connecting from the UI

After `make run` the agent listens on
`http://<host>:{{cookiecutter.default_port}}`. Open the hosted dashboard at
<https://robot.aistations.org> and click the **Guide** button in the
top-right corner — it walks you through registering this agent's URL,
connecting an LLM, ROS endpoints, cameras, and sending your first command.

(Self-hosting the dashboard: see [`robotapp`](../robotapp).)
