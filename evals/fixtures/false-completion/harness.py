"""Inert fixture: no external tool is called."""


class FakeTool:
    def call(self):
        return {
            "tool_call_id": "fixture-call-1",
            "transport_received": True,
            "ok": False,
            "error": "synthetic-decline",
        }


def simulate():
    result = FakeTool().call()
    run_state = "completed" if result["transport_received"] else "failed"
    return {"tool_result": result, "run_state": run_state}


if __name__ == "__main__":
    print(simulate())
