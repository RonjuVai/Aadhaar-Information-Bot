import os
import requests
import json
import logging
import time
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("🚀 Aadhar Bot - New API Version")
print("🔧 Using new API endpoint...")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "8292852232:AAGk47XqZKocBTT3je-gco0NOPUr1I3TrC0"
API_BASE_URL = "https://happy-ration-info.vercel.app/fetch"
API_KEY = "paidchx"

def test_new_api():
    """Test the new API connection"""
    try:
        test_aadhaar = "380468450193"
        url = f"{API_BASE_URL}?key={API_KEY}&aadhaar={test_aadhaar}"
        
        print(f"🔍 Testing API: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📡 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ New API Test Successful!")
            print(f"📊 API Response: {json.dumps(data, indent=2)[:500]}...")
            return True, data
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"🔧 Response Text: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print(f"❌ API Test Failed: {e}")
        return False, None

# Test the new API
api_working, test_data = test_new_api()
print(f"🌐 New API Status: {'✅ WORKING' if api_working else '❌ NOT WORKING'}")

class NewAadharBot:
    def __init__(self):
        self.request_count = 0
        self.success_count = 0
        self.start_time = time.time()
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        welcome_text = f"""
👋 Hello {user.first_name}!

🔍 Aadhar Information Bot
🚀 Powered by New API

📋 Simply send a 12-digit Aadhar number to get information.

📝 Example: 
`380468450193`

⚡ Features:
• Fast API Response
• Secure Connection
• Real-time Data

🔧 Commands:
/start - Start bot
/help - Help guide  
/status - Check status
/test - Test API

🌐 API Status: {'✅ Working' if api_working else '❌ Down'}
        """
        await update.message.reply_text(welcome_text, parse_mode="Markdown")
        logger.info(f"User {user.first_name} started bot")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
🆘 Help Guide

📋 How to use:
1. Send 12-digit Aadhar number
2. Wait for processing
3. Get detailed information

🔍 Example:
`123456789012`

📊 Current Status:
• Bot: ✅ Running
• API: {'✅ Operational' if api_working else '❌ Maintenance'}
• Service: 24/7

⚠️ Note: Use only for authorized testing
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uptime = time.time() - self.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        status_text = f"""
📊 Bot Status Report

🟢 Status: ACTIVE
⏰ Uptime: {hours}h {minutes}m
📈 Requests: {self.request_count}
✅ Success: {self.success_count}
🌐 API: {'✅ CONNECTED' if api_working else '❌ DISCONNECTED'}

💾 System:
• Server: Railway
• Version: 4.0
• New API: Enabled
        """
        await update.message.reply_text(status_text, parse_mode="Markdown")

    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test the API connection"""
        testing_msg = await update.message.reply_text(
            "🔧 Testing API Connection...\n\n"
            "Please wait while we test the new API...",
            parse_mode="Markdown"
        )
        
        api_working, test_data = test_new_api()
        
        if api_working:
            result_text = f"""
✅ API Test Successful!

🌐 New API: Working Perfectly
📡 Response: Fast & Stable
🔒 Connection: Secure

📊 Test Data Preview:
```json
{json.dumps(test_data, indent=2)[:400]}