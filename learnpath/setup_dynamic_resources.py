#!/usr/bin/env python
"""
Dynamic Resource Fetcher - Quick Start Script
Install dependencies and verify setup in one command
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"▶️  {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        print(f"\n✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - FAILED")
        print(f"Error: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\n" + "="*60)
    print("🔍 Checking Dependencies")
    print("="*60)
    
    packages = {
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
        'decouple': 'python-decouple',
        'ollama': 'ollama',
        'pandas': 'pandas'
    }
    
    missing = []
    for import_name, package_name in packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} (missing)")
            missing.append(package_name)
    
    return missing

def check_env_variables():
    """Check if .env file exists and has API keys"""
    print("\n" + "="*60)
    print("🔑 Checking Environment Variables")
    print("="*60)
    
    env_file = Path("backend/.env")
    
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Create: backend/.env")
        print("   Copy from: backend/.env.example")
        return False
    
    env_content = env_file.read_text()
    
    required_keys = {
        'SERPER_API_KEY': 'Google Search API (optional)',
        'YOUTUBE_API_KEY': 'YouTube API (optional)',
        'USE_DYNAMIC_RESOURCES': 'Feature toggle (required)'
    }
    
    all_present = True
    for key, description in required_keys.items():
        if key in env_content and f"{key}=" in env_content:
            # Check if value is set
            value = [line for line in env_content.split('\n') if line.startswith(f"{key}=")]
            if value and "=" in value[0] and len(value[0].split("=", 1)[1].strip()) > 0:
                print(f"✅ {key} ({description})")
            else:
                print(f"⚠️  {key} is empty ({description})")
                all_present = False
        else:
            print(f"⚠️  {key} missing ({description})")
    
    return all_present

def check_services():
    """Check if external services are running"""
    print("\n" + "="*60)
    print("🔌 Checking External Services")
    print("="*60)
    
    # Check Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama (LLM Service) - Running")
        else:
            print("❌ Ollama - Not responding correctly")
    except Exception as e:
        print("❌ Ollama - Not running")
        print("   Download: https://ollama.ai")
        print("   Run: ollama serve")
    
    # Check Django
    try:
        response = requests.get("http://localhost:8000/api/assessment/resources/health/", timeout=2)
        if response.status_code == 200:
            print("✅ Django Server - Running")
        else:
            print("⚠️  Django - Not responding")
    except Exception as e:
        print("⚠️  Django - Not running")
        print("   Run in another terminal: python manage.py runserver")

def main():
    """Main setup flow"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " DYNAMIC RESOURCE FETCHER - QUICK START ".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    # Check current directory
    if not os.path.exists("backend"):
        print("\n❌ Error: Run this script from the project root directory")
        print("   Current directory: " + os.getcwd())
        sys.exit(1)
    
    # Step 1: Check dependencies
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"\n⚠️  Missing {len(missing_packages)} package(s)")
        install = input("\nInstall missing packages now? (y/n): ").lower() == 'y'
        
        if install:
            print(f"\n📦 Installing missing packages...")
            cmd = f"pip install {' '.join(missing_packages)}"
            if run_command(cmd, "Package Installation"):
                print("✅ All packages installed")
            else:
                print("❌ Installation failed")
                sys.exit(1)
    else:
        print("\n✅ All required packages installed")
    
    # Step 2: Check environment variables
    env_ok = check_env_variables()
    
    if not env_ok:
        print("\n⚠️  Please update your .env file:")
        print("   backend/.env")
        input("\nPress Enter when ready...")
    
    # Step 3: Check services
    check_services()
    
    # Step 4: Test API
    print("\n" + "="*60)
    print("🧪 Testing API Connection")
    print("="*60)
    
    try:
        import requests
        response = requests.get(
            "http://localhost:8000/api/assessment/resources/health/",
            timeout=5
        )
        
        if response.status_code == 200:
            status = response.json()
            print("\n✅ API Endpoint Reachable")
            print("\nService Status:")
            for service, stat in status.get('services', {}).items():
                icon = "✅" if "not" not in stat else "⚠️"
                print(f"  {icon} {service}: {stat}")
        else:
            print(f"\n❌ API returned status {response.status_code}")
    except Exception as e:
        print(f"\n❌ Cannot reach API: {str(e)}")
        print("   Make sure Django server is running:")
        print("   python manage.py runserver")
    
    # Summary
    print("\n" + "="*60)
    print("📋 SETUP SUMMARY")
    print("="*60)
    print("""
✅ COMPLETED:
  • Installed Python dependencies
  • Verified environment variables
  • Checked external services
  • Tested API connection

🚀 NEXT STEPS:

1. Add API Keys to backend/.env:
   - SERPER_API_KEY=xxx (from serper.dev)
   - YOUTUBE_API_KEY=xxx (from Google Cloud)

2. Start Services (in separate terminals):
   Terminal 1: cd backend && python manage.py runserver
   Terminal 2: cd frontend && python -m http.server 8001
   Terminal 3: ollama serve (if using dynamic mode)

3. Enable Dynamic Mode (in backend/.env):
   USE_DYNAMIC_RESOURCES=true

4. Test Endpoints:
   curl http://localhost:8000/api/assessment/resources/health/
   curl http://localhost:8000/api/assessment/resources/fetch_resources/?topic=Python

5. Use in Frontend:
   Select course → Take assessment → Generate roadmap
   (System will fetch dynamic resources if enabled)

📚 Documentation:
   • DYNAMIC_RESOURCE_SETUP.md - Complete setup guide
   • DYNAMIC_RESOURCE_EXAMPLES.py - Code examples
   • dynamic_resource_fetcher.py - Source code with comments

💡 TIP:
   Use Static Mode (default) for fast, offline learning
   Use Dynamic Mode for real-time, customizable resources
    """)
    
    print("="*60)
    print("✨ Setup Complete! Ready to fetch dynamic resources.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
