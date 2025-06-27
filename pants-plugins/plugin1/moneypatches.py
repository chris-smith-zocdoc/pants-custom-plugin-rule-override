from __future__ import annotations

import logging
from typing import Iterable

from pants.backend.javascript.subsystems.nodejs import (
    CorepackToolDigest,
    CorepackToolRequest,
    NodeJSProcessEnvironment,
    NodeJSToolProcess,
    prepare_corepack_tool
)
from pants.engine.internals.native_engine import Digest, MergeDigests
from pants.engine.internals.selectors import Get
from pants.engine.intrinsics import merge_digests
from pants.engine.process import Process
from pants.engine.rules import Rule, collect_rules, implicitly, rule
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel

logger = logging.getLogger(__name__)

@rule(level=LogLevel.DEBUG)
async def setup_node_tool_process(
    request: NodeJSToolProcess, environment: NodeJSProcessEnvironment
) -> Process:
    if request.tool in ("npm", "npx", "pnpm", "yarn"):
        tool_name = request.tool.replace("npx", "npm")
        corepack_tool = await prepare_corepack_tool(
            CorepackToolRequest(tool_name, request.tool_version), **implicitly()
        )
        input_digest = await merge_digests(
            MergeDigests([request.input_digest, corepack_tool.digest])
        )
    else:
        input_digest = request.input_digest

    envvars = {
        # This is the modification to the rule we're trying to observe in the index.js
        "INJECTED_ENV_VAR": "hello",
        **environment.to_env_dict(request.extra_env),
    }


    return Process(
        argv=list(filter(None, (request.tool, *request.args))),
        input_digest=input_digest,
        output_files=request.output_files,
        immutable_input_digests=environment.immutable_digest(),
        output_directories=request.output_directories,
        description=request.description,
        level=request.level,
        env=envvars,
        working_directory=request.working_directory,
        append_only_caches={
            **request.append_only_caches,
            **environment.append_only_caches,
        },
        timeout_seconds=request.timeout_seconds,
    )


def rules() -> Iterable[Rule | UnionRule]:
    return [
        *collect_rules(),
    ]
