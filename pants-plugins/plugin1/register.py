from typing import Callable, Iterable, Union
from pants.backend.javascript.package_json import NodeBuildScriptTarget
from pants.build_graph.build_file_aliases import BuildFileAliases
from pants.engine.rules import Rule, TaskRule
from pants.engine.unions import UnionRule
import dataclasses
from pants.backend.experimental.javascript import register as js_register

from .moneypatches import rules as moneypatches_rules

def rules() -> Iterable[Union[Rule, UnionRule]]:
    
    def ignore_rule(rule):
        return isinstance(rule, TaskRule) and rule.canonical_name in [
            "pants.backend.javascript.subsystems.nodejs.setup_node_tool_process",
        ]
    
    original_rules = [
        r for r in js_register.rules()
        # Remove the original rule
        if not ignore_rule(r)
    ]
    
    custom_rules = []
    for rule in moneypatches_rules():
        if isinstance(rule, TaskRule) and rule.func.__name__ == "setup_node_tool_process":
            # Set the canonical name of our moneypatch to the original rule
            custom_rules.append(dataclasses.replace(rule, canonical_name="pants.backend.javascript.subsystems.nodejs.setup_node_tool_process"))
        else:
            custom_rules.append(rule)

    return [
        *original_rules,
        *custom_rules,
    ]


def target_types():
    return [
        NodeBuildScriptTarget,
        *js_register.target_types(),
    ]

def build_file_aliases() -> BuildFileAliases:
    return js_register.build_file_aliases()