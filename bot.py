import os, random, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from database import get_questions

TOKEN = os.getenv("BOT_TOKEN")
TIME = 30

sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🎓 بدء اختبار جامعي", callback_data="start")]]
    await update.message.reply_text("مرحبًا بك في نظام الاختبارات الجامعي 📚", reply_markup=InlineKeyboardMarkup(kb))

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user.id
    
    questions = get_questions(10)
    sessions[user] = {"i":0,"score":0,"correct":0,"questions":questions}
    await send_q(update, context)

async def send_q(update, context):
    q = update.callback_query
    user = q.from_user.id
    s = sessions[user]
    
    if s["i"] >= len(s["questions"]):
        await result(update, context)
        return
    
    que = s["questions"][s["i"]]
    header = f"📘 السؤال {s['i']+1}/{len(s['questions'])}\n\n"
    
    if que["type"] == "true_false":
        kb = [[InlineKeyboardButton("✅ صح", callback_data="a_true"),
               InlineKeyboardButton("❌ خطأ", callback_data="a_false")]]
        text = header + que["question"]
        
    elif que["type"] == "multiple_choice":
        kb = []
        for i,opt in enumerate(que["options"]):
            kb.append([InlineKeyboardButton(opt, callback_data=f"a_{i}")])
        text = header + que["question"]
        
    else:
        context.user_data["fill"] = True
        await q.edit_message_text(header + f"✍️ أكمل:\n\n{que['question']}")
        return
        
    await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))
    context.application.create_task(timer(context, user))

async def timer(context, user):
    await asyncio.sleep(TIME)
    if user in sessions:
        sessions[user]["i"] += 1

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user.id
    s = sessions[user]
    que = s["questions"][s["i"]]
    
    correct = False
    if que["type"] == "true_false":
        correct = (q.data=="a_true") == que["answer"]
    else:
        correct = int(q.data.split("_")[1]) == que["answer"]
        
    await process(update, context, correct)

async def fill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("fill"): return
    user = update.effective_user.id
    s = sessions[user]
    que = s["questions"][s["i"]]
    
    correct = update.message.text.strip()==que["answer"]
    context.user_data["fill"] = False
    await process(update, context, correct)

async def process(update, context, correct):
    q = update.callback_query
    user = q.from_user.id
    s = sessions[user]
    
    if correct:
        s["score"]+=10
        s["correct"]+=1
        msg="✅ إجابة صحيحة"
    else:
        msg="❌ إجابة خاطئة"
        
    s["i"]+=1
    
    kb=[[InlineKeyboardButton("➡ التالي", callback_data="next")]]
    await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb))

async def next_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_q(update, context)

async def result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = q.from_user.id
    s = sessions[user]
    total=len(s["questions"])
    percent=(s["correct"]/total)*100
    
    text=f"""
🎓 النتائج الجامعية

📊 عدد الأسئلة: {total}
✅ الصحيحة: {s['correct']}
📈 النسبة: {percent:.1f}%
🏆 النقاط: {s['score']}
"""
    kb=[[InlineKeyboardButton("🔄 إعادة", callback_data="start")]]
    await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))
    del sessions[user]

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(start_quiz, pattern="^start$"))
    app.add_handler(CallbackQueryHandler(answer, pattern="^a_"))
    app.add_handler(CallbackQueryHandler(next_q, pattern="^next$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fill))
    app.run_polling()

if __name__ == "__main__":
    main()