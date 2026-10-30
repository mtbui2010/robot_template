"""RobotAdapter for {{cookiecutter.package_name}}: how robot_agent's planner drives this robot.

robot_agent finds it with ``robot_agent.contract.load_adapter('{{cookiecutter.package_name}}')``,
which calls ``make_adapter()`` below. Everything robot-specific the planner
needs lives here and in ``manifest.yaml`` next to it, never in robot_agent:

  * manifest  -- the skills (abstract action, params, pre / effects, errors)
  * geometry  -- arrive tolerance, arm reach, workspace (manifest ``geometry``)
  * i18n      -- default language + phrases
  * bind()    -- an abstract plan step -> (skill name, params)
  * observe() / reconcile() / health() -- what the robot sees / believes / how it is

Check the manifest against the skills with
``python -m robot_agent.contract.check_manifest {{cookiecutter.package_name}}``.
The contract is described in robot_agent/docs/contract.md.
"""

from __future__ import annotations

import re
from pathlib import Path

from robot_agent.contract import Geometry, Manifest, Messages, Observation, Unbindable

MANIFEST_PATH = Path(__file__).with_name('manifest.yaml')

# Plan steps that need no robot motion: done without calling a skill.
NOOP_ACTIONS = {'Wait', 'Sit', 'LieOn', 'Serve'}

# Planner object / place names (CamelCase) -> what the skills expect. Fill in
# the names your detector / map use; unknown names fall back to "two words".
NAMES: dict[str, str] = {
    # 'LivingRoom': 'living room',
    # 'WaterBottle': 'water bottle',
}

# Per-robot changes to robot_agent's default recovery table (contract/recovery.py).
RECOVERY_OVERRIDES: dict = {
    # 'perception_unavailable': {'action': 'wait_health', 'retries': 3, 'then': 'stop'},
}


def to_name(name: str) -> str:
    """'CoffeeMachine' -> 'coffee machine' unless NAMES says otherwise."""
    if not name:
        return ''
    if name in NAMES:
        return NAMES[name]
    return ' '.join(re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', name).replace('_', ' ').split()).lower()


class Adapter:
    def __init__(self, manifest: Manifest | None = None):
        self.manifest = manifest or Manifest.from_yaml(MANIFEST_PATH)
        self.geometry = Geometry.from_dict(self.manifest.geometry)
        self.i18n = Messages(language=self.manifest.language)
        self.recovery_overrides = RECOVERY_OVERRIDES

    def bind(self, step: dict, world=None):
        """{'action': 'Pick', 'object': 'Cup'} -> ('pick', {'target': 'cup'}); None for a no-op."""
        action = (step.get('action') or '').strip()
        obj = (step.get('object') or '').strip()
        if action in NOOP_ACTIONS:
            return None
        spec = self.manifest.skill_for(action)
        if spec is None:
            raise Unbindable(f'no skill for {action!r} on {self.manifest.robot}')
        if not obj and action == 'Pick':
            obj = getattr(world, 'found', None) or ''
        if not obj:
            raise Unbindable(f'{action} needs an object')
        # The step's object goes into the skill's main param (the first required
        # one). Add skill-specific extras here, e.g. a grasp type for Pick.
        key = (spec.required_params or spec.param_names or ['inputs'])[0]
        return spec.name, {key: to_name(obj)}

    def observe(self, node=None) -> Observation:
        # TODO: base pose, what the hand holds, sensor health
        return Observation()

    def reconcile(self, world, node=None):
        # TODO: correct the belief (where the robot is, what it holds) from sensors
        return world

    def health(self, node=None) -> dict:
        # TODO: camera frame age, depth, pose timestamp, e-stop, battery ...
        return {'ok': None}


def make_adapter() -> Adapter:
    return Adapter()
