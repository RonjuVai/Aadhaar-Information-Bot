    await testing_msg.edit_text(result_text, parse_mode="Markdown")

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
        "⏳ Please wait 5-10 seconds...",
        parse_mode="Markdown"
    )

    try:
        # API request with timeout and headers
        response = requests.get(API_URL + aadhar, headers=HEADERS, timeout=15)
        
        if response.status_code != 200:
            await processing_msg.edit_text(
                f"❌ **API Error**\n\n"
                f"Status Code: {response.status_code}\n"
                f"Response: {response.text[:200]}\n\n"
                "Please try again later.",
                parse_mode="Markdown"
            )
            return

        data = response.json()
        
        # Check if data is valid
        if not data or (isinstance(data, dict) and not any(data.values())):
            await processing_msg.edit_text(
                f"❌ **No Data Found**\n\n"
                f"Aadhar `{aadhar}` - এর জন্য কোনো তথ্য পাওয়া যায়নি।\n\n"
                "**সম্ভাব্য কারণ:**\n"
                "• Aadhar number টি সঠিক নয়\n"
                "• Database এ তথ্য নেই\n"
                "• Temporary API issue\n\n"
                "🔧 **Solution:** ভিন্ন Aadhar number দিয়ে চেষ্টা করুন",
                parse_mode="Markdown"
            )
            return
        
        # Build enhanced response
        info = f"🔍 **Aadhar Lookup Results**\n\n"
        info += f"🆔 **Aadhar Number:** `{aadhar}`\n"
        info += "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        # Enhanced field mappings based on API response
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
            'age': '📅 **Age**',
            'district': '🏙️ **District**',
            'state': '🗺️ **State**',
            'pincode': '📮 **Pincode**'
        }

        found_data = False
        for field, display_name in field_map.items():
            if field in data and data[field]:
                info += f"{display_name}: `{data[field]}`\n"
                found_data = True

        if not found_data:
            # If no mapped fields found, show all available data
            info += "📄 **Available Information:**\n\n"
            for key, value in data.items():
                if value and str(value).strip():
                    formatted_key = ' '.join(word.capitalize() for word in key.split('_'))
                    info += f"**{formatted_key}:** `{value}`\n"
                    found_data = True

        if not found_data:
            await processing_msg.edit_text(
                f"❌ **No Information Found**\n\n"
                f"Aadhar `{aadhar}` - এর জন্য কোনো তথ্য পাওয়া যায়নি।\n\n"
                "**Raw API Response:**\n"
                f"```json\n{json.dumps(data, indent=2)[:500]}\n```",
                parse_mode="Markdown"
            )
            return

        # Add footer
        info += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
        info += "🔒 *Securely processed*\n"
        info += "⏰ *Real-time data*\n"
        info += "✅ *API Response Successful*"

        # Send the main results
        await processing_msg.edit_text(info, parse_mode="Markdown")
        
        # Send raw data in a separate message for debugging
        raw_data_preview = f"📄 **Raw Data Preview:**\n```json\n{json.dumps(data, indent=2)[:1500]}\n```"
        
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
            "• The API might be temporarily down\n"
            "• Try again in 5 minutes\n"
            "• Use /test to check API status\n\n"
            f"🔧 Technical Error: `{str(e)}`",
            parse_mode="Markdown"
        )
        logger.error(f"Network error: {e}")
        
    except Exception as e:
        await processing_msg.edit_text(
            "❌ **Unexpected Error**\n\n"
            "Something went wrong while processing your request.\n\n"
            "**Please try:**\n"
            "• Sending the Aadhar number again\n"
            "• Using /test to check API status\n"
            "• Contacting support if problem continues\n\n"
            f"🔧 Error: `{str(e)}`",
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
                "🔄 Please try your request again in a moment.",
                parse_mode="Markdown"
            )
    except:
        pass

def run(self):
    """Run the bot with enhanced configuration"""
    try:
        # টোকেন চেক করুন
        if not validate_token(BOT_TOKEN):
            print("❌ বট টোকেন সঠিক নয়! টোকেন চেক করুন")
            return
        
        # API টেস্ট
        api_working, _ = test_api()
        if not api_working:
            print("⚠️ API কাজ করছে না, কিন্তু বট চালু হচ্ছে...")
        
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("about", self.about_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("test", self.test_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_aadhar))
        
        # Add error handler
        application.add_error_handler(self.error_handler)
        
        # Start the bot
        print("🤖 Aadhar Information Bot is running...")
        print("✅ Successfully deployed on Own!")
        print("🔒 Secure API: Enabled")
        print("🚀 Version: Own Pro 3.0")
        print(f"🌐 API Status: {'✅ Working' if api_working else '⚠️ Issues'}")
        
        application.run_polling(
            poll_interval=1.0,
            timeout=30,
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")
        print(f"❌ Bot startup failed: {e}")
        print("🔄 Attempting restart in 10 seconds...")
        time.sleep(10)
        self.run()  # Auto-restart