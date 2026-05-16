#!/usr/bin/env python3
"""
Startup script for Enterprise Agent System API server
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from enterprise_agent_system.infrastructure.api import start_api_server

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Enterprise Agent System - API Server")
    print("=" * 80)
    print()
    print("📖 API Documentation:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc:      http://localhost:8000/redoc")
    print()
    start_api_server(host="0.0.0.0", port=8000)
