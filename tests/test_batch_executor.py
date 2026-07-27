import time

from parsers.xml_parser import XMLParser
from ai.batch_planner import BatchPlanner
from ai.batch_executor import BatchExecutor


parser = XMLParser("temp_uploads/dvwa_scan_01.xml")

report = parser.parse()

planner = BatchPlanner()

batches = planner.create_batches(
    report.vulnerabilities
)

print(f"Created {len(batches)} batches")

executor = BatchExecutor()

start = time.perf_counter()

results = executor.execute(batches)

end = time.perf_counter()

print()

print(f"Returned {len(results)} AI analyses")

print(f"Execution Time : {end-start:.2f} sec")