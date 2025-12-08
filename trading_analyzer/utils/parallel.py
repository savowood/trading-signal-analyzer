"""
Parallel Processing Utilities
High-performance concurrent analysis for scanners
"""
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import List, Callable, Any, Optional
import multiprocessing
from dataclasses import dataclass


@dataclass
class ParallelConfig:
    """Configuration for parallel processing"""
    max_workers: int = None  # None = auto-detect CPU count
    use_processes: bool = True  # False = use threads instead
    timeout: Optional[int] = 60  # Timeout per task in seconds
    show_progress: bool = True


class ParallelProcessor:
    """
    High-performance parallel processing for ticker analysis

    Uses multiprocessing for CPU-bound tasks (analysis)
    Can fall back to threading for I/O-bound tasks
    """

    def __init__(self, config: Optional[ParallelConfig] = None):
        self.config = config or ParallelConfig()

        # Auto-detect optimal worker count if not specified
        if self.config.max_workers is None:
            cpu_count = multiprocessing.cpu_count()
            # Use 75% of CPUs, leave some for system
            self.config.max_workers = max(1, int(cpu_count * 0.75))

    def process_tickers(self,
                       tickers: List[str],
                       process_func: Callable,
                       *args,
                       **kwargs) -> List[Any]:
        """
        Process multiple tickers in parallel

        Args:
            tickers: List of ticker symbols
            process_func: Function to call for each ticker (must accept ticker as first arg)
            *args, **kwargs: Additional arguments passed to process_func

        Returns:
            List of results (None for failed tickers)
        """
        results = []

        # Choose executor type
        executor_class = ProcessPoolExecutor if self.config.use_processes else ThreadPoolExecutor

        with executor_class(max_workers=self.config.max_workers) as executor:
            # Submit all tasks
            future_to_ticker = {
                executor.submit(self._safe_execute, process_func, ticker, *args, **kwargs): ticker
                for ticker in tickers
            }

            # Collect results as they complete
            completed = 0
            total = len(tickers)

            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                completed += 1

                try:
                    result = future.result(timeout=self.config.timeout)
                    if result is not None:
                        results.append(result)

                    # Progress indicator
                    if self.config.show_progress and completed % 10 == 0:
                        print(f"   [{completed}/{total}] Processed {ticker}...", end='\r')

                except Exception as e:
                    # Log error but continue processing
                    if self.config.show_progress:
                        print(f"   ⚠️  Failed to process {ticker}: {str(e)[:50]}")

        if self.config.show_progress:
            print(f"\n   ✅ Completed {len(results)}/{total} tickers")

        return results

    @staticmethod
    def _safe_execute(func: Callable, ticker: str, *args, **kwargs) -> Optional[Any]:
        """
        Safely execute function with error handling

        This method runs in a separate process/thread
        """
        try:
            return func(ticker, *args, **kwargs)
        except Exception as e:
            # Return None on error (will be filtered out)
            return None

    def process_batch(self,
                     items: List[Any],
                     process_func: Callable,
                     batch_size: int = 100) -> List[Any]:
        """
        Process items in batches for memory efficiency

        Args:
            items: List of items to process
            process_func: Function to process each item
            batch_size: Items per batch

        Returns:
            Combined results from all batches
        """
        all_results = []

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]

            if self.config.show_progress:
                batch_num = (i // batch_size) + 1
                total_batches = (len(items) + batch_size - 1) // batch_size
                print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} items)...")

            batch_results = self.process_tickers(batch, process_func)
            all_results.extend(batch_results)

        return all_results


def parallel_analyze(tickers: List[str],
                    analyze_func: Callable,
                    max_workers: Optional[int] = None,
                    show_progress: bool = True) -> List[Any]:
    """
    Convenience function for parallel ticker analysis

    Args:
        tickers: List of ticker symbols
        analyze_func: Analysis function (takes ticker as first arg)
        max_workers: Number of parallel workers (None = auto)
        show_progress: Show progress indicators

    Returns:
        List of analysis results

    Example:
        >>> def analyze_ticker(ticker):
        ...     return scanner.analyze_ticker(ticker)
        >>> results = parallel_analyze(['AAPL', 'TSLA', 'GME'], analyze_ticker)
    """
    config = ParallelConfig(
        max_workers=max_workers,
        use_processes=True,
        show_progress=show_progress
    )

    processor = ParallelProcessor(config)
    return processor.process_tickers(tickers, analyze_func)


# Test function
if __name__ == "__main__":
    import time

    def mock_analyze(ticker):
        """Mock analysis function"""
        time.sleep(0.5)  # Simulate analysis time
        return {'ticker': ticker, 'score': 75}

    print("Testing parallel processing...")
    test_tickers = ['AAPL', 'TSLA', 'GME', 'AMC', 'NVDA', 'MSFT', 'GOOGL', 'META']

    # Sequential (baseline)
    start = time.time()
    sequential_results = [mock_analyze(t) for t in test_tickers]
    sequential_time = time.time() - start

    # Parallel
    start = time.time()
    parallel_results = parallel_analyze(test_tickers, mock_analyze)
    parallel_time = time.time() - start

    print(f"\n📊 Performance Comparison:")
    print(f"   Sequential: {sequential_time:.2f}s")
    print(f"   Parallel:   {parallel_time:.2f}s")
    print(f"   Speedup:    {sequential_time/parallel_time:.2f}x")
