# {{cookiecutter.project_name}} — Claude notes

Generated from [`robot_template`](../robot_template) on top of
[`robot_agent`](../robot_agent).

## Three execution modes — one bootstrap

| Mode | Entry | Notes |
|---|---|---|
| UI / HTTP | `make run` → `uvicorn {{cookiecutter.package_name}}.main:app` | Port `{{cookiecutter.default_port}}`. FastAPI lifespan wraps `bootstrap()`. |
| CLI | `{{cookiecutter.package_name}} <skill>[::<inputs>] [k=v ...]` | Registered as console-script via `[project.scripts]`. |
| Python API | `from {{cookiecutter.package_name}}.skills.<file> import <skill>` | `@skill_entry` wrapper triggers `bootstrap()` lazily. |

All three call `robot_agent.runtime.bootstrap('{{cookiecutter.package_name}}', ...)`.
Idempotent. One process = one mode.

## Layout (Claude-relevant)

```
{{cookiecutter.package_name}}/
├── main.py                        # UI entry: create_app(pkg, data_dir)
├── __main__.py                    # CLI entry: from robot_agent.cli import main
├── skills/__init__.py             # auto_wrap_skills(SKILL_CONFIGS, pkg=...)
├── skills/<skill>.py              # def <skill>(node, **params) -> dict
├── configs/skills_config.py       # SKILL_CONFIGS: skill_name -> (module, func)
├── configs/tasks.py               # ARM_CONFIGS / ENV / LIFT_CONFIGS overrides
└── data/                          # connections.json, skills.json, logs/
```

## Skill contract

```python
def my_skill(node, **params) -> dict:
    # node = pyconnect.ros.custom_node.CustomNode (spinning).
    # params = caller-supplied kwargs (HTTP body / CLI k=v / Python kwargs).
    return {'isdone': True, ...}     # contract: must return dict with 'isdone'.
```

Inter-skill calls always pass `node=` through; the wrapper only auto-injects
when caller has not supplied one.

## Adding a skill

1. `<{{cookiecutter.package_name}}>/skills/<new_skill>.py` — write the function.
2. Add to `<{{cookiecutter.package_name}}>/configs/skills_config.py`:
   ```python
   SKILL_CONFIGS['<new_skill>'] = (f'{_PKG}.<new_skill>', '<new_skill>')
   ```
3. For UI: `POST /skills/reload` or restart `make run`.
   For CLI / Python: next process picks it up automatically.

Or use the scaffold targets:

```bash
make skill-generic SKILL=wave
make skill-detect  SKILL=find_apple
```

## Devices

Registered in `data/connections.json` and reloaded by
`DeviceManager.load_saved()` during `bootstrap()`.
CLI / Python modes load devices **synchronously** so first skill call has
them ready. UI mode loads in a background thread for snappy startup.

## Debug

```bash
make doctor                                  # env + import smoke test
make cli ARGS="--list"                       # show registered skills (no server)
ROBOT_AGENT_DEBUG_RESPONSE=1 make run        # full traceback in skill error dicts
ROBOT_AGENT_LOG_LEVEL=DEBUG make run
```

Logs: `data/logs/{{cookiecutter.package_name}}.log` (rotating).
