from __future__ import annotations

import functools
import queue
import threading
import time
from typing import Callable, TypeVar, ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


def throttle_dispatch(interval: float) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator that throttles function calls with a minimum interval between each execution.

    Args:
        interval (float): The minimum interval between each function call.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        call_queue = queue.Queue()
        lock = threading.Lock()
        last_called = 0.0
        processing = False

        def process_queue() -> None:
            nonlocal last_called, processing
            with lock:
                processing = True

            while True:
                try:
                    args, kwargs, result_event, result_container = call_queue.get(
                        block=False
                    )

                    elapsed = time.time() - last_called
                    if elapsed < interval:
                        time.sleep(interval - elapsed)

                    try:
                        last_called = time.time()
                        result = func(*args, **kwargs)
                        result_container[0] = (result, None)
                    except Exception as e:
                        result_container[0] = (None, e)

                    result_event.set()
                    call_queue.task_done()

                except queue.Empty:
                    with lock:
                        if call_queue.empty():
                            processing = False
                            break

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result_event = threading.Event()
            result_container = [None]

            call_queue.put((args, kwargs, result_event, result_container))

            with lock:
                if not processing:
                    thread = threading.Thread(target=process_queue, daemon=True)
                    thread.start()

            result_event.wait()
            result, exception = result_container[0]
            if exception:
                raise exception
            return result

        return wrapper

    return decorator
