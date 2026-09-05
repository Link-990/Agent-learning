"""Priority queue, temporary retry, unknown errors, and safe shutdown."""

from dataclasses import dataclass, field
import queue
import threading
import time
import uuid


@dataclass(order=True)
class Job:
    priority: int
    created_at: float = field(compare=True)
    job_id: str = field(compare=False)
    attempts: int = field(default=0, compare=False)
    stop: bool = field(default=False, compare=False)


class Runtime:
    def __init__(self, worker_count: int = 2, max_retries: int = 2) -> None:
        self.jobs: queue.PriorityQueue[Job] = queue.PriorityQueue(maxsize=3)
        self.worker_count = worker_count
        self.max_retries = max_retries
        self.stop = threading.Event()
        self.threads: list[threading.Thread] = []

    def submit(self, job: Job) -> None:
        self.jobs.put(job)  # 队列满时阻塞，形成背压
        print(f"submit job={job.job_id} priority={job.priority}")

    def worker(self, number: int) -> None:
        while True:
            try:
                job = self.jobs.get(timeout=0.1)
            except queue.Empty:
                if self.stop.is_set():
                    return
                continue
            try:
                if job.stop:
                    return
                job.attempts += 1
                print(
                    f"worker={number} start job={job.job_id} "
                    f"priority={job.priority} attempt={job.attempts}"
                )
                time.sleep(0.05)
                if job.attempts == 1:
                    raise TimeoutError("temporary tool timeout")
                print(f"worker={number} success job={job.job_id}")
            except TimeoutError as exc:
                if job.attempts <= self.max_retries:
                    print(f"retry job={job.job_id} reason={exc}")
                    self.jobs.put(job)
                else:
                    print(f"failed job={job.job_id} attempts={job.attempts}")
            except Exception as exc:
                print(f"failed job={job.job_id} unexpected={type(exc).__name__}: {exc}")
            finally:
                self.jobs.task_done()

    def start(self) -> None:
        for number in range(self.worker_count):
            thread = threading.Thread(target=self.worker, args=(number,), daemon=True)
            thread.start()
            self.threads.append(thread)

    def shutdown(self, timeout: float = 5.0) -> None:
        joiner = threading.Thread(target=self.jobs.join, daemon=True)
        joiner.start()
        joiner.join(timeout)
        if joiner.is_alive():
            print("shutdown timeout: abandoning queued jobs")
            while True:
                try:
                    self.jobs.get_nowait()
                except queue.Empty:
                    break
                else:
                    self.jobs.task_done()
        self.stop.set()
        for _ in self.threads:
            self.jobs.put(Job(10**9, time.time(), "STOP", stop=True))
        for thread in self.threads:
            thread.join(timeout=timeout)
        print("all jobs completed and workers stopped")


if __name__ == "__main__":
    runtime = Runtime()
    runtime.start()
    for priority in (5, 1, 3):
        runtime.submit(Job(priority, time.time(), uuid.uuid4().hex[:6]))
    runtime.shutdown()
