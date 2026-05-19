"""Runtime configs for {{cookiecutter.package_name}}.

`robot_agent.ConfigManager` imports this module via the robot_pkg argument
to `create_app`. Any module-level dict here (e.g. `ARM_CONFIGS`, `ENV`,
`LLM_SERVERS`) overrides the corresponding hardcoded `_default` in
`robot_agent.skill_configs`.

This file is intentionally empty -- robot_agent's built-in defaults will be
used for any name that isn't defined here. Add what you need:

    ARM_CONFIGS = {
        'home': [0, 0, 0, 0, 0, 0],
        ...
    }

    ENV = {
        'kitchen': {'pose': {...}, ...},
        'living':  {'pose': {...}, ...},
    }
"""
