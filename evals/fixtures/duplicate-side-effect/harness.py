"""Inert fixture: records synthetic effects in memory and performs no I/O."""


class FakePaymentGateway:
    def __init__(self):
        self.committed = []

    def charge(self, synthetic_order_id, tool_call_id, attempt):
        self.committed.append(
            {"order": synthetic_order_id, "tool_call_id": tool_call_id, "amount": "FIXTURE-10"}
        )
        if attempt == 1:
            raise TimeoutError("synthetic timeout after in-memory commit")
        return {"ok": True, "tool_call_id": tool_call_id}


def simulate():
    gateway = FakePaymentGateway()
    result = None
    for attempt in (1, 2):
        try:
            result = gateway.charge("fixture-order", f"call-{attempt}", attempt)
            break
        except TimeoutError:
            continue
    return {"result": result, "committed": gateway.committed}


if __name__ == "__main__":
    print(simulate())
