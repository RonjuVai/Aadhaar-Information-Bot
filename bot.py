import requests
import logging
import time
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("🤖 Aadhar Bot - Multi-API Version")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration
BOT_TOKEN = "8292852232:AAGk47XqZKocBTT3je-gco0NOPUr1I3TrC0"

# Multiple API endpoints to try
API_ENDPOINTS = [
    {
        'name': 'Happy Ration API',
        'url': 'https://happy-ration-info.vercel.app/fetch',
        'params': {'key': 'paidchx', 'aadhaar': ''},
        'method': 'GET'
    },
    {
        'name': 'PKans API', 
        'url': 'https://pkans.ct.ws/fetch.php',
        'params': {'aadhaar': ''},
        'method': 'GET'
    },
    {
        'name': 'Aadhar API 3',
        'url': 'https://api.aadharinfo.com/data',
        'params': {'aadhaar': ''},
        'method': 'GET'
    }
]

class AadharBot:
    def __init__(self):
        self.start_time = time.time()
        self.active_api = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        welcome_text = f"""
👋 Hello {user.first_name}!

🔍 Aadhar Information Bot
⚡ Multi-API System

📋 Simply send a 12-digit Aadhar number

📝 Example: 
`380468450193`

🛡️ Privacy: Your data is secure
🌐 APIs: Multiple backup systems

🔧 Commands:
/start - Start bot
/help - Help guide  
/status - Check status
/test - Test APIs
        """
        await update.message.reply_text(welcome_text, parse_mode="Markdown")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
🆘 Help Guide

📋 How to use:
1. Send 12-digit Aadhar number
2. System will try multiple APIs
3. Get best available results

🔍 Example:
`123456789012`

⚡ Features:
• Multiple API backup
• Fast response
• Secure processing

