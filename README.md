# robot_template — Bootstrap a New Robot in 30 Seconds

> Cookiecutter that emits a dashboard-ready, CLI-ready, Python-API-ready
> ROS2 robot package. Same contract as the production
> [`kcare_robot`](../kcare_robot) — minus its hardware-specific quirks.

```bash
pip install cookiecutter
cookiecutter https://github.com/mtbui2010/robot_template
cd <package_name>
make install && make run
# → uvicorn on :8001, ready to drive from https://robot.aistations.org
```

---

## What you get

A complete package that drops straight into the
[`robot_agent`](../robot_agent) runtime and is immediately controllable from
the [`robotapp`](../robotapp) dashboard.

```
<package_name>/
├── Makefile                  install · run · cli · doctor · terminate · help
├── pyproject.toml            registers [project.scripts] <package_name> CLI
├── README.md                 tailored quickstart
├── .gitignore
├── .vscode/launch.json       F5 → debug uvicorn
└── <package_name>/
    ├── main.py               create_app('<package_name>', data_dir=...)
    ├── __main__.py           CLI entry → robot_agent.cli:main
    ├── configs/
    │   ├── skills_config.py  SKILL_CONFIGS — auto-populated from your skill list
    │   ├── tasks.py          ARM_CONFIGS, ENV stubs
    │   └── guide.py          planner guide stub
    ├── skills/
    │   ├── __init__.py       auto_wrap_skills(SKILL_CONFIGS, pkg='<package_name>')
    │   └── <skill>.py        one runnable mock per skill (find/pick/place
    │                         get domain-aware templates; others get generic stubs)
    └── template_skills/      three reference patterns, NOT auto-registered
        ├── grip_pyconnect.py     Pattern 1 — pyconnect NodeAgent (90 % of cases)
        ├── grip_pure_ros2.py     Pattern 2 — raw rclpy + custom QoS / feedback
        └── grip_external.py     Pattern 3 — separate process / language / host
```

All three execution modes work out of the box:

```bash
make run                                    # UI / HTTP — port 8001
<package_name> find::apple                  # CLI (registered as console-script)
python -c "from <package_name>.skills.find import find; print(find('apple'))"
```

---

## Prompts

| Prompt                | Default                          | Purpose                                                          |
|-----------------------|----------------------------------|------------------------------------------------------------------|
| `project_name`        | `My Robot`                       | Human-readable name — appears in README and FastAPI title        |
| `package_name`        | derived from `project_name`      | Importable Python package (lowercase, underscores)               |
| `description`         | `A robot agent ...`              | One-line summary for `pyproject.toml`                            |
| `author`              | `Your Name`                      | `pyproject.toml` author metadata                                 |
| `version`             | `0.1.0`                          | Initial package version                                          |
| `skills`              | `find,pick,place`                | Comma-separated skill names — one file generated per skill       |
| `default_port`        | `8001`                           | Default port in the Makefile                                     |
| `robot_agent_relpath` | `../robot_agent`                 | Editable-install path for `robot_agent`                          |
| `pyconnect_relpath`   | `../pyconnect`                   | Editable-install path for `pyconnect`                            |

The generator's post-hook
([`hooks/post_gen_project.py`](hooks/post_gen_project.py)) parses the skill
list and emits:
- one runnable skill file per name in `<package_name>/skills/`
  (with domain-aware templates for `find`, `pick`, `place`; generic stubs for
  anything else),
- a `SKILL_CONFIGS` dict in `configs/skills_config.py` already wired up,
- a Makefile with your chosen port pinned.

---

## Why scaffold instead of fork `kcare_robot`?

`kcare_robot` is a real implementation — 23 skills tuned for a specific KAAIR
arm, Femto Bolt head, and D405 wrist camera. Forking it means inheriting (and
then pruning) those quirks. The template gives you a **clean baseline** that
honours the same contract with `robot_agent`:

```python
# Everything robot_agent needs from your package:
SKILL_CONFIGS: dict[str, tuple[str, str]]   # name -> (module_path, func_name)
```

That's it. One dict, one convention, infinite robots.

---

## After generation

```bash
cd <package_name>
make install      # editable-installs robot_agent, pyconnect, this package
make doctor       # pre-flight: ROS2 sourced? skills importable? data dir writable?
make run          # uvicorn <package_name>.main:app --port <default_port>
```

### Drive it from the dashboard

Open <https://robot.aistations.org>, click **Guide** in the top right, paste
`http://<this-host>:<default_port>`, click Connect. Every skill in your
`SKILL_CONFIGS` shows up in the skill picker. Cameras and ROS devices register
through the same UI.

### Add a skill

```python
# <package_name>/skills/wave.py
def wave(node, **params) -> dict:
    arm = node.agents['movej']
    arm.send({'joints': [0, -1.2, 1.5, 0, 0.8, 0]})
    return {'isdone': True, 'msg': 'waved'}
```

```python
# <package_name>/configs/skills_config.py
SKILL_CONFIGS = {
    ...
    'wave': (f'{_PKG}.wave', 'wave'),
}
```

Then `curl -X POST http://localhost:8001/skills/reload` — no restart.

For external skills (a GPU vision service, a non-Python module, anything
separately processed), register them at runtime:

```bash
curl -X POST http://localhost:8001/skills \
  -d '{"name":"detect_face","type":"external",
       "url":"http://gpu-box:9000/detect","timeout":15}'
```

---

## Related

- [`robot_agent`](../robot_agent) — the runtime your scaffold plugs into
  (FastAPI, 30+ endpoints, WebSocket camera + plan streaming)
- [`kcare_robot`](../kcare_robot) — full production example (23 skills,
  RealSense D405, Femto Bolt, Nav2, head-to-base calibration)
- [`robotapp`](../robotapp) — Next.js 14 ops dashboard
  (<https://robot.aistations.org>)
