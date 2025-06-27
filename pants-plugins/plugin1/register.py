from typing import Callable, Iterable, Union
from pants.backend.javascript.package_json import NodeBuildScriptTarget
from pants.build_graph.build_file_aliases import BuildFileAliases
from pants.engine.rules import Rule, TaskRule
from pants.engine.unions import UnionRule
import dataclasses
from pants.backend.experimental.javascript import register as js_register

from .moneypatches import setup_node_tool_process, rules as moneypatches_rules

# This monkeypatch method works in both 2.27 and 2.28!!
from pants.backend.javascript.subsystems import nodejs as pants_nodejs
# Need to monkeypatch here
pants_nodejs.setup_node_tool_process = setup_node_tool_process

def single_or_raise(rules: Iterable[TaskRule], lambda_filter: Callable[[TaskRule], bool]) -> TaskRule:
    matching_rules = [
        r for r in rules 
        if lambda_filter(r)
    ]
    if len(matching_rules) != 1:
        raise Exception(f"Expected 1 matching rule, got {len(matching_rules)}\n{matching_rules}")
    return matching_rules[0]


def rules() -> Iterable[Union[Rule, UnionRule]]:
    
    custom_rules = [
        *moneypatches_rules(),
    ]
    original_rules = [
        *js_register.rules(),
    ]
    
    custom_rule = single_or_raise(
        custom_rules,
        lambda r: isinstance(r, TaskRule) and r.func.__name__ == "setup_node_tool_process"
    )

    patched_rules = []
    for rule in original_rules:
        if isinstance(rule, TaskRule) and rule.func.__name__ == "setup_node_tool_process":
            # And also replace the callable stored in the original rule
            patched_rules.append(dataclasses.replace(rule, func=custom_rule.func))
        else:
            patched_rules.append(rule)

    return [
        *patched_rules,
    ]


def target_types():
    return [
        NodeBuildScriptTarget,
        *js_register.target_types(),
    ]

def build_file_aliases() -> BuildFileAliases:
    return js_register.build_file_aliases()