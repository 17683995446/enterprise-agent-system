"""
Quick debug test to see what errors are happening
"""
import sys
import time
import random
import threading
from datetime import datetime

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.core.in_memory_data_storage_backend import InMemoryDataStorageBackend
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration
)
from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache


def main():
    print('=' * 80)
    print('Quick debug test')
    print('=' * 80)
    
    backend = InMemoryDataStorageBackend()
    store = SimpleMemoryStore()
    cache = SimpleCache()
    
    errors = []
    
    # Test 100 operations quickly
    for i in range(100):
        try:
            # Random operations
            op_type = random.choice(['task_create', 'memory_create', 'cache'])
            
            if op_type == 'task_create':
                task = backend.create_new_task_entry(
                    task_title=f"Task {i}",
                    priority_level=random.choice(list(TaskPriorityLevelEnumeration))
                )
                # Try to update
                backend.update_task_entry(
                    task.unique_entity_id,
                    execution_status=random.choice(list(TaskExecutionStatusEnumeration)),
                    progress_percentage_value=random.random()
                )
                
            elif op_type == 'memory_create':
                memory = backend.create_new_memory_entry(
                    content_text=f"Content {i}",
                    category_type=random.choice(list(MemoryCategoryTypeEnumeration)),
                    importance_score=random.randint(1, 5)
                )
                backend.retrieve_memory_by_id(memory.unique_memory_id)
                
            else:
                cache.set(f"key_{i}", f"value_{i}")
                cache.get(f"key_{random.randint(0, i)}")
                
        except Exception as e:
            errors.append((i, type(e).__name__, str(e)))
            import traceback
            print(f"ERROR at {i}: {type(e).__name__}: {e}")
            print(traceback.format_exc()[:300])
            if len(errors) >= 5:
                break
    
    print(f"\nDone. Total operations: 100, Errors: {len(errors)}")
    
    if errors:
        print("\nError details:")
        for i, err_type, err_msg in errors:
            print(f"  [{i}] {err_type}: {err_msg}")
    else:
        print("✓ No errors found!")


if __name__ == '__main__':
    main()
