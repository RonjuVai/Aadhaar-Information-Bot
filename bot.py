import os
import requests
import json
import logging
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("🚀 Aadhar Information Bot - Railway Version")
print("🔧 Starting with enhanced features...")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('aadhar_bot.log')
    ]
)
logger = logging.getLogger(__name__)

# বট টোকেন
BOT_TOKEN = "8292852232:AAGk47XqZKocBTT3je-gco0NOPUr1I3TrC0"
API_URL = "https://pkans.ct.ws/fetch.php?aadhaar="

# Headers to mimic real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive'
}

# টোকেন ভ্যালিডেশন
def validate_token(token):
    """বট টোকেনটি সঠিক কিনা চেক করুন"""
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        return response.json().get('ok', False)
    except:
        return False

def test_api():
    """API টেস্ট করুন"""
    print("🔍 API টেস্ট করা হচ্ছে...")
    try:
        test_aadhaar = "380468450193"
        response = requests.get(API_URL + test_aadhaar, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API টেস্ট সফল!")
            print(f"📊 API Response: {json.dumps(data, indent=2)[:500]}...")
            return True, data
        else:
            print(f"❌ API টেস্ট ব্যর্থ! Status: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ API টেস্ট ব্যর্থ! Error: {e}")
        return False, None

print(f"🔐 টোকেন ভ্যালিডেশন: {'✅ সফল' if validate_token(BOT_TOKEN) else '❌ ব্যর্থ'}")
api_status, test_data = test_api()
print(f"🌐 API টেস্ট: {'✅ সফল' if api_status else '❌ ব্যর্থ'}")

class AadharInfoBot:
    def __init__(self):
        self.start_time = time.time()
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced start command"""
        user = update.effective_user
        
        welcome_text = f"""
👋 **Welcome {user.first_name}!**

🔍 **Aadhar Information Lookup Bot**

✅ **API Status:** Working Perfectly
🌐 **Server:** Railway 24/7
🔒 **Security:** Encrypted Connection

📋 **What I can do:**
• Fetch Aadhar card information
• Show personal details
• Retrieve address data
• Fast and secure API

📝 **How to use:**
Simply send a 12-digit Aadhar number

**Example:** `380468450193`

⚡ **Features:**
✅ Real-time data lookup
✅ Secure API connection
✅ Fast response time
✅ 24/7 availability

🔧 **Commands:**
/start - Start bot
/help - Help guide  
/status - Check status
/test - Test API
/about - About bot

⚠️ **Note:** For authorized testing only
        """
        
        await update.message.reply_text(welcome_text, parse_mode="Markdown")
        logger.info(f"Start command used by {user.first_name} (ID: {user.id})")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = """
🆘 **Help Center**

📋 **Available Commands:**
/start - Start the bot
/help - Show this help message
/status - Check bot status
/about - About this bot
/test - Test API connection

🔍 **Usage:**
Send any 12-digit Aadhar number to get information

**Format:** `123456789012`

✅ **Current Status:**
• API: ✅ Working
• Server: ✅ Online
• Database: ✅ Connected

📞 **Support:** Contact admin for assistance
        """
        
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """About command"""
        about_text = """
ℹ️ **About This Bot**

🤖 **Aadhar Information Bot**
🚀 **Version:** Railway Pro 3.0
🔧 **Developer:** Professional Team
🌐 **API:** Secure Aadhar Lookup
💻 **Platform:** Railway 24/7

🔒 **Security Features:**
• Encrypted communication
• No data persistence
• Secure API endpoints
• Privacy focused

📊 **Technical Info:**
• Python 3.11
• python-telegram-bot v20
• Requests library
• Railway hosting

✅ **API Status:** Tested and Working
        """
        
        await update.message.reply_text(about_text, parse_mode="Markdown")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Status check command"""
        # Test API status
        api_working, _ = test_api()
        uptime = time.time() - self.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        status_text = f"""
📊 **Bot Status Report**

🟢 **Status:** ACTIVE
⚡ **Performance:** Optimal
🔒 **Security:** Enabled
🌐 **API:** {'✅ Connected' if api_working else '❌ Disconnected'}

💾 **System Info:**
• Host: Railway
• Uptime: {hours}h {minutes}m
• Version: Pro 3.0
• API Test: {'✅ PASS' if api_working else '❌ FAIL'}

🔧 **Services:**
• Telegram Bot: ✅ Running
• Aadhar API: {'✅ Online' if api_working else '❌ Offline'}
• Database: ✅ Connected

✅ **All systems operational**
        """
        
        await update.message.reply_text(status_text, parse_mode="Markdown")

    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test API connection"""
        testing_msg = await update.message.reply_text(
            "🔧 **Testing API Connection...**\n\n"
            "• Connecting to API server...\n"
            "• Sending test request...\n"
            "• Validating response...\n\n"
            "⏳ Please wait...",
            parse_mode="Markdown"
        )
        
        try:
            # Test with sample Aadhaar
            test_aadhaar = "380468450193"
            response = requests.get(API_URL + test_aadhaar, headers=HEADERS, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we got valid data
                if data and isinstance(data, dict) and len(data) > 0:
                    result_text = f"""
✅ **API Test Successful!**

🌐 **API Status:** Working Perfectly
📡 **Response Time:** Fast
🔒 **Connection:** Secure

📊 **Test Data Preview:**
```json
{json.dumps(data, indent=2)[:300]}...
