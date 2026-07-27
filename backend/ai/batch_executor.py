from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from ai.recommendation_engine import RecommendationEngine


class BatchExecutor:

    def __init__(self, workers=2):
        self.workers = max(1, workers)
        self.engine = RecommendationEngine()
        self.lock = Lock()

    def process_batch(self, batch):

        analyzed = []

        for i, vulnerability in enumerate(batch, start=1):

            with self.lock:
                print(f"Analyzing {vulnerability.title} ({i}/{len(batch)})")

            ai = self.engine.analyze(vulnerability)

            data = vulnerability.model_dump()
            data["ai_analysis"] = ai.model_dump()

            analyzed.append(data)

        return analyzed

    def execute(self, batches):

        final_results = []

        with ThreadPoolExecutor(max_workers=self.workers) as executor:

            futures = [
                executor.submit(self.process_batch, batch)
                for batch in batches
            ]

            for future in futures:
                try:
                    final_results.extend(future.result())
                except Exception as e:
                    with self.lock:
                        print(f"Batch execution failed: {e}")

        return final_results