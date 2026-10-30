"""Cookiecutter post-generation hook.

Runs from inside the freshly-generated project directory. Reads the
comma-separated `skills` answer and:

  1. Validates each skill name is a valid Python identifier.
  2. Generates one mock skill file per name under <pkg>/skills/<skill>.py.
  3. Generates <pkg>/configs/skills_config.py mapping each skill name to its
     (module_path, func_name) tuple.
  4. Generates <pkg>/configs/manifest.yaml declaring each skill for the
     planner (robot_agent.contract.Manifest); configs/adapter.py reads it.

Mock skills receive a slightly richer body for the three defaults (`find`,
`pick`, `place`) so users have something runnable to read; all other skills
get a generic stub.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# These two values are rendered by cookiecutter (Jinja2) BEFORE the script
# is exec'd. Everything else (including the template strings below) is
# protected by `{% raw %}...{% endraw %}` so Python's `{}` doesn't collide
# with Jinja's `{}`.
PACKAGE_NAME = '{{cookiecutter.package_name}}'
SKILLS_RAW   = '{{cookiecutter.skills}}'

{% raw %}
IDENT_RE = re.compile(r'^[a-z_][a-z0-9_]*$')

PROJECT_ROOT = Path.cwd()                       # cookiecutter cwd = new project root
{% endraw %}
PKG_DIR      = PROJECT_ROOT / PACKAGE_NAME
{% raw %}
SKILLS_DIR   = PKG_DIR / 'skills'
CONFIGS_DIR  = PKG_DIR / 'configs'


# ── Skill body templates ─────────────────────────────────────────────────────

GENERIC_TEMPLATE = '''"""Mock implementation of `{name}`. Replace the body with the real logic.

Skill contract: see {pkg}/README.md ("Skill contract" section).
"""

from robot_agent.skills import log_data


def {name}(node, **params) -> dict:
    """Skill `{name}`.

    Args:
        node:   live ROS2 node (already spinning in MultiThreadedExecutor).
        params: JSON body of POST /skill/{name} unpacked as kwargs.

    Returns:
        dict with at least 'isdone': bool.
    """
    log_data({{'msg': f'{name} called with params={{params}}'}})

    # TODO: replace this stub.
    #
    # Common patterns:
    #   client = node.agents['my_device']        # registered via Connections UI
    #   result = client.send({{'x': 1.0, ...}})
    #   client_get = client.get()                # for subscribers
    #
    # See <pkg>/template_skills/ for reference patterns.

    return {{'isdone': True, 'msg': '{name} stub'}}
'''


FIND_TEMPLATE = '''"""Mock `find` skill — fetch image + call detector. Replace with real logic.

Generated to mirror `make skill-detect`: pulls a frame from a registered
camera agent and forwards it to a TCP detector client. Edit the agent name,
detector key, and request payload to match your setup.
"""

from robot_agent.skills import log_data
from robot_agent.state  import current


def _fetch_data_find(node):
    """Mock image fetch. Replace 'head_rgb'/'head_depth' with the agent names
    you registered in the Connections panel."""
    a = node.agents
    rgb         = a['head_rgb'].get()         if 'head_rgb'         in a else None
    depth       = a['head_depth'].get()       if 'head_depth'       in a else None
    cam_params  = a['head_cam_params'].get()  if 'head_cam_params'  in a else None
    if rgb is None:
        raise Exception("camera agent 'head_rgb' not registered — add it in the Connections panel")
    return {{
        'rgb':        rgb.get('im')                 if isinstance(rgb,        dict) else rgb,
        'depth':      depth.get('im')               if isinstance(depth,      dict) else depth,
        'cam_params': cam_params.get('cam_params')  if isinstance(cam_params, dict) else cam_params,
    }}


def find(node, **params) -> dict:
    """Skill `find` — mock detector flow.

    1. Fetch an image from the camera agent (see _fetch_data_find).
    2. Send the image + params to the detector client over TCP.
    3. Log the result and return it.
    """
    log_data({{'msg': f'find called with params={{params}}'}})

    # 1. fetch image
    data = _fetch_data_find(node)

    # 2. call the detector client (TCP). Register a TCP client named 'detector'
    #    (or rename below) in the Connections panel.
    detector = current().dm.get_client('detector')
    if detector is None:
        raise Exception("TCP client 'detector' not registered — add it in the Connections panel")

    # Edit the request shape to match your detector server's contract.
    request = {{
        'detector': 'mask2grasps',   # detector name on the server side
        'image':    data['rgb'],
        **params,
    }}
    result = detector.send(request)  # -> whatever your server returns (dict / ndarray)

    # 3. log the annotated image so it shows up in the UI Camera panel
    log_data({{'log_image': data['rgb']}})

    return {{'isdone': True, 'msg': 'find done', 'result': result}}
'''


PICK_TEMPLATE = '''"""Mock `pick` skill -- pick up an object.

