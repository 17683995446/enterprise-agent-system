"""
验证修复后的API端点是否正常工作
"""

import sys
from pathlib import Path

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

print("=" * 80)
print("验证API修复")
print("=" * 80)

# 1. 测试导入是否正常
print("\n1. 测试模块导入...")
try:
    from enterprise_agent_system.infrastructure.api_unified_models import ApiResponse, ResponseStatus, ErrorCode
    from enterprise_agent_system.infrastructure.error_handling import AppError, EnterpriseAgentError
    from enterprise_agent_system.infrastructure.api.api_server import app
    print("   ✅ 模块导入成功")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    sys.exit(1)

# 2. 测试 ApiResponse 类
print("\n2. 测试 ApiResponse 类...")
try:
    response1 = ApiResponse.success(data={"test": "ok"})
    print(f"   ✅ success 响应创建: {response1.status}")

    response2 = ApiResponse.error(error_code=ErrorCode.INTERNAL_ERROR, message="test error")
    print(f"   ✅ error 响应创建: {response2.status}")

    print(f"   ✅ model_dump() 方法可用: {len(response1.model_dump())} 字段")
except Exception as e:
    print(f"   ❌ ApiResponse 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 测试 FastAPI 客户端
print("\n3. 测试 FastAPI 端点...")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)

    # 测试根端点
    print("\n   测试 GET /...")
    response = client.get("/")
    print(f"   状态码: {response.status_code}")

    if response.status_code == 200:
        print(f"   ✅ 根端点正常")
        data = response.json()
        print(f"   响应: {data}")
    else:
        print(f"   ❌ 根端点失败: {response.text}")

    # 测试健康检查
    print("\n   测试 GET /health...")
    response = client.get("/health")
    print(f"   状态码: {response.status_code}")

    if response.status_code == 200:
        print(f"   ✅ 健康检查正常")
        data = response.json()
        print(f"   响应: {data}")
    else:
        print(f"   ❌ 健康检查失败: {response.text}")

except Exception as e:
    print(f"   ❌ API 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("验证完成")
print("=" * 80)