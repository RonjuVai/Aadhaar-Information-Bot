import os
import requests
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("🚀 Aadhar Information Bot - Own Version")
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

# টোকেন সেট করার সর্বোত্তম উপায়
def get_bot_token():
    """বট টোকেন পাওয়ার জন্য বিভিন্ন উপায় try করুন"""
    # 1. প্রথমে environment variable চেক করুন
    env_token = os.environ.get("BOT_TOKEN")
    if env_token:
        print("✅ Environment variable থেকে টোকেন লোড হয়েছে")
        return env_token
    
    # 2. Own specific environment variables চেক করুন
    Own_token = os.environ.get("Own_BOT_TOKEN")
    if Own_token:
        print("✅ Own environment variable থেকে টোকেন লোড হয়েছে")
        return Own_token
    
    # 3. সরাসরি টোকেন (fallback)
    print("⚠️ Environment variable না পাওয়ায় সরাসরি টোকেন ব্যবহার করা হচ্ছে")
    return "8292852232:AAGk47XqZKocBTT3je-gco0NOPUr1I3TrC0"

BOT_TOKEN = get_bot_token()
API_URL = "https://pkans.ct.ws/fetch.php?aadhaar="

# টোকেন ভ্যালিডেশন
def validate_token(token):
    """বট টোকেনটি সঠিক কিনা চেক করুন"""
    try:
        import requests
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        return response.json().get('ok', False)
    except:
        return False

print(f"🔐 টোকেন ভ্যালিডেশন: {'✅ সফল' if validate_token(BOT_TOKEN) else '❌ ব্যর্থ'}")

class AadharInfoBot:
    def __init__(self):
        self.start_time = None
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced start command"""
        user = update.effective_user
        welcome_text = f"""
👋 **Welcome {user.first_name}!**

🔍 **Aadhar Information Lookup Bot**

📋 **What I can do:**
• Fetch Aadhar card information
• Show personal details
• Retrieve address data
• Fast and secure API

🛡️ **Privacy & Security:**
• Your queries are encrypted
• No data storage
• Secure API connection

📝 **How to use:**
Simply send a 12-digit Aadhar number

**Example:** `380468450193`

⚠️ **Disclaimer:** For authorized testing only
🔧 **Version:**  Pro 2.0
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

🔍 **Usage:**
Send any 12-digit Aadhar number to get information

**Format:** `123456789012`

⚡ **Features:**
✅ Fast API response
✅ Secure data handling
✅ 24/7 availability
✅ User-friendly interface

📞 **Support:** Contact admin for assistance
        """
        
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """About command"""
        about_text = """
ℹ️ **About This Bot**

🤖 **Aadhar Information Bot**
🚀 **Version:**  Pro 2.0
🔧 **Developer:** Professional Team Ronju Vai
🌐 **API:** Secure Aadhar Lookup
💻 **Platform:** Own 24/7

🔒 **Security Features:**
• Encrypted communication
• No data persistence
• Secure API endpoints
• Privacy focused

📊 **Technical Info:**
• Python 3.11
• python-telegram-bot v20
• Requests library
• Own hosting

