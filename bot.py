import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
Ты — персональный ассистент по здоровью, дисциплине и рельефу тела.

РОЛЬ:
Жёсткий, требовательный цифровой тренер.
Никакой воды, никакой жалости.

ПОЛЬЗОВАТЕЛЬ:
Мужчина, 30 лет, 172 см, 61 кг.
Тренируется дома, без оборудования.
Цель — сухое, рельефное тело.
Аллергии: берёза, яблоки, груша, киви, бобовые, рис, любые каши.

ПРАВИЛА:
- Коротко и по делу
- Давление и контроль допустимы
- Хвалишь только за факты
- Отчитываешь за пропуски
- Не ставишь диагнозы
- Не рекомендуешь медикаменты
- Не составляешь меню
- Анализируешь только реальное питание

ЕСЛИ ПИШУТ ОБЩЕЕ («привет», «норм», «как дела»):
— ты сам инициируешь контроль: тренировка, питание, самочувствие.
"""

def ask_gpt(user_text: str) -> str:
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4.1-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text},
                ],
                "temperature": 0.4,
            },
            timeout=30,
        )

        data = response.json()

        if "choices" not in data:
            return "Связь с мозгами дала сбой. Напиши ещё раз."

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("OPENAI ERROR:", e)
        return "Ошибка связи. Не отмазывайся. Повтори сообщение."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Я здесь. Без воды.\n\n"
        "Отчитывайся:\n"
        "1) Была ли сегодня тренировка\n"
        "2) Что ел\n"
        "3) Самочувствие"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip().lower()

    if user_text in ["привет", "hi", "hello", "здарова", "ку"]:
        user_text = (
            "Пользователь написал общее приветствие. "
            "Инициируй жёсткий контроль: тренировка, питание, самочувствие."
        )

    answer = ask_gpt(user_text)
    await update.message.reply_text(answer)


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("BOT STARTED")
    app.run_polling()


if __name__ == "__main__":
    main()
