"""Observe process, thread, waiting, and CPU work without external services."""

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import os
import threading
import time


def io_task(name: str, delay: float) -> str:
    print(f"io start name={name} pid={os.getpid()} tid={threading.get_ident()}")
    time.sleep(delay)
    return f"io done name={name}"


def cpu_task(number: int) -> tuple[int, int, int]:
    total = 0
    for value in range(350_000):
        total += value * value
    return number, total, os.getpid()


def main() -> None:
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(io_task, ("A", "B"), (0.2, 0.2)))
    print("io results:", results)
    print(f"io elapsed={time.perf_counter() - started:.2f}s")

    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(cpu_task, range(2)))
    print(f"parent pid={os.getpid()} process results (number, value, worker_pid):", results)
    print(f"process elapsed={time.perf_counter() - started:.2f}s")


if __name__ == "__main__":
    main()