Replace the body with motion-planning + gripper control.
"""

from robot_agent.skills import log_data


def pick(node, **params) -> dict:
    """Pick up `target`.

    Typically run after `find`. May read its position via:
        position = params.get('position', [0, 0, 0])

    Args:
        target   (str):              object name.
        position (list[float], opt): xyz in metres; defaults to [0,0,0].

    Returns:
        dict: {{'isdone': bool, 'msg': str, 'grasped': bool}}
    """
    target   = params.get('target', '')
    position = params.get('position', [0.0, 0.0, 0.0])
    log_data({{'msg': f'pick {{target!r}} at {{position}}'}})

    # TODO: real implementation. Example sketch:
    #   arm   = node.agents['arm']
    #   grip  = node.agents['gripper']
    #   arm.send({{'goto': position}})
    #   grip.send({{'close': True}})

    return {{
        'isdone': True,
        'msg':    f'(stub) picked {{target!r}}',
        'grasped': True,
    }}
'''


PLACE_TEMPLATE = '''"""Mock `place` skill -- place a held object somewhere.

Replace the body with motion-planning + gripper release.
"""

from robot_agent.skills import log_data


def place(node, **params) -> dict:
    """Place the currently-held object at `location`.

    Args:
        location (str | list[float]):
            named location (e.g. "kitchen_table") or xyz in metres.

    Returns:
        dict: {{'isdone': bool, 'msg': str, 'released': bool}}
    """
    location = params.get('location', '')
    log_data({{'msg': f'place at {{location!r}}'}})

    # TODO: real implementation. Example sketch:
    #   arm  = node.agents['arm']
    #   grip = node.agents['gripper']
    #   arm.send({{'goto': resolve_location(location)}})
    #   grip.send({{'open': True}})

    return {{
        'isdone': True,
        'msg':    f'(stub) placed at {{location!r}}',
        'released': True,
    }}
'''


SPECIAL_TEMPLATES = {
    'find':  FIND_TEMPLATE,
    'pick':  PICK_TEMPLATE,
    'place': PLACE_TEMPLATE,
}


SKILLS_CONFIG_TEMPLATE = '''# Auto-generated by cookiecutter — edit freely.
#
# Maps skill_name → (module_path, func_name). robot_agent loads this at boot
# (or on POST /skills/reload) and exposes each as POST /skill/<name>.
#
# To add a new skill:
#   1. Create {pkg}/skills/<name>.py with `def <name>(node, **params) -> dict`.
#   2. Add a line below: '<name>': (f'{{_PKG}}.<file>', '<func>'),
#   3. POST /skills/reload (or restart the agent).

_PKG = '{pkg}.skills'

SKILL_CONFIGS: dict[str, tuple[str, str]] = {{
{entries}
}}
'''


def parse_skill_names(raw: str) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for token in raw.split(','):
        name = token.strip()
        if not name:
            continue
        if not IDENT_RE.match(name):
            print(
                f'ERROR: skill name {name!r} is not a valid Python identifier '
                '(expected: lowercase, digits, underscores, starting with letter/underscore).',
                file=sys.stderr,
            )
            sys.exit(1)
        if name in seen:
            print(f'ERROR: skill name {name!r} listed twice.', file=sys.stderr)
            sys.exit(1)
        seen.add(name)
        names.append(name)
    return names


def write_skill_file(name: str) -> None:
    template = SPECIAL_TEMPLATES.get(name, GENERIC_TEMPLATE)
    body = template.format(name=name, pkg=PACKAGE_NAME)
    (SKILLS_DIR / f'{name}.py').write_text(body)


def write_skills_config(names: list[str]) -> None:
    entries = '\n'.join(
        f"    {name!r:24}: (f'{{_PKG}}.{name}', {name!r}),"
        for name in names
    )
    text = SKILLS_CONFIG_TEMPLATE.format(pkg=PACKAGE_NAME, entries=entries)
    (CONFIGS_DIR / 'skills_config.py').write_text(text)


# ── manifest.yaml (robot_agent.contract) ────────────────────────────────────
# skill name -> abstract planner action; anything else gets its CamelCase name
KNOWN_ACTIONS = {
    'move': 'MoveTo', 'navigate': 'MoveTo', 'goto': 'MoveTo',
    'find': 'Find', 'detect': 'Find', 'look': 'Find',
    'pick': 'Pick', 'grasp': 'Pick',
    'place': 'Place', 'put': 'Place',
    'open': 'Open', 'open_drawer': 'Open', 'close': 'Close', 'close_drawer': 'Close',
    'say': 'Say', 'speak': 'Say', 'announce': 'Say', 'ask': 'Ask',
}
# per action: (main param, other params, pre, effects, errors) — matches the mock bodies above
ACTION_SPECS = {
    'MoveTo': ('inputs', {}, [], ['arrived(?inputs)'], ['unreachable', 'blocked', 'timeout']),
    'Find':   ('inputs', {}, [], ['found(?inputs)'], ['absent', 'perception_unavailable']),
    'Pick':   ('target', {'position': 'array'}, ['found(?target)', 'hand_empty'],
               ['holding(?target)', 'not hand_empty'], ['absent', 'unreachable', 'grasp_failed']),
    'Place':  ('location', {}, ['not hand_empty'], ['hand_empty'], ['dropped', 'blocked', 'unreachable']),
    'Open':   ('inputs', {}, ['hand_empty'], ['opened(?inputs)'], ['unreachable', 'grasp_failed']),
    'Close':  ('inputs', {}, ['hand_empty'], ['not opened(?inputs)'], ['unreachable', 'grasp_failed']),
}
GENERIC_SPEC = ('inputs', {}, [], [], ['unknown'])
# holding an object / pulling a drawer: the planner lets these finish before it stops
NOT_INTERRUPTIBLE = {'Pick', 'Place', 'Open', 'Close'}

MANIFEST_HEADER = """# What {pkg} can do, for robot_agent's planner (robot_agent.contract.Manifest).
# Generated by robot_template -- edit freely, then check it against the skills:
#     python -m robot_agent.contract.check_manifest {pkg}
#
# Per skill: action = the abstract planner action it realises (MoveTo Find Pick Place
# Open Close Say Ask ...); params = JSON schema of its kwargs; pre / hold / effects =
# predicates over the shared world model (arrived(L) found(O) holding(O) hand_empty
# opened(C), "not P" negates, ?x = the param x); verify = symbolic | sensor (another
# skill that checks, e.g. grasp_succeed) | vlm (prompt); errors = the FailureCodes it
# may return (absent perception_unavailable unreachable blocked grasp_failed dropped
# hw_fault estop timeout cancelled software unknown).
robot: {pkg}
version: "1.0"
language: en
# TODO: describe the hardware (base-only robots: arms 0, hands [])
capabilities: {{base: {base}, arms: {arms}, hands: {hands}, lift: false, head: false, drawer: false}}
# metres; robot_agent's defaults shown
geometry: {{arrive_tol_m: 0.3, reach_m: 0.78, reach_far_m: 1.0}}
skills:
"""


def _camel(name: str) -> str:
    return ''.join(p.capitalize() for p in name.split('_') if p) or 'Skill'


def _yaml_list(items) -> str:
    return '[' + ', '.join(f'"{x}"' if any(c in x for c in '(?: ') else x for x in items) + ']'


def manifest_entry(name: str) -> str:
    action = KNOWN_ACTIONS.get(name, _camel(name))
    main, others, pre, effects, errors = ACTION_SPECS.get(action, GENERIC_SPEC)
    props = ', '.join([f'{main}: {{type: string}}'] + [f'{k}: {{type: {t}}}' for k, t in others.items()])
    todo = '' if name in KNOWN_ACTIONS else '    # TODO: pick the abstract action, pre / effects and errors\n'
    return (f'  - name: {name}\n'
            f'{todo}'
            f'    action: {action}\n'
            f'    params: {{type: object, properties: {{{props}}}, required: [{main}]}}\n'
            f'    pre: {_yaml_list(pre)}\n'
            f'    hold: []\n'
            f'    effects: {_yaml_list(effects)}\n'
            f'    verify: [{{kind: symbolic}}]\n'
            f'    interruptible: {"false" if action in NOT_INTERRUPTIBLE else "true"}\n'
            f'    errors: {_yaml_list(errors)}\n'
            f'    version: "1.0"\n')


def write_manifest(names: list[str]) -> None:
    actions = {KNOWN_ACTIONS.get(n) for n in names}
    has_arm = bool(actions & {'Pick', 'Place', 'Open', 'Close'})
    text = MANIFEST_HEADER.format(pkg=PACKAGE_NAME, base='true' if 'MoveTo' in actions else 'false',
                                  arms=1 if has_arm else 0, hands='[hand]' if has_arm else '[]')
    text += ''.join(manifest_entry(n) for n in names) if names else '  []\n'
    if not names:
        text = text.replace('skills:\n  []', 'skills: []')
    (CONFIGS_DIR / 'manifest.yaml').write_text(text)


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print(f'ERROR: expected skills dir at {SKILLS_DIR}', file=sys.stderr)
        return 1
    if not CONFIGS_DIR.is_dir():
        print(f'ERROR: expected configs dir at {CONFIGS_DIR}', file=sys.stderr)
        return 1

    names = parse_skill_names(SKILLS_RAW)
    if not names:
        print('WARNING: no skills specified -- generated package will have an empty SKILL_CONFIGS.')

    for name in names:
        write_skill_file(name)
    write_skills_config(names)
    write_manifest(names)

    print(f'[robot_template] generated {len(names)} skill file(s): {", ".join(names) or "(none)"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
{% endraw %}
