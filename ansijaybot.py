import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import openai
import nest_asyncio
import asyncio

# === CONFIGURAÇÕES MANUAIS ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = "https://ansijaybot.onrender.com/"  # 👈 fixado aqui!

# === INICIALIZAÇÕES ===
openai.api_key = OPENAI_API_KEY
nest_asyncio.apply()
app = FastAPI()
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# === GERADOR DE RESPOSTAS GPT ===
async def gerar_resposta_com_gpt(mensagem_usuario):
    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é Ansijay, um assistente emocional empático e acolhedor. "
                    "Ajude pessoas com ansiedade, estresse ou tristeza, com escuta ativa, técnicas de respiração e palavras de apoio. "
                    "Não use frases genéricas. Fale como um amigo próximo, com empatia real."
                )
            },
            {"role": "user", "content": mensagem_usuario}
        ],
        temperature=0.7,
        max_tokens=300
    )
    return resposta.choices[0].message["content"]

# === HANDLER DE MENSAGENS ===
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    resposta = await gerar_resposta_com_gpt(texto)
    await update.message.reply_text(resposta)

telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

# === ENDPOINT DO TELEGRAM ===
@app.post("/")
async def webhook(request: Request):
    update_dict = await request.json()
    update = Update.de_json(update_dict, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

# === STARTUP: REGISTRA O WEBHOOK NO TELEGRAM ===
@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)
    await telegram_app.start()
    print(f"🔔 Webhook configurado com sucesso: {WEBHOOK_URL}")
    print("feito")

