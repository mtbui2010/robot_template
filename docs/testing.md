# Testing robot_template

Generate a project and check its manifest against its skills (needs
`pip install cookiecutter` and robot_agent importable):

```bash
cookiecutter --no-input . -o /tmp/rt_out
PYTHONPATH=../robot_agent python -m robot_agent.contract.check_manifest --strict /tmp/rt_out/my_robot/my_robot
```

[base_robot](../../base_robot/CLAUDE.md) is a project generated from this
template; its tests and the scenario suite
([../../scenarios/CLAUDE.md](../../scenarios/CLAUDE.md)) run it end to end.
