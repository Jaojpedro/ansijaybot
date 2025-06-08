from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from datetime import datetime
import json
import os
import nest_asyncio
import asyncio

# Token do Telegram via variável de ambiente
TOKEN = os.getenv("BOT_TOKEN")

# Emoções e palavras-chave
emotion_keywords = {
    "ansiedade": ["ansioso", "desespero", "coração acelerado", "medo", "sufocando", "pânico"],
    "tristeza": ["triste", "sofrendo", "chorar", "chateado", "desanimado", "abatido"],
    "raiva": ["raiva", "irritado", "ódio", "explodir", "estressado"],
    "calma": ["calmo", "tranquilo", "em paz", "aliviado", "leve"],
    "alegria": ["feliz", "contente", "animado", "empolgado", "grato"],
}

# Respostas empáticas por emoção
adaptive_responses = {
    "ansiedade": "Sinto muito que esteja se sentindo assim. Vamos tentar juntos um exercício de respiração? Inspire por 4s, segure por 4s, expire por 6s. Estou com você.",
    "tristeza": "Lamento que esteja passando por isso. Quer conversar sobre o que está te deixando assim? Estou aqui para te ouvir.",
    "raiva": "A raiva é válida. Respire fundo, e se quiser, podemos encontrar uma forma de canalizar isso de forma saudável.",
    "calma": "Que bom que está se sentindo calmo. Aproveite esse momento. Se quiser conversar, estou aqui.",
    "alegria": "Fico muito feliz por você! Que essa alegria continue com você hoje. Quer compartilhar o que te deixou assim?",
    "neutro": "Entendi. Quer me contar mais? Estou aqui para conversar com você."
}

# Detecta emoção
def detect_emotion(message):
    message_lower = message.lower()
    for emotion, keywords in emotion_keywords.items():
        if any(word in message_lower for word in keywords):
            return emotion
    return "neutro"

# Responde mensagem
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    emotion = detect_emotion(user_message)
    response = adaptive_responses[emotion]

    log = {
        "timestamp": datetime.now().isoformat(),
        "user": update.effective_user.username,
        "message": user_message,
        "emotion": emotion,
        "response": response
    }

    with open("historico_respostas.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")

    await update.message.reply_text(response)

# Inicializa o app
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Loop compatível com Render / Jupyter
async def main():
    print("🤖 Bot Ansijay está online!")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(main())
    else:
        nest_asyncio.apply()
        asyncio.ensure_future(main())

