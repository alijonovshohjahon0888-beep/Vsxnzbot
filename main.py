import asyncio
import os
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ================== SOZLAMALAR ==================
YOUR_USERNAME = "vsxnz"

SOCIAL_MEDIA = {
    "📸 Instagram": "https://instagram.com/shakhvsn",
    "🎵 TikTok": "https://www.tiktok.com/@vsxnzz",
    "💬 Telegram": "https://t.me/vsxnz",
}

CHANNEL_ID = "@eslatmacontact"

# Bot tokenini environment variable dan olish (bothosting.space uchun)
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN topilmadi! bothosting.space Environment Variables bo'limiga BOT_TOKEN ni qo'shing.")

user_questions = {}
# ================================================

async def send_to_channel(context, text):
    """Kanalga xabar yuborish"""
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="HTML")
    except Exception as e:
        print(f"Kanalga yuborishda xatolik: {e}")

async def log_user_action(context, user, action, details=""):
    """Foydalanuvchi amalini kanalga yozish"""
    text = f"""📝 <b>Foydalanuvchi amali</b>

👤 <b>Foydalanuvchi:</b> {user.full_name}
🆔 <b>ID:</b> <code>{user.id}</code>
📛 <b>Username:</b> @{user.username if user.username else 'Yoq'}
⚡ <b>Amal:</b> {action}
📄 <b>Ma'lumot:</b> {details}
⏰ <b>Vaqt:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    await send_to_channel(context, text)

async def send_user_info_to_channel(context, user):
    text = f"""🆕 <b>Yangi foydalanuvchi /start bosdi!</b>

👤 <b>Ism:</b> {user.full_name}
🆔 <b>User ID:</b> <code>{user.id}</code>
📛 <b>Username:</b> @{user.username if user.username else 'Yoq'}
🌐 <b>Til:</b> {user.language_code or 'Noma\'lum'}

