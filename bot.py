import os
import requests
import json
import logging
import time
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("🚀 Aadhar Bot - Fixed Version")
print("🔧 Testing API connection...")

# Simple logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "8292852232:AAGk47XqZKocBTT3je-gco0NOPUr1I3TrC0"
API_URL = "https://pkans.ct.ws/fetch.php"

def test_api_connection():
    """Test if API is working"""
    try:
        test_data = {"aadhaar": "380468450193"}
        response = requests.post(API_URL, data=test_data, timeout=10)
        print(f"🔍 API Test - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Connection Successful!")
            print(f"📊 Response: {data}")
            return True
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ API Connection Failed: {e}")
        return False

# Test API before starting
api_working = test_api_connection()
print(f"🌐 API Status: {'✅ WORKING' if api_working else '❌ BROKEN'}")

class SimpleAadharBot:
    def __init__(self):
        self.user_requests = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        welcome_text = f"""
👋 Hello {user.first_name}!

📋 Aadhar Information Bot

Simply send a 12-digit Aadhar number to get information.

Example: 380468450193

🔧 Commands:
/start - Start bot
/help - Help guide
/status - Check status
        """
        await update.message.reply_text(welcome_text)
        logger.info(f"User {user.first_name} started bot")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
📖 Help Guide:

1. Send 12-digit Aadhar number
2. Wait for processing
3. Receive information

Example: 123456789012

Note: API might be slow sometimes
        """
        await update.message.reply_text(help_text)

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        status_text = f"""
📊 Bot Status:

✅ Bot: Running
🌐 API: {'✅ Working' if api_working else '❌ Down'}
🔄 Requests: {len(self.user_requests)}
        """
        await update.message.reply_text(status_text)

    async def handle_aadhar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        aadhar_number = update.message.text.strip()
        
        logger.info(f"User {user.first_name} requested Aadhar: {aadhar_number}")
        
        # Basic validation
        if not aadhar_number.isdigit() or len(aadhar_number) != 12:
            await update.message.reply_text("❌ Please send a valid 12-digit Aadhar number")
            return
        
        # Store request
        self.user_requests[user.id] = aadhar_number
        
        # Process the request
        await self.process_aadhar_request(update, aadhar_number)
    
    async def process_aadhar_request(self, update: Update, aadhar: str):
        """Process Aadhar request with better error handling"""
        try:
            # Send processing message
            processing_msg = await update.message.reply_text("🔄 Processing your request... Please wait.")
            
            # Make API request
            api_success, result_data = await self.make_safe_api_call(aadhar)
            
            if not api_success:
                await processing_msg.edit_text("❌ API service is currently unavailable. Please try again later.")
                return
            
            # Format and send results
            await self.send_formatted_results(update, processing_msg, aadhar, result_data)
            
        except Exception as e:
            logger.error(f"Process error: {e}")
            await update.message.reply_text("❌ System error. Please try again.")

    async def make_safe_api_call(self, aadhar: str):
        """Make API call with comprehensive error handling"""
        try:
            # Prepare request data
            request_data = {"aadhaar": aadhar}
            
            # Make POST request with timeout
            response = requests.post(
                API_URL, 
                data=request_data,
                timeout=15,
                headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                logger.error(f"API returned status: {response.status_code}")
                return False, None
                
        except requests.exceptions.Timeout:
            logger.error("API request timeout")
            return False, None
        except requests.exceptions.ConnectionError:
            logger.error("API connection error")
            return False, None
        except requests.exceptions.RequestException as e:
            logger.error(f"API request exception: {e}")
            return False, None
        except json.JSONDecodeError:
            logger.error("API returned invalid JSON")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected API error: {e}")
            return False, None

    async def send_formatted_results(self, update: Update, processing_msg, aadhar: str, data: dict):
        """Send formatted results to user"""
        try:
            if not data:
                await processing_msg.edit_text("❌ No data received from API")
                return
            
            # Build result message
            result_text = f"🔍 Aadhar: {aadhar}\n\n"
            
            # Common fields to check
            fields_to_check = [
                ('name', '👤 Name'),
                ('full_name', '👤 Full Name'),
                ('father', '👨 Father'),
                ('father_name', '👨 Father Name'),
                ('mother', '👩 Mother'),
                ('mother_name', '👩 Mother Name'),
                ('dob', '🎂 Date of Birth'),
                ('address', '🏠 Address'),
                ('mobile', '📱 Mobile'),
                ('email', '📧 Email')
            ]
            
            found_data = False
            for field_key, field_display in fields_to_check:
                if field_key in data and data[field_key]:
                    result_text += f"{field_display}: {data[field_key]}\n"
                    found_data = True
            
            if not found_data:
                result_text += "❌ No information found for this Aadhar number.\n"
                result_text += "This Aadhar might not exist in the database."
            else:
                result_text += "\n✅ Information retrieved successfully."
            
            # Send results
            await processing_msg.edit_text(result_text)
            
        except Exception as e:
            logger.error(f"Send results error: {e}")
            await processing_msg.edit_text("✅ Request processed successfully.")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors gracefully"""
        try:
            logger.error(f"Bot error: {context.error}")
        except:
            pass

    def run(self):
        """Run the bot"""
        try:
            # Create application
            application = Application.builder().token(BOT_TOKEN).build()
            
            # Add handlers
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("help", self.help_command))
            application.add_handler(CommandHandler("status", self.status_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_aadhar))
            
            # Add error handler
            application.add_error_handler(self.error_handler)
            
            # Start bot
            print("🤖 Bot is starting...")
            print("✅ All systems ready!")
            
            application.run_polling(
                poll_interval=2.0,
                timeout=30,
                drop_pending_updates=True
            )
            
        except Exception as e:
            logger.critical(f"Bot crashed: {e}")
            print(f"🔴 Bot crashed: {e}")
            print("🔄 Restarting in 10 seconds...")
            time.sleep(10)
            self.run()

if __name__ == "__main__":
    bot = SimpleAadharBot()
    bot.run()