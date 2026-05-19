# {{cookiecutter.project_name}}

{{cookiecutter.description}}

Built on [`robot_agent`](../robot_agent). Generated from the
[`robot_template`](../robot_template) cookiecutter.

## Quickstart

```bash
make install      # editable-install pyconnect, robot_agent, this package
make doctor      # pre-flight: ROS2, skill imports, data dir
make run         # uvicorn on port {{cookiecutter.default_port}}
```

`make help` lists all targets.

## Layout

```
{{cookiecutter.package_name}}/
├── Makefile                       # install / run / terminate / doctor / test
├── pyproject.toml                 # editable-installable
├── .vscode/launch.json            # F5 debug in VSCode
└── {{cookiecutter.package_name}}/
    ├── main.py                    # uvicorn entry: create_app(pkg, data_dir)
    ├── data/                      # runtime state (not committed)
    │   ├── connections.json       # devices registry
    │   ├── skills.json            # skill registry
    │   ├── skill_configs_override.json
    │   └── logs/
    ├── configs/
    │   ├── skills_config.py       # SKILL_CONFIGS: maps skill name → module:func
    │   ├── tasks.py               # optional runtime values (ENV, ARM_CONFIGS, ...)
    │   └── guide.py               # optional planner guide
    ├── skills/                    # one file per skill
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

The agent listens on `http://<host>:{{cookiecutter.default_port}}`. In the
[`robotapp`](../robotapp) frontend's **DevicePanel**, add this robot under
the Robot Agent picker (give it a name + URL), then click Connect.
