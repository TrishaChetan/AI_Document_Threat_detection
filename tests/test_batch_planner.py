from parsers.xml_parser import XMLParser
from ai.batch_planner import BatchPlanner


parser = XMLParser("temp_uploads/dvwa_scan_01.xml")

report = parser.parse()

planner = BatchPlanner()

batches = planner.create_batches(report.vulnerabilities)

print("=" * 50)

print("Total vulnerabilities :", len(report.vulnerabilities))

print("Total batches :", len(batches))

print("=" * 50)

for i, batch in enumerate(batches, start=1):

    print(f"\nBatch {i}")

    print("-" * 30)

    for v in batch:

        print(v.title)