#!/usr/bin/env python3
"""
第一性原理极端测试 - 带详细日志
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 80)
print("STARTING FIRST-PRINCIPLES EXTREME TESTS WITH FULL LOGGING")
print("=" * 80)

from enterprise_agent_system.infrastructure.simple_memory_store_with_logging import (
    SimpleMemoryStore,
    SimpleCache
)

print("\n" * 3)
print("=" * 80)
print("TEST 1: SIMPLE CACHE BASIC OPERATION")
print("=" * 80)
cache = SimpleCache()

print("\n--- CACHE SET ---")
cache.set("test_key1", "value1")
cache.set("test_key2", "value2", ttl=100)
cache.set("test_key3", "value3", ttl=0)

print("\n--- CACHE GET ---")
print(f"cache.get('test_key1') = {cache.get('test_key1')}")
print(f"cache.get('test_key2') = {cache.get('test_key2')}")
print(f"cache.get('test_key3') = {cache.get('test_key3')}")
print(f"cache.get('non_existent') = {cache.get('non_existent')}")

print("\n--- CACHE EXISTS ---")
print(f"cache.exists('test_key1') = {cache.exists('test_key1')}")
print(f"cache.exists('non_existent') = {cache.exists('non_existent')}")

print("\n--- CACHE DELETE ---")
print(f"cache.delete('test_key1') = {cache.delete('test_key1')}")
print(f"cache.get('test_key1') after delete = {cache.get('test_key1')}")

print("\n--- CACHE STATS ---")
print(f"cache.get_stats() = {cache.get_stats()}")

print("\n" * 3)
print("=" * 80)
print("TEST 2: SIMPLE MEMORY STORE")
print("=" * 80)

store = SimpleMemoryStore()

print("\n--- STORE SAVE REPORT ---")
report_id1 = store.save_report({
    "title": "First Report",
    "type": "test",
    "content": "Test content 1",
    "quality_score": 8.5
})
print(f"store.save_report() returned report_id1 = {report_id1}")

report_id2 = store.save_report({
    "id": "manual_id_123",
    "title": "Second Report",
    "type": "test",
    "content": "Test content 2",
    "quality_score": 9.2,
    "metrics": {
        "counter": 10
    }
})
print(f"store.save_report() returned report_id2 = {report_id2}")

print("\n--- STORE GET REPORT ---")
print(f"store.get_report(report_id1) = {store.get_report(report_id1)}")
print(f"store.get_report(report_id2) = {store.get_report(report_id2)}")
print(f"store.get_report('invalid') = {store.get_report('invalid')}")

print("\n--- STORE LIST REPORTS ---")
reports = store.list_reports()
print(f"store.list_reports() returned {len(reports)} reports")
for i, r in enumerate(reports):
    print(f"  report {i+1}: {r.get('title')} (score: {r.get('quality_score')})")

print("\n--- STORE ATOMIC INCREMENT ---")
new_val = store.atomic_increment("manual_id_123", "metrics.counter", 5)
print(f"store.atomic_increment() returned new_value = {new_val}")
final_report = store.get_report("manual_id_123")
print(f"After increment: metrics.counter = {final_report.get('metrics', {}).get('counter')}")

print("\n--- STORE DELETE REPORT ---")
print(f"store.delete_report(report_id1) = {store.delete_report(report_id1)}")
print(f"store.get_report(report_id1) after delete = {store.get_report(report_id1)}")

print("\n--- STORE STATS ---")
print(f"store.get_stats() = {store.get_stats()}")

print("\n" * 3)
print("=" * 80)
print("TEST 3: CONCURRENCY")
print("=" * 80)

import threading
import time

results = []
error_count = 0
lock = threading.Lock()

def concurrent_task_worker(worker_id):
    global error_count
    try:
        store = SimpleMemoryStore()
        cache = SimpleCache()
        for i in range(10):
            report_id = store.save_report({
                "title": f"Worker {worker_id} Report {i}",
                "quality_score": 8.0
            })
            cache.set(f"w{worker_id}_k{i}", f"value_{i}")
            _ = store.get_report(report_id)
            _ = cache.get(f"w{worker_id}_k{i}")
        with lock:
            results.append(worker_id)
    except Exception as e:
        with lock:
            error_count += 1
        print(f"WORKER {worker_id} ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

threads = []
for i in range(10):
    t = threading.Thread(target=concurrent_task_worker, args=(i,))
    threads.append(t)

start_time = time.time()
for t in threads:
    t.start()

for t in threads:
    t.join()

end_time = time.time()

print(f"\nConcurrency test complete. {len(results)} workers completed. {error_count} errors.")
print(f"Time taken: {end_time - start_time:.3f} seconds")

print("\n" * 3)
print("=" * 80)
print("FIRST-PRINCIPLES TESTS FINISHED")
print("=" * 80)
