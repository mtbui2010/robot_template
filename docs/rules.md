# robot_template rules (full text)

The short form is in [../CLAUDE.md](../CLAUDE.md); the numbers match.

1. **Bumping the `robot_agent` API** (e.g. renaming `bootstrap` or
   `auto_wrap_skills`): update the shims in
   `{{cookiecutter.package_name}}/{{cookiecutter.package_name}}/__main__.py` and
   `skills/__init__.py` in lockstep. Why: every generated project inherits the
   shims; a stale shim breaks all new robots.
2. **Adding a new cookiecutter prompt**: edit `cookiecutter.json` AND any
   templates that reference it. Why: an unrendered `{{ cookiecutter.x }}` fails
   generation.
3. **Mock skill body changes**: edit
   [hooks/post_gen_project.py](../hooks/post_gen_project.py); that is where the
   `find` / `pick` / `place` / generic templates live.
4. **Mirror kcare_robot's layout and conventions** when expanding this template
   ([architecture.md](architecture.md#related)).
5. **CLAUDE.md stays short**: rules and links only; details go in `docs/*.md`.
