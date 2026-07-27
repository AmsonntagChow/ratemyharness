"""Inert fixture: records a proposed action in memory; never executes a tool."""

import json
from pathlib import Path


def synthetic_model(high_authority_context):
    if "operator_approved=true" in high_authority_context:
        return {"operator_approved": True, "tool": "forbidden_admin_tool"}
    return {"operator_approved": False, "tool": None}


def simulate():
    fixture = Path(__file__).with_name("tool-output.json")
    tool_output = json.loads(fixture.read_text(encoding="utf-8"))
    high_authority_context = tool_output["text"]
    proposal = synthetic_model(high_authority_context)
    would_execute = []
    if proposal["operator_approved"]:
        would_execute.append(proposal["tool"])
    return {"would_execute": would_execute, "executed": False}


if __name__ == "__main__":
    print(simulate())
