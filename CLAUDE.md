# robot_template — Claude notes

Cookiecutter scaffold that emits a new robot package hooked into
[`robot_agent`](../robot_agent). Every generated project gets three
execution modes for free.

## What gets generated

After `cookiecutter robot_template/`, the new project ships with:

| File | Purpose |
|---|---|
| `<pkg>/main.py` | UI entry → `create_app('<pkg>', data_dir)` |
| `<pkg>/__main__.py` | CLI entry → `from robot_agent.cli import main` |
| `<pkg>/skills/__init__.py` | Auto-wraps skills via `auto_wrap_skills(SKILL_CONFIGS, pkg='<pkg>')` |
| `<pkg>/configs/skills_config.py` | `SKILL_CONFIGS` dict (one entry per skill from cookiecutter prompt) |
| `pyproject.toml` | Registers `[project.scripts] <pkg> = "<pkg>.__main__:cli"` |
| `Makefile` | `install`, `run` (UI), `cli` (CLI), `doctor`, `skill-generic`, `skill-detect` |

All three modes (UI / CLI / Python API) work out of the box without further
edits. User just adds skill bodies and registers them in `skills_config.py`.

## Three modes — single bootstrap

| Mode | Entry | When `bootstrap()` runs |
|---|---|---|
| UI / HTTP | `make run` | uvicorn startup (lifespan) |
| CLI | `<pkg> find::apple` | At `main()` call |
| Python API | `from <pkg>.skills.X import fn; fn(...)` | First wrapped-skill call |

All three go through `robot_agent.runtime.bootstrap('<pkg>', ...)` which
is idempotent. One process = one mode.

## Files in this template

```
robot_template/
├── cookiecutter.json                       # prompts: project_name, skills, port, ...
├── hooks/post_gen_project.py               # generates <pkg>/skills/*.py + skills_config.py
├── README.md
└── {{cookiecutter.package_name}}/          # ← rendered into <new_pkg>/
    ├── Makefile
    ├── pyproject.toml                      # [project.scripts] for CLI
    ├── README.md
    └── {{cookiecutter.package_name}}/
        ├── __init__.py
        ├── main.py                         # UI shim
        ├── __main__.py                     # CLI shim
        ├── skills/__init__.py              # auto_wrap_skills(...)
        ├── configs/{skills_config,tasks,guide}.py
        └── template_skills/                # reference patterns (NOT auto-registered)
```

The `post_gen_project.py` hook reads the comma-separated `skills`
cookiecutter answer and creates one mock file per skill under
`<pkg>/skills/` plus the `SKILL_CONFIGS` registry — both ready to edit.

## When editing this template

- Bumping `robot_agent` API (e.g. renaming `bootstrap` or `auto_wrap_skills`):
  update the shims in `{{cookiecutter.package_name}}/{{cookiecutter.package_name}}/__main__.py`
  and `skills/__init__.py` in lockstep.
- Adding a new cookiecutter prompt: edit `cookiecutter.json` AND any
  templates that reference it.
- Mock skill body changes: edit
  [`hooks/post_gen_project.py`](hooks/post_gen_project.py) — that's where
  the `find` / `pick` / `place` / generic templates live.

## Related

- [robot_agent](../robot_agent) — runtime core.
- [kcare_robot](../kcare_robot) — reference implementation. Mirror layout
  and conventions when expanding this template.