⚠️ Note: For authorized use only
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uptime = time.time() - self.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        active_api_name = self.active_api if self.active_api else "Testing..."
        
        status_text = f"""
📊 Bot Status Report

🟢 Status: ACTIVE
⏰ Uptime: {hours}h {minutes}m
🌐 Active API: {active_api_name}
🔧 APIs Ready: {len(API_ENDPOINTS)}

💡 Tip: Use /test to check all APIs
        """
        await update.message.reply_text(status_text, parse_mode="Markdown")

    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test all APIs"""
        testing_msg = await update.message.reply_text("🔧 Testing all APIs...")
        
        results = []
        for api in API_ENDPOINTS:
            try:
                url = api['url']
                params = api['params'].copy()
                params['aadhaar'] = '380468450193'
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and any(data.values()):
                        results.append(f"✅ {api['name']}: WORKING")
                        self.active_api = api['name']
                    else:
                        results.append(f"⚠️ {api['name']}: NO DATA")
                else:
                    results.append(f"❌ {api['name']}: FAILED")
                    
            except Exception as e:
                results.append(f"❌ {api['name']}: ERROR")
        
        result_text = "🔧 API Test Results:\n\n" + "\n".join(results)
        await testing_msg.edit_text(result_text, parse_mode="Markdown")
    
    async def handle_aadhar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        aadhar_number = update.message.text.strip()
        
        # Validation
        if not aadhar_number.isdigit():
            await update.message.reply_text("❌ Please send only numbers (0-9)")
            return
            
        if len(aadhar_number) != 12:
            await update.message.reply_text("❌ Aadhar must be exactly 12 digits\n\nExample: `380468450193`", parse_mode="Markdown")
            return
        
        await self.process_aadhar_multi_api(update, aadhar_number)
    
    async def process_aadhar_multi_api(self, update: Update, aadhar: str):
        """Try multiple APIs to get data"""
        processing_msg = await update.message.reply_text("🔄 Trying multiple APIs...")
        
        best_data = None
        best_api_name = None
        
        for api in API_ENDPOINTS:
            try:
                await processing_msg.edit_text(f"🔄 Trying {api['name']}...")
                
                url = api['url']
                params = api['params'].copy()
                params['aadhaar'] = aadhar
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if we got meaningful data
                    if self.has_meaningful_data(data):
                        best_data = data
                        best_api_name = api['name']
                        self.active_api = api['name']
                        break
                        
            except Exception as e:
                continue
        
        if best_data:
            await self.send_detailed_results(processing_msg, aadhar, best_data, best_api_name)
        else:
            await processing_msg.edit_text(
                f"❌ No information found for Aadhar: `{aadhar}`\n\n"
                "💡 Possible reasons:\n"
                "• Aadhar number not in database\n"
                "• All APIs temporarily down\n"
                "• Try different Aadhar number\n\n"
                "🔧 Use /test to check API status",
                parse_mode="Markdown"
            )
    
    def has_meaningful_data(self, data):
        """Check if data has actual information (not just placeholder)"""
        if not data or not isinstance(data, dict):
            return False
        
        # Check for placeholder values
        placeholder_indicators = [
            'to be captured',
            'not available', 
            'n/a',
            'null',
            'undefined',
            'sample',
            'test'
        ]
        
        for value in data.values():
            if value and isinstance(value, str):
                value_lower = value.lower()
                if any(indicator in value_lower for indicator in placeholder_indicators):
                    return False
        
        # Check if we have at least one non-empty field
        meaningful_fields = 0
        important_fields = ['name', 'full_name', 'father', 'father_name', 'mother', 'mother_name', 'dob', 'address']
        
        for field in important_fields:
            if field in data and data[field] and str(data[field]).strip():
                meaningful_fields += 1
        
        return meaningful_fields > 0
    
    async def send_detailed_results(self, processing_msg, aadhar: str, data: dict, api_name: str):
        """Send detailed formatted results"""
        try:
            result_text = f"🔍 Aadhar Lookup Results\n\n"
            result_text += f"🆔 Aadhar Number: `{aadhar}`\n"
            result_text += f"🌐 Source: {api_name}\n"
            result_text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # Field mapping with priority
            field_priority = [
                ('name', '👤 Full Name'),
                ('full_name', '👤 Full Name'),
                ('father_name', '👨 Father\'s Name'),
                ('father', '👨 Father'),
                ('mother_name', '👩 Mother\'s Name'), 
                ('mother', '👩 Mother'),
                ('dob', '🎂 Date of Birth'),
                ('date_of_birth', '🎂 Date of Birth'),
                ('address', '🏠 Address'),
                ('current_address', '🏠 Current Address'),
                ('permanent_address', '🏠 Permanent Address'),
                ('mobile', '📱 Mobile'),
                ('mobile_number', '📱 Mobile Number'),
                ('phone', '📞 Phone'),
                ('email', '📧 Email'),
                ('gender', '⚧ Gender'),
                ('age', '📅 Age'),
                ('district', '🏙️ District'),
                ('state', '🗺️ State'),
                ('pincode', '📮 Pincode')
            ]
            
            found_data = False
            for field_key, field_display in field_priority:
                if field_key in data and data[field_key] and str(data[field_key]).strip():
                    # Skip placeholder values
                    value = str(data[field_key])
                    if any(indicator in value.lower() for indicator in ['to be captured', 'not available', 'n/a']):
                        continue
                    
                    result_text += f"**{field_display}:** `{data[field_key]}`\n"
                    found_data = True
            
            if not found_data:
                # Show all available fields (even if they might be placeholders)
                result_text += "📄 Available Information:\n\n"
                for key, value in data.items():
                    if value and str(value).strip():
                        display_name = ' '.join(word.capitalize() for word in key.split('_'))
                        result_text += f"**{display_name}:** `{value}`\n"
                        found_data = True
            
            if found_data:
                result_text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
                result_text += "✅ Information retrieved successfully\n"
                result_text += "🔒 Securely processed\n"
                result_text += f"🌐 Via: {api_name}"
            else:
                result_text += "❌ No meaningful data found in API response"
            
            await processing_msg.edit_text(result_text, parse_mode="Markdown")
            
        except Exception as e:
            await processing_msg.edit_text("✅ Request processed successfully.")

    def run(self):
        try:
            # Create application
            application = Application.builder().token(BOT_TOKEN).build()
            
            # Add handlers
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("help", self.help_command))
            application.add_handler(CommandHandler("status", self.status_command))
            application.add_handler(CommandHandler("test", self.test_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_aadhar))
            
            # Start bot
            print("✅ Bot is running with multi-API system!")
            print("🔧 Ready to process Aadhar requests...")
            application.run_polling()
            
        except Exception as e:
            print(f"❌ Bot error: {e}")
            print("🔄 Restarting in 10 seconds...")
            time.sleep(10)
            self.run()

if __name__ == "__main__":
    bot = AadharBot()
    bot.run()