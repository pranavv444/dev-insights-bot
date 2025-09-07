# test_apis.py
import os
from dotenv import load_dotenv
import requests
import google.generativeai as genai

load_dotenv()

print("Testing API connections...\n")

# Test GitHub
github_token = os.getenv("GITHUB_TOKEN")
github_owner = os.getenv("GITHUB_OWNER")

headers = {"Authorization": f"token {github_token}"}
response = requests.get(f"https://api.github.com/users/{github_owner}", headers=headers)

if response.status_code == 200:
    print("✅ GitHub API: Connected")
    print(f"   User: {response.json()['login']}")
else:
    print("❌ GitHub API: Failed")
    print(f"   Error: {response.status_code}")

# Test Gemini
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'API connected' in exactly 3 words")
    print("\n✅ Gemini API: Connected")
    print(f"   Response: {response.text}")
except Exception as e:
    print("\n❌ Gemini API: Failed")
    print(f"   Error: {str(e)}")

# Test Slack
slack_token = os.getenv("SLACK_BOT_TOKEN")
if slack_token and slack_token.startswith("xoxb-"):
    print("\n✅ Slack Token: Configured")
else:
    print("\n❌ Slack Token: Missing or invalid")