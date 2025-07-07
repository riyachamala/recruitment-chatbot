#!/usr/bin/env python3
"""
Setup script for the Resume Chatbot project.
This script helps with initial project setup and resume ingestion.
"""

import os
import sys
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists and has required variables."""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("📝 Please copy .env.example to .env and fill in your API keys:")
        print("   cp .env.example .env")
        return False
    
    load_dotenv()
    required_vars = ['PINECONE_API_KEY', 'INDEX_NAME', 'GROQ_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("📝 Please set these variables in your .env file")
        return False
    
    print("✅ Environment variables configured")
    return True

def check_resumes_folder():
    """Check if resumes folder exists and has PDF files."""
    if not os.path.exists('resumes'):
        print("📁 Creating resumes folder...")
        os.makedirs('resumes')
        print("📄 Please add your resume PDF files to the 'resumes/' folder")
        return False
    
    pdf_files = [f for f in os.listdir('resumes') if f.endswith('.pdf')]
    if not pdf_files:
        print("❌ No PDF files found in resumes/ folder")
        print("📄 Please add resume PDF files to the 'resumes/' folder")
        return False
    
    print(f"✅ Found {len(pdf_files)} resume PDF files")
    for pdf in pdf_files:
        print(f"   📄 {pdf}")
    return True

def run_ingestion():
    """Run the resume ingestion process."""
    print("\n🔄 Running resume ingestion...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'ingestion.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Resume ingestion completed successfully!")
            print(result.stdout)
        else:
            print("❌ Resume ingestion failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running ingestion: {e}")
        return False
    return True

def main():
    print("🚀 Resume Chatbot Setup")
    print("="*40)
    
    # Check environment setup
    if not check_env_file():
        return
    
    # Check resumes folder
    if not check_resumes_folder():
        return
    
    # Ask user if they want to run ingestion
    response = input("\n🤔 Do you want to run resume ingestion now? (y/n): ").lower().strip()
    if response == 'y' or response == 'yes':
        if run_ingestion():
            print("\n🎉 Setup completed successfully!")
            print("\n📋 Next steps:")
            print("1. Start backend: python start_backend.py")
            print("2. Start frontend: npm run dev")
            print("3. Open http://localhost:3000 in your browser")
        else:
            print("\n❌ Setup completed with errors. Please check the ingestion process.")
    else:
        print("\n⚠️  Setup completed, but you'll need to run ingestion manually:")
        print("   python ingestion.py")

if __name__ == "__main__":
    main()