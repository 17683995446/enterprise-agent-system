"""
Very short version of the extreme test to capture errors
"""
import sys
import time
import random
import threading
import gc
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance
from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
from enterprise_agent_system.core.in_memory_data_storage_backend import InMemoryDataStorageBackend
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration
)


def test_error_capture():
    print('=' * 80)
    print('Short error capture test')
    print('=' * 80)
    
    backend = InMemoryDataStorageBackend()
    store = SimpleMemoryStore()
    cache = SimpleCache()
    
    errors = []
    lock = threading.Lock()
    
    def worker(thread_id):
        for i in range(20):  # Only 20 iterations per thread
            try:
                op_type = random.choice(['create_task', 'update_task', 'create_memory', 'list_pending'])
                
                if op_type == 'create_task':
                    task = backend.create_new_task_entry(
                        task_title=f"T{thread_id}-{i}",
                        priority_level=random.choice(list(TaskPriorityLevelEnumeration))
                    )
                elif op_type == 'update_task':
                    tasks = backend.retrieve_all_tasks()
                    if tasks:
                        task = random.choice(tasks)
                        backend.update_task_entry(
                            task.unique_entity_id,
                            execution_status=random.choice(list(TaskExecutionStatusEnumeration)),
                            progress_percentage_value=random.random()
                        )
                elif op_type == 'create_memory':
                    backend.create_new_memory_entry(
                        content_text=f"Mem{thread_id}-{i}",
                        category_type=random.choice(list(MemoryCategoryTypeEnumeration)),
                        importance_score=random.randint(1, 5)
                    )
                else:  # list_pending
                    backend.retrieve_pending_tasks_sorted_by_priority()
                    
            except Exception as e:
                with lock:
                    import traceback
                    errors.append({
                        'thread': thread_id,
                        'iter': i,
                        'type': type(e).__name__,
                        'msg': str(e),
                        'traceback': traceback.format_exc()
                    })
                    if len(errors) <= 3:
                        print(f"ERROR from thread {thread_id}: {type(e).__name__}: {e}")
    
    # Start 5 threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"\nDone! Total errors: {len(errors)}")
    
    if errors:
        print("\n" + "=" * 80)
        print("ERROR DETAILS")
        print("=" * 80)
        for i, err in enumerate(errors[:5]):  # Show first 5 errors
            print(f"\nERROR {i+1}:")
            print(f"  Thread: {err['thread']}")
            print(f"  Type: {err['type']}")
            print(f"  Message: {err['msg']}")
            print(f"  Traceback:")
            print(err['traceback'][:500])
    else:
        print("\n✓ No errors! Great success!")


if __name__ == '__main__':
    test_error_capture()
