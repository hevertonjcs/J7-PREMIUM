from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import json

# TOKEN fixo embutido diretamente
TOKEN = "8493792708:AAGwFXi6QZPnvnZ_fhXI74h_uWZFxogBhew"

# Carregando os produtos com margem do JSON
with open("produtos.json", "r") as f:
    produtos = json.load(f)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚠️ Sem estorno\n"
        "⚠️ Não garantimos vínculo, saldo ou aprovação\n"
        "✅ Garantia só de LIVE no teste\n"
        "🕐 Troca só pelo bot, até 10min depois da compra\n"
        "⚠️ Compre se estiver de acordo com as regras!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 LOJA | COMPRAR", callback_data="loja")],
            [InlineKeyboardButton("💎 MEU PERFIL", callback_data="perfil")]
        ])
    )

# Resposta a cliques nos botões
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "loja":
        keyboard = []
        for p in produtos:
            keyboard.append([
                InlineKeyboardButton(f"{p['nome']} - R$ {p['revenda_valor']}", callback_data=f"produto_{p['nome']}")
            ])
        await query.edit_message_text("🛍️ Escolha um produto:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("produto_"):
        nome = query.data.replace("produto_", "")
        produto = next((x for x in produtos if x["nome"] == nome), None)
        if produto:
            context.user_data["produto"] = produto["nome"]
            await query.edit_message_text(
                f"💳 Produto: {produto['nome']}\n"
                f"💰 Valor: R$ {produto['revenda_valor']}\n\n"
                f"🔑 Chave Pix: tesouraria@multinegociacoes.com\n\n"
                f"Após pagar, clique no botão abaixo para confirmar.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Já paguei", callback_data="confirmar_pagamento")]
                ])
            )

    elif query.data == "confirmar_pagamento":
        produto = context.user_data.get("produto")
        await query.edit_message_text(
            "⏳ Verificando pagamento...\n🔁 Realizando a compra no fornecedor..."
        )

        from telethon_bot import comprar_no_fornecedor
        resultado = await comprar_no_fornecedor(produto)

        await query.message.reply_text(
            f"✅ Compra concluída!\n🧾 Conteúdo: \n\n{resultado}"
        )

# Inicialização do bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))
app.run_polling(drop_pending_updates=True)
