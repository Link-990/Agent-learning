"""Observe cooperative scheduling, timeout, and cancellation."""

import asyncio
import time


async def io_task(name: str, delay: float) -> str:
    print(f"start {name}")
    await asyncio.sleep(delay)
    print(f"finish {name}")
    return f"{name} done"


async def cancelled_task() -> None:
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("cancelled task cleaned up")
        raise


async def main() -> None:
    started = time.perf_counter()
    results = await asyncio.gather(
        io_task("A", 0.2),
        io_task("B", 0.1),
    )
    print("results:", results)
    print(f"concurrent elapsed={time.perf_counter() - started:.2f}s")

    try:
        await asyncio.wait_for(io_task("timeout", 1), timeout=0.05)
    except asyncio.TimeoutError:
        print("timeout was converted to a controllable error")

    task = asyncio.create_task(cancelled_task())
    await asyncio.sleep(0)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("caller observed cancellation")


if __name__ == "__main__":
    asyncio.run(main())
