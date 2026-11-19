"""Fail a CI build when a ZAP scan breaks your security policy.

    cd backend
    python scan_gate.py report.xml                                  # fail on any High finding
    python scan_gate.py report.xml --fail-on medium --max low=10
    python scan_gate.py report.xml --baseline last_release.xml      # only NEW findings count
    python scan_gate.py report.xml --policy ../zap-gate.json --github

--github prints ::error annotations and appends a summary to $GITHUB_STEP_SUMMARY.
Exit codes: 0 pass · 1 policy violated · 2 bad input.
"""
import argparse
import json
import os
import sys

from parsers import parse_report
from services.scan_gate import Policy, evaluate, format_text, github_annotations, markdown_summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report", help="ZAP .xml or .json report of this build")
    ap.add_argument("--baseline", help="report from the last release; only new findings count")
    ap.add_argument("--policy", help="JSON policy file: {fail_on, max, ignore}")
    ap.add_argument("--fail-on", help="High | Medium | Low | Informational | none (overrides the policy file)")
    ap.add_argument("--max", action="append", default=[], metavar="SEV=N", help="severity budget, e.g. medium=5 (repeatable)")
    ap.add_argument("--github", action="store_true", help="GitHub Actions annotations + job summary")
    ap.add_argument("--json", action="store_true", help="print the result as JSON")
    args = ap.parse_args(argv)
    try:
        policy = Policy.load(args.policy) if args.policy else Policy()
        if args.fail_on:
            policy.fail_on = "none" if args.fail_on.lower() == "none" else Policy.from_dict({"fail_on": args.fail_on}).fail_on
        for item in args.max:
            sev, _, n = item.partition("=")
            policy.max.update(Policy.from_dict({"max": {sev: int(n)}}).max)
        report = parse_report(args.report)
        baseline = parse_report(args.baseline) if args.baseline else None
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    res = evaluate(report, policy, baseline)
    print(json.dumps(res, indent=2) if args.json else format_text(res))
    if args.github:
        for line in github_annotations(res):
            print(line)
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary, "a", encoding="utf-8") as fh:
                fh.write(markdown_summary(res))
    return 0 if res["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
