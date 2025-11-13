import time
import threading
import statistics

# ---------------------------------------------
# 1. Factorial function (Iterative)
# ---------------------------------------------
def factorial(n: int) -> int:
    """Iterative factorial to avoid recursion overhead."""
    if n < 0:
        raise ValueError("n must be non-negative")
    result = 1
    # (n - 1) loop iterations dominate → O(n)
    for i in range(2, n + 1):
        result *= i
    return result


# ---------------------------------------------
# 2. Multithreaded factorial computation
# ---------------------------------------------
def run_multithreaded_factorials(rounds: int = 10, numbers=(50, 100, 200)):
    print("=== Multithreading run ===")
    all_times = []

    for r in range(1, rounds + 1):
        timings = {}   # thread_id -> (start_ns, end_ns)
        sizes = {}     # thread_id -> len(str(result))
        threads = []

        def make_worker(n, tid):
            def worker():
                start = time.perf_counter_ns()
                val = factorial(n)
                end = time.perf_counter_ns()
                timings[tid] = (start, end)
                sizes[tid] = len(str(val))  # check result length for correctness
            return worker

        # Create and start threads
        for n in numbers:
            t = threading.Thread(target=make_worker(n, f"n={n}"), daemon=True)
            threads.append(t)

        start_all = time.perf_counter_ns()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        end_all = time.perf_counter_ns()

        first_start = min(s for s, e in timings.values())
        last_end = max(e for s, e in timings.values())
        total_ns = last_end - first_start
        all_times.append(total_ns)

        size_bits = ", ".join(f"{k}: {v} digits" for k, v in sorted(sizes.items()))
        print(f"Round {r:02d}: T = {total_ns} ns | results -> {size_bits}")

    avg_ns = int(statistics.mean(all_times))
    print(f"Average T over {rounds} rounds (multithreading): {avg_ns} ns\n")
    return all_times, avg_ns


# ---------------------------------------------
# 3. Single-threaded factorial computation
# ---------------------------------------------
def run_singlethread_factorials(rounds: int = 10, numbers=(50, 100, 200)):
    print("=== Single-threaded run ===")
    all_times = []

    for r in range(1, rounds + 1):
        start = time.perf_counter_ns()
        sizes = {}
        for n in numbers:
            val = factorial(n)
            sizes[f"n={n}"] = len(str(val))
        end = time.perf_counter_ns()

        total_ns = end - start
        all_times.append(total_ns)

        size_bits = ", ".join(f"{k}: {v} digits" for k, v in sorted(sizes.items()))
        print(f"Round {r:02d}: T = {total_ns} ns | results -> {size_bits}")

    avg_ns = int(statistics.mean(all_times))
    print(f"Average T over {rounds} rounds (single-threaded): {avg_ns} ns\n")
    return all_times, avg_ns


# ---------------------------------------------
# 4. Run both experiments
# ---------------------------------------------
if __name__ == "__main__":
    mt_times, mt_avg = run_multithreaded_factorials(10)
    st_times, st_avg = run_singlethread_factorials(10)

    print("=== Summary ===")
    print(f"Average (multithreading): {mt_avg} ns")
    print(f"Average (single-threaded): {st_avg} ns")
    print("\nNote: CPython threads do not achieve true parallelism for CPU-bound tasks due to the GIL.")