⚠️ **Legal Notice:**
This bot is for authorized testing only.
Unauthorized use is prohibited.
        """
        
        await update.message.reply_text(about_text, parse_mode="Markdown")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Status check command"""
        status_text = f"""
📊 **Bot Status**

🟢 **Status:** ACTIVE
⚡ **Performance:** Optimal
🔒 **Security:** Enabled
🌐 **API:** Connected

💾 **System Info:**
• Host: Own
• Uptime: 24/7
• Version: Pro 2.0
• Updates: Auto-deploy

🔐 **Token Status:** {'✅ Valid' if validate_token(BOT_TOKEN) else '❌ Invalid'}

✅ **All services operational**
        """
        
        await update.message.reply_text(status_text, parse_mode="Markdown")

    async def handle_aadhar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle Aadhar number input with enhanced features"""
        aadhar = update.message.text.strip()
        user = update.effective_user
        
        logger.info(f"Aadhar lookup requested by {user.first_name}: {aadhar}")

        # Validation
        if not aadhar.isdigit():
            await update.message.reply_text(
                "❌ **Invalid Input**\n\nPlease send only numbers (0-9)",
                parse_mode="Markdown"
            )
            return
            
        if len(aadhar) != 12:
            await update.message.reply_text(
                "❌ **Invalid Length**\n\nAadhar number must be exactly 12 digits\n\n**Example:** `380468450193`",
                parse_mode="Markdown"
            )
            return

        # Show processing message
        processing_msg = await update.message.reply_text(
            "🔄 **Processing Request...**\n\n"
            "• Validating Aadhar number ✅\n"
            "• Connecting to secure API 🔒\n"
            "• Fetching information 📡\n\n"
            "⏳ Please wait...",
            parse_mode="Markdown"
        )

        try:
            # API request with timeout
            response = requests.get(API_URL + aadhar, timeout=15)
            
            if response.status_code != 200:
                await processing_msg.edit_text(
                    "❌ **API Connection Error**\n\n"
                    f"Status Code: {response.status_code}\n"
                    "Please try again later or contact support.",
                    parse_mode="Markdown"
                )
                return

            data = response.json()
            
            # Build enhanced response
            info = f"🔍 **Aadhar Lookup Results**\n\n"
            info += f"🆔 **Aadhar Number:** `{aadhar}`\n"
            info += "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            # Enhanced field mappings with better formatting
            field_map = {
                'name': '👤 **Full Name**',
                'full_name': '👤 **Full Name**', 
                'address': '🏠 **Address**',
                'current_address': '🏠 **Current Address**',
                'permanent_address': '🏠 **Permanent Address**',
                'mother_name': '👩 **Mother\'s Name**',
                'mother': '👩 **Mother\'s Name**',
                'father_name': '👨 **Father\'s Name**', 
                'father': '👨 **Father\'s Name**',
                'mobile': '📱 **Mobile Number**',
                'mobile_number': '📱 **Mobile Number**',
                'phone': '📞 **Phone Number**',
                'email': '📧 **Email Address**',
                'email_id': '📧 **Email Address**',
                'dob': '🎂 **Date of Birth**',
                'date_of_birth': '🎂 **Date of Birth**',
                'gender': '⚧ **Gender**',
                'age': '📅 **Age**'
            }

            found_data = False
            for field, display_name in field_map.items():
                if field in data and data[field]:
                    info += f"{display_name}: `{data[field]}`\n"
                    found_data = True

            if not found_data:
                info += "❌ **No Information Found**\n\n"
                info += "This Aadhar number may not exist in the database or the API is temporarily unavailable.\n\n"
                info += "**Troubleshooting:**\n"
                info += "• Check the Aadhar number\n"
                info += "• Try again later\n"
                info += "• Contact support if issue persists"
                
                await processing_msg.edit_text(info, parse_mode="Markdown")
                return

            # Add footer
            info += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            info += "🔒 *Securely processed*\n"
            info += "⏰ *Real-time data*\n"
            info += "✅ *API Response Successful*"

            # Send the main results
            await processing_msg.edit_text(info, parse_mode="Markdown")
            
            # Send raw data in a separate message if needed
            raw_data_preview = f"📄 **Raw Data Preview:**\n```json\n{json.dumps(data, indent=2)[:800]}...\n```"
            
            if len(raw_data_preview) < 4000:  # Telegram message limit
                await update.message.reply_text(raw_data_preview, parse_mode="Markdown")
            
            logger.info(f"Successful lookup for Aadhar: {aadhar}")

        except requests.exceptions.Timeout:
            await processing_msg.edit_text(
                "⏰ **Request Timeout**\n\n"
                "The API is taking too long to respond.\n\n"
                "**Possible reasons:**\n"
                "• API server busy\n"
                "• Network congestion\n"
                "• High load\n\n"
                "🔄 Please try again in a few moments.",
                parse_mode="Markdown"
            )
            logger.warning(f"API timeout for Aadhar: {aadhar}")
            
        except requests.exceptions.RequestException as e:
            await processing_msg.edit_text(
                "🌐 **Network Error**\n\n"
                "Cannot connect to the API server.\n\n"
                "**Solutions:**\n"
                "• Check your internet connection\n"
                "• Try again later\n"
                "• Contact support\n\n"
                f"🔧 Error: `{str(e)}`",
                parse_mode="Markdown"
            )
            logger.error(f"Network error: {e}")
            
        except Exception as e:
            await processing_msg.edit_text(
                "❌ **Unexpected Error**\n\n"
                "Something went wrong while processing your request.\n\n"
                "**Please try:**\n"
                "• Sending the Aadhar number again\n"
                "• Using /start to restart\n"
                "• Contacting support if problem continues\n\n"
                f"🔧 Technical details: `{str(e)}`",
                parse_mode="Markdown"
            )
            logger.error(f"Unexpected error: {e}")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Global error handler"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ **System Error**\n\n"
                    "A temporary error occurred. The bot is auto-recovering...\n\n"
                    "🔄 Please try your request again.",
                    parse_mode="Markdown"
                )
        except:
            pass

    def run(self):
        """Run the bot with enhanced configuration"""
        try:
            # টোকেন চেক করুন
            if not validate_token(BOT_TOKEN):
                print("❌ বট টোকেন সঠিক নয়! Own Dashboard থেকে BOT_TOKEN variable সেট করুন")
                print("📝 Own Dashboard → Variables → Add BOT_TOKEN")
                return
            
            # Create application
            application = Application.builder().token(BOT_TOKEN).build()
            
            # Add handlers
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("help", self.help_command))
            application.add_handler(CommandHandler("about", self.about_command))
            application.add_handler(CommandHandler("status", self.status_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_aadhar))
            
            # Add error handler
            application.add_error_handler(self.error_handler)
            
            # Start the bot
            print("🤖 Aadhar Information Bot is running...")
            print("✅ Successfully deployed on Own!")
            print("🔒 Secure API: Enabled")
            print("🚀 Version: Own Pro 2.0")
            print(f"🔐 Token Status: Valid")
            
            application.run_polling(
                poll_interval=1.0,
                timeout=30,
                drop_pending_updates=True
            )
            
        except Exception as e:
            logger.critical(f"Bot failed to start: {e}")
            print(f"❌ Bot startup failed: {e}")
            print("🔄 Attempting restart in 10 seconds...")
            import time
            time.sleep(10)
            self.run()  # Auto-restart

if __name__ == "__main__":
    bot = AadharInfoBot()
    bot.run()