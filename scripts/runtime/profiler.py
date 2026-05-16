import time
import logging
import functools

logger = logging.getLogger("EGC.Profiler")

class PROFILER:
    """
    EGC Profiler
    Measures execution latency and overhead of orchestration components.
    """
    
    def __init__(self):
        self.metrics = []

    def record(self, component: str, operation: str, duration_ms: float):
        metric = {
            "timestamp": time.time(),
            "component": component,
            "operation": operation,
            "duration_ms": duration_ms
        }
        self.metrics.append(metric)
        logger.debug(f"PROFILER: {component}.{operation} took {duration_ms:.2f}ms")
        
    def summary(self):
        logger.info(f"--- Profiler Summary ({len(self.metrics)} events) ---")
        summary_map = {}
        for m in self.metrics:
            key = f"{m['component']}.{m['operation']}"
            if key not in summary_map:
                summary_map[key] = []
            summary_map[key].append(m['duration_ms'])
            
        for k, v in summary_map.items():
            avg = sum(v) / len(v)
            logger.info(f"{k}: Avg {avg:.2f}ms (Count: {len(v)})")
            
def profile_sync(component: str, operation: str):
    """Decorator for profiling synchronous functions"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Assumes the first arg is 'self' and it has a 'profiler' attribute if available
            start = time.perf_counter()
            res = func(*args, **kwargs)
            duration = (time.perf_counter() - start) * 1000
            
            # Simple fallback to global profiler for testing
            global_profiler.record(component, operation, duration)
            return res
        return wrapper
    return decorator

def profile_async(component: str, operation: str):
    """Decorator for profiling asynchronous functions"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            res = await func(*args, **kwargs)
            duration = (time.perf_counter() - start) * 1000
            
            global_profiler.record(component, operation, duration)
            return res
        return wrapper
    return decorator

global_profiler = PROFILER()
