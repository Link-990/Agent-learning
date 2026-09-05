"""Check the minimum Python features used by the Runtime course."""

import json


def build_state() -> dict[str, object]:
    return {"run_id": "run-000", "status": "ready", "step": 0}


def main() -> None:
    state = build_state()
    encoded = json.dumps(state, ensure_ascii=False)
    decoded = json.loads(encoded)
    print("state:", state)
    print("json:", encoded)
    print("decoded run_id:", decoded["run_id"])

    try:
        raise ValueError("demo failure")
    except ValueError as exc:
        print({"status": "failed", "error": str(exc)})


if __name__ == "__main__":
    main()
