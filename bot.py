import requests
import logging
import time
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("🤖 Aadhar Bot - GET Method Fixed")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration
BOT_TOKEN = "8292852232:AAGk47XqZKocBTT3je-gco0NOPUr1I3TrC0"

# GET Method API endpoints
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
⚡ GET Method Fixed

📋 Send 12-digit Aadhar number to get information.

Example: 380468450193

Commands:
/start - Start bot
/help - Help guide  
/status - Check status
/test - Test APIs
        """
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
Help Guide:

1. Send 12-digit Aadhar number
2. System will try multiple APIs
3. Get best available results

Example: 123456789012

Commands:
/start - Start bot
/help - This message
/status - Check status
/test - Test APIs
        """
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uptime = time.time() - self.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        active_api_name = self.active_api if self.active_api else "Testing..."
        
        status_text = f"""
Bot Status:
✅ Active
⏰ Uptime: {hours}h {minutes}m
🌐 Active API: {active_api_name}
🔧 APIs Ready: {len(API_ENDPOINTS)}
        """
        await update.message.reply_text(status_text)

    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test all APIs"""
        testing_msg = await update.message.reply_text("🔧 Testing APIs...")
        
        results = []
        for api in API_ENDPOINTS:
            try:
                # Build URL with parameters for GET request
                params = api['params'].copy()
                params['aadhaar'] = '380468450193'
                
                # For GET request, we build the URL with query parameters
                url = api['url']
                if api['method'] == 'GET':
                    from urllib.parse import urlencode
                    query_string = urlencode(params)
                    full_url = f"{url}?{query_string}"
                else:
                    full_url = url
                
                print(f"Testing: {full_url}")
                
                response = requests.get(full_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and any(data.values()):
                        results.append(f"✅ {api['name']}: WORKING")
                        self.active_api = api['name']
                    else:
                        results.append(f"⚠️ {api['name']}: NO DATA")
                else:
                    results.append(f"❌ {api['name']}: FAILED ({response.status_code})")
                    
            except Exception as e:
                results.append(f"❌ {api['name']}: ERROR ({str(e)})")
        
        result_text = "API Test Results:\n\n" + "\n".join(results)
        await testing_msg.edit_text(result_text)
    
    async def handle_aadhar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        aadhar_number = update.message.text.strip()
        
        # Validation
        if not aadhar_number.isdigit():
            await update.message.reply_text("❌ Please send only numbers (0-9)")
            return
            
        if len(aadhar_number) != 12:
            await update.message.reply_text("❌ Aadhar must be exactly 12 digits\n\nExample: 380468450193")
            return
        
        await self.process_aadhar_multi_api(update, aadhar_number)
    
    async def process_aadhar_multi_api(self, update: Update, aadhar: str):
        """Try multiple APIs using GET method"""
        processing_msg = await update.message.reply_text("🔄 Processing your request...")
        
        best_data = None
        best_api_name = None
        
        for api in API_ENDPOINTS:
            try:
                # Build URL with parameters for GET request
                params = api['params'].copy()
                params['aadhaar'] = aadhar
                
                # Construct full URL for GET request
                url = api['url']
                if api['method'] == 'GET':
                    from urllib.parse import urlencode
                    query_string = urlencode(params)
                    full_url = f"{url}?{query_string}"
                else:
                    full_url = url
                
                print(f"Trying: {full_url}")
                
                response = requests.get(full_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if we got meaningful data
                    if self.has_meaningful_data(data):
                        best_data = data
                        best_api_name = api['name']
                        self.active_api = api['name']
                        break
                        
            except Exception as e:
                print(f"API Error: {e}")
                continue
        
        if best_data:
            await self.send_results(processing_msg, aadhar, best_data, best_api_name)
        else:
            await processing_msg.edit_text(
                f"❌ No information found for Aadhar: {aadhar}\n\n"
                "Possible reasons:\n"
                "• Aadhar number not in database\n"
                "• APIs temporarily down\n"
                "• Try different Aadhar number"
            )
    
    def has_meaningful_data(self, data):
        """Check if data has actual information"""
        if not data or not isinstance(data, dict):
            return False
        
        # Check for placeholder values
        placeholder_indicators = [
            'to be captured',
            'not available', 
            'n/a',
            'null',
            'undefined'
        ]
        
        for value in data.values():
            if value and isinstance(value, str):
                value_lower = value.lower()
                if any(indicator in value_lower for indicator in placeholder_indicators):
                    return False
        
        # Check if we have at least one non-empty field
        for value in data.values():
            if value and str(value).strip():
                return True
        
        return False
    
    async def send_results(self, processing_msg, aadhar: str, data: dict, api_name: str):
        """Send formatted results"""
        try:
            result_text = f"🔍 Aadhar: {aadhar}\n"
            result_text += f"🌐 Source: {api_name}\n\n"
            
            # Field mapping
            field_map = {
                'name': '👤 Name',
                'full_name': '👤 Full Name',
                'father_name': '👨 Father',
                'father': '👨 Father',
                'mother_name': '👩 Mother', 
                'mother': '👩 Mother',
                'dob': '🎂 Date of Birth',
                'date_of_birth': '🎂 Date of Birth',
                'address': '🏠 Address',
                'mobile': '📱 Mobile',
                'email': '📧 Email',
                'gender': '⚧ Gender',
                'age': '📅 Age'
            }
            
            found_data = False
            for field_key, field_display in field_map.items():
                if field_key in data and data[field_key] and str(data[field_key]).strip():
                    value = str(data[field_key])
                    # Skip placeholder values
                    if any(indicator in value.lower() for indicator in ['to be captured', 'not available']):
                        continue
                    
                    result_text += f"{field_display}: {data[field_key]}\n"
                    found_data = True
            
            if not found_data:
                # Show all available fields
                for key, value in data.items():
                    if value and str(value).strip():
                        display_name = ' '.join(word.capitalize() for word in key.split('_'))
                        result_text += f"{display_name}: {value}\n"
                        found_data = True
            
            if found_data:
                result_text += "\n✅ Information retrieved successfully"
            else:
                result_text += "❌ No meaningful data found"
            
            await processing_msg.edit_text(result_text)
            
        except Exception as e:
            await processing_msg.edit_text("✅ Request completed.")

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
            print("✅ Bot is running with GET method!")
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