⏰ Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    await send_to_channel(context, text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await send_user_info_to_channel(context, user)
    await log_user_action(context, user, "/start bosdi", "Botni ishga tushirdi")
    
    keyboard = [
        [InlineKeyboardButton("💬 Vsxnz bilan tog'ridan-tog'ri bog'lanish", 
                              url=f"https://t.me/{YOUR_USERNAME}")],
        [InlineKeyboardButton("🌐 Ijtimoiy tarmoqlarni korish", 
                              callback_data="showsocial")],
        [InlineKeyboardButton("❓ Maxsus savol va malumotlar", 
                              callback_data="special_questions")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Salom, {user.first_name}!\nNima yordam bera olaman?",
        reply_markup=reply_markup
    )

async def special_questions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    
    await log_user_action(context, user, "Maxsus savollar menyusini ochdi", "3 ta savol ko'rsatildi")
    
    keyboard = [
        [InlineKeyboardButton("💕 @vsxnz sevgan qizi", callback_data="q_girl")],
        [InlineKeyboardButton("🔐 Instagram paroli", callback_data="q_instagram")],
        [InlineKeyboardButton("👥 Eng yaqin dost'i", callback_data="q_friend")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="backto_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="❓ Maxsus savol va malumotlar\n\nSavollardan birini tanlang:",
        reply_markup=reply_markup
    )

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    user_id = user.id
    
    await query.answer()
    
    if query.data == "q_girl":
        user_questions[user_id] = {"type": "food", "attempts": 0}
        msg = await query.edit_message_text(
            "🍽️ Savol: Uning eng yaxshi kor'gan taomi?\n\nJavob imloviy xatosiz bolsin!"
        )
        user_questions[user_id]["message_id"] = msg.message_id
        await log_user_action(context, user, "1-savol tanlandi", "Sevgan qizi - taom savoli")
        
    elif query.data == "q_instagram":
        user_questions[user_id] = {"type": "birthdate", "attempts": 0}
        msg = await query.edit_message_text(
            "📅 Savol: @vsxnz tug'ilgan vaqtini toliq ayting\n\nFormat: DD.MM.YYYY\n\nMasalan: 22.02.2022"
        )
        user_questions[user_id]["message_id"] = msg.message_id
        await log_user_action(context, user, "2-savol tanlandi", "Instagram paroli - tug'ilgan vaqt savoli")
        
    elif query.data == "q_friend":
        await query.edit_message_text(
            "👥 Eng yaqin dost'i:\n\nBu savolga javob faqat @vsxnz ning oʻzi biladi!\nUni Telegramda soʻrang: @vsxnz",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Orqaga", callback_data="special_questions")
            ]])
        )
        await log_user_action(context, user, "3-savol tanlandi", "Eng yaqin do'sti - @vsxnz ga murojaat")

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    answer = update.message.text.strip().lower()
    
    if user_id not in user_questions:
        return
    
    question_data = user_questions[user_id]
    question_type = question_data["type"]
    
    await log_user_action(context, user, f"Javob berdi: {answer}", f"Savol turi: {question_type}")
    
    try:
        await context.bot.delete_message(chat_id=user_id, message_id=question_data["message_id"])
    except:
        pass
    
    if question_type == "food":
        if answer in ["manti", "monti"]:
            msg = await update.message.reply_text("💖 Mohina 💖")
            await log_user_action(context, user, "✅ To'g'ri javob", "Taom savoli: monti/manti/Manti/Monti")
            await asyncio.sleep(5)
            await msg.delete()
            await update.message.delete()
            del user_questions[user_id]
        else:
            question_data["attempts"] += 1
            if question_data["attempts"] >= 2:
                msg = await update.message.reply_text("❌ Javob notog'ri! Boshqa savol tanlang.")
                await log_user_action(context, user, "❌ Noto'g'ri javob (2 marta)", f"Javob: {answer}")
                await asyncio.sleep(3)
                await msg.delete()
                await update.message.delete()
                del user_questions[user_id]
            else:
                msg = await update.message.reply_text("❌ Notog'ri! Yana urinib kor'ing:")
                await log_user_action(context, user, "❌ Noto'g'ri javob (1-marta)", f"Javob: {answer}")
                await asyncio.sleep(2)
                await msg.delete()
                await update.message.delete()
                new_msg = await context.bot.send_message(
                    chat_id=user_id,
                    text="🍽️ Savol: Uning eng yaxshi kor'gan taomi?\n\nJavob imloviy xatosiz bolsin!"
                )
                question_data["message_id"] = new_msg.message_id
                
    elif question_type == "birthdate":
        if answer == "13.02.2010":
            msg = await update.message.reply_text("🖕🏻")
            await log_user_action(context, user, "✅ To'g'ri javob", "Tug'ilgan vaqt: 13.02.2010")
            await asyncio.sleep(5)
            await msg.delete()
            await update.message.delete()
            del user_questions[user_id]
        else:
            question_data["attempts"] += 1
            if question_data["attempts"] >= 2:
                msg = await update.message.reply_text("❌ Javob notog'ri! Boshqa savol tanlang.")
                await log_user_action(context, user, "❌ Noto'g'ri javob (2 marta)", f"Javob: {answer}")
                await asyncio.sleep(3)
                await msg.delete()
                await update.message.delete()
                del user_questions[user_id]
            else:
                msg = await update.message.reply_text("❌ Notog'ri! Yana urinib kor'ing (DD.MM.YYYY):")
                await log_user_action(context, user, "❌ Noto'g'ri javob (1-marta)", f"Javob: {answer}")
                await asyncio.sleep(2)
                await msg.delete()
                await update.message.delete()
                new_msg = await context.bot.send_message(
                    chat_id=user_id,
                    text="📅 Savol: @vsxnz tug'ilgan vaqtini toʻliq ayting\n\nFormat: DD.MM.YYYY"
                )
                question_data["message_id"] = new_msg.message_id

async def show_social(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    
    await log_user_action(context, user, "Ijtimoiy tarmoqlarni ko'rish", "Instagram, TikTok, Telegram")
    
    keyboard = [[InlineKeyboardButton(name, url=url)] for name, url in SOCIAL_MEDIA.items()]
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="backto_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="🌐 Mening ijtimoiy tarmoqlarim:",
        reply_markup=reply_markup
    )

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    
    await log_user_action(context, user, "Asosiy menyuga qaytish", "Orqaga tugmasi")
    
    keyboard = [
        [InlineKeyboardButton("💬 Vsxnz bilan tog'ridan-tog'ri bog'lanish", 
                              url=f"https://t.me/{YOUR_USERNAME}")],
        [InlineKeyboardButton("🌐 Ijtimoiy tarmoqlarni korish", 
                              callback_data="showsocial")],
        [InlineKeyboardButton("❓ Maxsus savol va malumotlar", 
                              callback_data="special_questions")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="👋 Asosiy menyu\nNima yordam bera olaman?",
        reply_markup=reply_markup
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_social, pattern="^showsocial$"))
    app.add_handler(CallbackQueryHandler(back_to_main, pattern="^backto_main$"))
    app.add_handler(CallbackQueryHandler(special_questions_menu, pattern="^special_questions$"))
    app.add_handler(CallbackQueryHandler(handle_question, pattern="^q_"))
    app.add_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, check_answer))

    print("🤖 Bot ishga tushdi!")
    print("✅ Har bir foydalanuvchi amali kanalga yuboriladi!")
    print(f"📢 Kanal: {CHANNEL_ID}")

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
