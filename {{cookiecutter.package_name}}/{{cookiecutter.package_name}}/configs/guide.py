"""Optional planner guide for {{cookiecutter.package_name}}.

`robot_agent.UnifiedAgent` looks up this module when handling unstructured
("natural language") prompts:

    {{cookiecutter.package_name}}.configs.guide.GUIDE   -- free-form text guide

If you also want structured plan generation (JSON), create
`{{cookiecutter.package_name}}/configs/guide_struct.py` with both `GUIDE`
and `FORMAT` attributes; the planner prefers structured when present.

For structured-only deployments (no LLM planner), this file can stay empty.
"""

GUIDE = ""
