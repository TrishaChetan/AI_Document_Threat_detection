"""Group a ZAP report's findings into fix tickets with severity-based due dates.

    cd backend
    python remediation_plan.py ../reports/zap/xml/webgoat_scan_01.xml
    python remediation_plan.py report.json --format csv -o plan.csv
    python remediation_plan.py report.xml --sla high=14,medium=60 --today 2026-11-17
"""
import argparse
import json
import sys
from datetime import date

from parsers import parse_report
from services.remediation_plan import build_plan, parse_sla, to_csv, to_markdown


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report", help="ZAP .xml or .json report")
    ap.add_argument("--format", choices=["md", "csv", "json"], default="md")
    ap.add_argument("--sla", help="days to fix per severity, e.g. high=14,medium=60,low=120")
    ap.add_argument("--today", help="YYYY-MM-DD to count due dates against (default: today)")
    ap.add_argument("--include-info", action="store_true", help="also make tickets for Informational findings")
    ap.add_argument("-o", "--output", help="output file (default: stdout)")
    args = ap.parse_args(argv)
    try:
        sla = parse_sla(args.sla)
        today = date.fromisoformat(args.today) if args.today else None
    except ValueError as e:
        ap.error(str(e))
    plan = build_plan(parse_report(args.report), today=today, sla=sla, include_info=args.include_info)
    text = {"md": to_markdown, "csv": to_csv, "json": lambda p: json.dumps(p, indent=2)}[args.format](plan)
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print(f"{plan['findings_in']} finding type(s) -> {len(plan['tickets'])} ticket(s) -> {args.output}",
              file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
