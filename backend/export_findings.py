"""Export a ZAP report's findings as SARIF (GitHub Security tab) or CSV.

    cd backend
    python export_findings.py ../reports/zap/xml/dvwa_scan_01.xml --format sarif -o zap.sarif
    python export_findings.py report.json --format csv -o findings.csv
"""
import argparse
import json
import sys

from parsers import parse_report
from services.findings_export import to_csv, to_sarif


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report", help="ZAP .xml or .json report")
    ap.add_argument("--format", choices=["sarif", "csv"], default="sarif")
    ap.add_argument("-o", "--output", help="output file (default: stdout)")
    args = ap.parse_args(argv)
    report = parse_report(args.report)
    text = json.dumps(to_sarif(report), indent=2) if args.format == "sarif" else to_csv(report)
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print(f"{len(report.vulnerabilities)} findings -> {args.output} ({args.format})", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
