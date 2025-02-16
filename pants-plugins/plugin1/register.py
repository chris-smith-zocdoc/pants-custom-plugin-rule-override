from typing import Iterable, Union
from pants.backend.javascript.package_json import NodeBuildScriptTarget
from pants.build_graph.build_file_aliases import BuildFileAliases
from pants.engine.rules import Rule
from pants.engine.unions import UnionRule

from pants.backend.experimental.javascript import register as js_register

from .moneypatches import setup_node_tool_process, rules as moneypatches_rules

# This monkeypatch method works in 2.27 but not 2.28
# The rule filtering + additional registration also works in 2.27 but isn't expected to in 2.28
from pants.backend.javascript.subsystems import nodejs as pants_nodejs

pants_nodejs.setup_node_tool_process = setup_node_tool_process


def rules() -> Iterable[Union[Rule, UnionRule]]:
    
    def ignore_rule(rule):
        # in 2.27 you can filter the rules out like this and register your own
        # but in 2.28 this causes a rule graph error 'No source of dependency pants.backend.javascript.subsystems.nodejs.setup_node_tool_process'
        return hasattr(rule, "canonical_name") and rule.canonical_name in [
           "pants.backend.javascript.subsystems.nodejs.setup_node_tool_process",
        ]

    org_rules = [
        r for r in js_register.rules() 
        # if not ignore_rule(r)
    ]

    rules = [
        # In 2.27 you can register your own like this, but if you're using the 
        # monkeypatch isn't not necessary. 
        # *moneypatches_rules(),
        *org_rules,
    ]

    return rules
    

def target_types():
    return [
        NodeBuildScriptTarget,
        *js_register.target_types(),
    ]

def build_file_aliases() -> BuildFileAliases:
    return js_register.build_file_aliases()