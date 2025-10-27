import requests
import logging
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("🤖 Aadhar Bot Starting...")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration
BOT_TOKEN = "8292852232:AAGk47XqZKocBTT3je-gco0NOPUr1I3TrC0"
API_URL = "https://happy-ration-info.vercel.app/fetch"

class AadharBot:
    def __init__(self):
        self.start_time = time.time()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        welcome_text = f"""
👋 Hello {user.first_name}!

🔍 Aadhar Information Bot

Send me a 12-digit Aadhar number to get information.

Example: 380468450193

Commands:
/start - Start bot
/help - Help guide
/status - Check status
        """
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
Help Guide:

1. Send 12-digit Aadhar number
2. Wait for processing
3. Get results

Example: 123456789012

Commands:
/start - Start bot
/help - This message
/status - Check status
        """
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uptime = time.time() - self.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        status_text = f"""
Bot Status:
✅ Active
⏰ Uptime: {hours}h {minutes}m
🌐 API: Ready
        """
        await update.message.reply_text(status_text)
    
    async def handle_aadhar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        aadhar_number = update.message.text.strip()
        
        # Validation
        if not aadhar_number.isdigit() or len(aadhar_number) != 12:
            await update.message.reply_text("❌ Please send a valid 12-digit Aadhar number")
            return
        
        await self.process_aadhar(update, aadhar_number)
    
    async def process_aadhar(self, update: Update, aadhar: str):
        try:
            # Send processing message
            processing_msg = await update.message.reply_text("🔄 Processing your request...")
            
            # Make API request
            url = f"{API_URL}?key=paidchx&aadhaar={aadhar}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                await self.send_results(processing_msg, aadhar, data)
            else:
                await processing_msg.edit_text("❌ API error. Please try again later.")
                
        except Exception as e:
            await update.message.reply_text("❌ Error processing request. Please try again.")
    
    async def send_results(self, processing_msg, aadhar: str, data: dict):
        try:
            result_text = f"🔍 Aadhar: {aadhar}\n\n"
            
            # Check common fields
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
                result_text += "❌ No information found for this Aadhar number."
            else:
                result_text += "\n✅ Information retrieved successfully."
            
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
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_aadhar))
            
            # Start bot
            print("✅ Bot is running successfully!")
            application.run_polling()
            
        except Exception as e:
            print(f"❌ Bot error: {e}")
            print("🔄 Restarting in 10 seconds...")
            time.sleep(10)
            self.run()

if __name__ == "__main__":
    bot = AadharBot()
    bot.run()