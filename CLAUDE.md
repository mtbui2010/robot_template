# robot_template

Cookiecutter scaffold that emits a new robot package on top of [robot_agent](../robot_agent/CLAUDE.md) (UI, CLI and Python API modes).
Docs index: [docs/README.md](docs/README.md). Full rules: [docs/rules.md](docs/rules.md).

## Rules

1. When the robot_agent API changes, update the `__main__.py` and `skills/__init__.py` shims in lockstep.
2. When adding a cookiecutter prompt, edit `cookiecutter.json` and every template that uses it.
3. Change mock skill bodies only in `hooks/post_gen_project.py`.
4. Mirror kcare_robot's layout and conventions when expanding the template.
5. Keep this file short: one-line rules and links; details go in `docs/*.md`.

## Test

`cookiecutter --no-input . -o /tmp/rt_out` then `check_manifest --strict`; see [docs/testing.md](docs/testing.md).

## Docs

- [docs/architecture.md](docs/architecture.md): generated files, modes, template layout
- [docs/testing.md](docs/testing.md): how to check a generated project
