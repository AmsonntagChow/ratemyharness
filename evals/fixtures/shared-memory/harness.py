"""Inert fixture: demonstrates cross-session state using synthetic text only."""


shared_context = []


def add_turn(session_id, text):
    shared_context.append({"session_id": session_id, "text": text})


def render_context(_session_id):
    return list(shared_context)


def simulate():
    add_turn("session-a", "fixture-secret-alice")
    return {"session_b_context": render_context("session-b")}


if __name__ == "__main__":
    print(simulate())
