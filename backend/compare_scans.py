"""Compare two ZAP reports from the command line.

    cd backend
    python compare_scans.py ../reports/zap/xml/juiceshop_scan_01.xml ../reports/zap/xml/juiceshop_scan_02.xml
    python compare_scans.py old.json new.xml --json diff.json

Exit code is 1 if the newer scan introduced any High findings, so it can gate a CI pipeline.
"""
import argparse
import json
import sys

from parsers import parse_report
from services.scan_diff import diff_reports, format_diff


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("baseline")
    ap.add_argument("current")
    ap.add_argument("--json", metavar="FILE", help="also write the full comparison as JSON")
    args = ap.parse_args(argv)
    d = diff_reports(parse_report(args.baseline), parse_report(args.current))
    print(format_diff(d))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(d, fh, indent=2)
    return 1 if d["summary"]["new_high"] else 0


if __name__ == "__main__":
    sys.exit(main())
