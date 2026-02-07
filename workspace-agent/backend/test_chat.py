import requests
import json

BASE_URL = "http://localhost:8000"

def test_chat(query):
    """Test chat endpoint"""
    print(f"\n💬 You: {query}")
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"query": query},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"🤖 Agent: {data['response']}\n")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def get_eod_report():
    """Get EOD report"""
    print("\n📊 Fetching EOD Report...\n")
    
    response = requests.get(f"{BASE_URL}/api/eod-report")
    
    if response.status_code == 200:
        data = response.json()
        if 'content' in data and data['content']:
            print(f"📝 Report for {data['date']}:")
            print(f"\n{data['content']}\n")
        else:
            print("No report available yet.")
    else:
        print(f"❌ Error: {response.status_code}")

def trigger_report():
    """Manually trigger EOD report generation"""
    print("\n🔄 Generating new EOD report...")
    
    response = requests.post(f"{BASE_URL}/api/eod-report/generate")
    
    if response.status_code == 200:
        print("✅ Report generated!")
    else:
        print(f"❌ Error: {response.status_code}")

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 WORKSPACE AGENT TEST SUITE".center(60))
    print("=" * 60)
    
    # Test 1: Trigger report
    trigger_report()
    
    # Test 2: Get report
    get_eod_report()
    
    # Test 3: Chat
    test_chat("What emails do I need to respond to?")
    test_chat("What's due this week?")
    test_chat("Summarize my day")