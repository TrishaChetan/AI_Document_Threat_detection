import time

from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
)


class RetryExecutor:

    def __init__(self, retries=5, delay=2):
        self.retries = max(1, retries)
        self.delay = max(1, delay)

    def run(self, func):

        wait = self.delay

        for attempt in range(1, self.retries + 1):

            try:
                return func()

            except (
                RateLimitError,
                InternalServerError,
                APIConnectionError,
                APITimeoutError,
            ) as e:

                print(
                    f"[Attempt {attempt}/{self.retries}] "
                    f"{type(e).__name__}: {e}"
                )

                if attempt == self.retries:
                    print("Maximum retry limit reached.")
                    raise

                print(f"Retrying in {wait} seconds...\n")

                time.sleep(wait)

                wait = min(wait * 2, 30)

        raise RuntimeError("RetryExecutor exited unexpectedly.")