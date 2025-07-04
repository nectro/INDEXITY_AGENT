#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Letwrk AI Agent - FastAPI Server Entry Point
"""

import uvicorn
import os
from src.api.app import app

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    print("🚀 Starting Letwrk AI Agent API Server...")
    print(f"🌐 Server will run on: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/api/v1/health")
    print(f"🔄 Auto-reload: {reload}")
    print()
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    ) 