"""
快速调试测试 - 知识图谱问题
"""

import sys

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.core.in_memory_data_storage_backend import InMemoryDataStorageBackend

# 创建后端
backend = InMemoryDataStorageBackend()

print("=== 调试：添加节点 ===")

# 尝试添加节点
try:
    node1 = backend.add_node_to_knowledge_graph("node1")
    print(f"✅ 节点1添加成功: {node1}")

    node2 = backend.add_node_to_knowledge_graph("node2")
    print(f"✅ 节点2添加成功: {node2}")

    # 添加边
    edge = backend.add_edge_to_knowledge_graph(node1, node2, "rel", 1.0)
    print(f"✅ 边添加成功: {edge}")

except Exception as e:
    print(f"❌ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# 检查统计
print("\n=== 检查统计 ===")
stats = backend.retrieve_knowledge_graph_statistics()
print(f"统计: {stats}")

# 手动查看内部存储（仅供调试）
print("\n=== 内部状态 ===")
try:
    print(f"_knowledge_graph_nodes keys: {list(backend._knowledge_graph_nodes.keys())}")
    print(f"_knowledge_graph_edges: {backend._knowledge_graph_edges}")
except Exception as e:
    print(f"无法直接访问: {e}")
