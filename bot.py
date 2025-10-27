import os
import requests
import json
import logging
import time
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, NetworkError

print("🚀 Aadhar Information Bot - Ultra Stable Version")
print("🔧 Starting with crash protection...")

# Enhanced logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "8292852232:AAGk47XqZKocBTT3je-gco0NOPUr1I3TrC0"
API_URL = "https://pkans.ct.ws/fetch.php?aadhaar="

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

class StableAadharBot:
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.restart_count = 0
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Simple start command"""
        try:
            user = update.effective_user
            welcome_text = f"""
👋 Hello {user.first_name}!

🔍 Aadhar Information Bot

Send me a 12-digit Aadhar number to get information.

Example: 380468450193

Commands:
/start - Start bot
/help - Help
/status - Bot status
            """
            await update.message.reply_text(welcome_text)
            logger.info(f"Start by {user.first_name}")
        except Exception as e:
            logger.error(f"Start error: {e}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        try:
            help_text = """
Help Guide:

1. Send 12-digit Aadhar number
2. Wait for processing
3. Get results

Example: 123456789012

Commands:
/start - Start
/help - This message  
/status - Check status
            """
            await update.message.reply_text(help_text)
        except Exception as e:
            logger.error(f"Help error: {e}")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Status command"""
        try:
            uptime = time.time() - self.start_time
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            
            status_text = f"""
Bot Status:
✅ Active
⏰ Uptime: {hours}h {minutes}m
📊 Requests: {self.request_count}
🔄 Restarts: {self.restart_count}
🌐 API: Working
            """
            await update.message.reply_text(status_text)
        except Exception as e:
            logger.error(f"Status error: {e}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all messages"""
        try:
            text = update.message.text.strip()
            
            # Ignore commands
            if text.startswith('/'):
                return
                
            # Validate Aadhar number
            if not text.isdigit() or len(text) != 12:
                await update.message.reply_text("❌ Please send a valid 12-digit Aadhar number")
                return
            
            await self.process_aadhar(update, text)
            
        except Exception as e:
            logger.error(f"Message handler error: {e}")
            await update.message.reply_text("❌ System error. Please try again.")

    async def process_aadhar(self, update: Update, aadhar: str):
        """Process Aadhar lookup"""
        self.request_count += 1
        
        # Send processing message
        try:
            processing_msg = await update.message.reply_text("🔄 Processing your request...")
        except:
            processing_msg = None

        try:
            # API request with retry
            response = await self.make_api_request(aadhar)
            
            if not response:
                await self.send_error(update, processing_msg, "API connection failed. Please try again.")
                return

            if response.status_code != 200:
                await self.send_error(update, processing_msg, f"API error: {response.status_code}")
                return

            data = response.json()
            
            # Format and send results
            await self.send_results(update, processing_msg, aadhar, data)
            
        except Exception as e:
            logger.error(f"Process Aadhar error: {e}")
            await self.send_error(update, processing_msg, "Processing error. Please try again.")

    async def make_api_request(self, aadhar: str, retries: int = 3):
        """Make API request with retry logic"""
        for attempt in range(retries):
            try:
                response = requests.get(
                    API_URL + aadhar, 
                    headers=HEADERS, 
                    timeout=10,
                    verify=False  # Skip SSL verification for stability
                )
                return response
            except requests.exceptions.Timeout:
                logger.warning(f"API timeout attempt {attempt + 1}")
                if attempt < retries - 1:
                    await asyncio.sleep(2)
            except Exception as e:
                logger.warning(f"API error attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2)
        
        return None

    async def send_results(self, update: Update, processing_msg, aadhar: str, data: dict):
        """Send formatted results"""
        try:
            # Build result message
            result_text = f"🔍 Aadhar: {aadhar}\n\n"
            
            # Add available fields
            fields_added = False
            for field in ['name', 'full_name', 'father', 'father_name', 'mother', 'mother_name', 'dob', 'address']:
                if field in data and data[field]:
                    field_name = field.replace('_', ' ').title()
                    result_text += f"• {field_name}: {data[field]}\n"
                    fields_added = True
            
            if not fields_added:
                result_text += "❌ No information found for this Aadhar number."
            else:
                result_text += "\n✅ Information retrieved successfully."
            
            # Update or send message
            if processing_msg:
                try:
                    await processing_msg.edit_text(result_text)
                except:
                    await update.message.reply_text(result_text)
            else:
                await update.message.reply_text(result_text)
                
        except Exception as e:
            logger.error(f"Send results error: {e}")
            await update.message.reply_text("✅ Request completed.")

    async def send_error(self, update: Update, processing_msg, error_text: str):
        """Send error message"""
        try:
            if processing_msg:
                await processing_msg.edit_text(f"❌ {error_text}")
            else:
                await update.message.reply_text(f"❌ {error_text}")
        except:
            await update.message.reply_text(f"❌ {error_text}")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Global error handler"""
        try:
            logger.error(f"Update error: {context.error}")
        except:
            pass

    def run_bot(self):
        """Run the bot with crash protection"""
        max_restarts = 5
        restart_delay = 30
        
        while self.restart_count < max_restarts:
            try:
                print(f"🔄 Starting bot (Attempt {self.restart_count + 1}/{max_restarts})...")
                
                # Create application
                application = Application.builder().token(BOT_TOKEN).build()
                
                # Add handlers
                application.add_handler(CommandHandler("start", self.start))
                application.add_handler(CommandHandler("help", self.help_command))
                application.add_handler(CommandHandler("status", self.status_command))
                application.add_handler(MessageHandler(filters.TEXT, self.handle_message))
                
                # Add error handler
                application.add_error_handler(self.error_handler)
                
                # Start bot
                print("🤖 Bot is running...")
                application.run_polling(
                    poll_interval=3.0,  # Increased interval
                    timeout=60,
                    drop_pending_updates=True
                )
                
            except TelegramError as e:
                logger.error(f"Telegram error: {e}")
                self.restart_count += 1
                print(f"🔴 Telegram error. Restarting in {restart_delay} seconds...")
                time.sleep(restart_delay)
                
            except Exception as e:
                logger.critical(f"Critical error: {e}")
                self.restart_count += 1
                print(f"🔴 Critical error. Restarting in {restart_delay} seconds...")
                time.sleep(restart_delay)
        
        print("💥 Max restarts reached. Bot stopped.")

if __name__ == "__main__":
    bot = StableAadharBot()
    bot.run_bot()