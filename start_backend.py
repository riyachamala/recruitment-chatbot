#!/usr/bin/env python3
"""
Simple script to start the FastAPI backend server for the resume chatbot.
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("🚀 Starting Resume Chatbot Backend...")
    print("📡 API will be available at: http://localhost:8000")
    print("📋 API docs will be available at: http://localhost:8000/docs")
    print("🔧 Make sure your .env file is configured with API keys!")
    print("="*50)
    
    uvicorn.run(
        "api:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )