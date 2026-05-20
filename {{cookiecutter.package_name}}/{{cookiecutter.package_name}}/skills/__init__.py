"""Skill package init for {{cookiecutter.package_name}}.

Auto-wraps every skill listed in
``{{cookiecutter.package_name}}.configs.skills_config.SKILL_CONFIGS`` so they
can be imported and called as plain Python functions::

    from {{cookiecutter.package_name}}.skills.<file> import <skill>
    ret = <skill>(inputs='...')

When ``skills_config`` is missing (typical at project bootstrap) wrapping is
skipped silently — UI mode still works via SkillRegistry's saved skills.json.
"""

from robot_agent.skills import auto_wrap_skills, log_data  # noqa: F401

try:
    from {{cookiecutter.package_name}}.configs.skills_config import SKILL_CONFIGS
    auto_wrap_skills(SKILL_CONFIGS, pkg='{{cookiecutter.package_name}}')
except ModuleNotFoundError:
    pass
except Exception as _e:
    import sys
    print(f'[{{cookiecutter.package_name}}.skills] auto_wrap_skills skipped: {_e}',
          file=sys.stderr)
