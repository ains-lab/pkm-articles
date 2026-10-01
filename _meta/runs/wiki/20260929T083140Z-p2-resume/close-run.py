"""Retired one-off historical closure: never replay old state/log mutations.

Historical run-report.json and final-verification.json remain evidence, not
instructions for a new run. Verified publication is owned by publish-one.py.
The unsafe replay is demonstrated by handoff-red.txt in the repair run.
"""
import json


def main():
    print(json.dumps({
        "status": "retired",
        "reason": "Historical closure cannot be replayed. Use a fresh approved run; "
                  "publication state is committed only by the verified publisher.",
    }))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
