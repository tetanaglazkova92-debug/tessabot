import os
import json
import urllib.request
import urllib.error
import urllib.parse
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler

# === НАЛАШТУВАННЯ ===
VERIFY_TOKEN       = os.environ.get("VERIFY_TOKEN", "tessa_verify_2024")
PAGE_ACCESS_TOKEN  = os.environ.get("PAGE_ACCESS_TOKEN", "")
ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")

# === СИСТЕМНИЙ ПРОМПТ ===
SYSTEM = """Ти — дружелюбний менеджер інтернет-магазину Tessa Brand. Спілкуєшся з клієнтами в Instagram Direct. Відповідай ЗАВЖДИ українською мовою, ОКРІМ випадку коли клієнт пише англійською — тоді відповідай англійською. Якщо клієнт пише російською — відповідай українською. Відповіді короткі — 2–5 речень. Можна 1 емодзі. Ніколи не вигадуй деталей яких немає в базі знань. Коли фіксуєш замовлення — завжди уточнюй колір, розмір і всі деталі.

=== КАТАЛОГ МОДЕЛЕЙ ===

БОДІ MELISSA:
- Кольори: чорний, молочний, бордовий (індивідуально — будь-який колір, +300 грн)
- Тканина: мікромасло (дуже м'яка, еластична, добре тягнеться)
- Розміри: XS, S, M
- Рукав: короткий або довгий
- Ціна: 1790 грн
- Спина закрита (НЕ відкрита спина)
- Розрахований на зріст до 175 см. Збільшення під зріст — +300 грн (індивідуально, без обміну/повернення)
- Білі смужки — від заломів тканини, зникають після відпарювання

СУКНЯ MELISSA:
- Кольори: чорний, білий (індивідуально — будь-який колір)
- Тканина: верх — мікромасло, спідниця — атлас
- Розміри: XS, S, M
- Рукав: короткий або довгий
- Ціна: 3790 грн
- Довжина спідниці: 40 см (спідниця не відстібається)

СУКНЯ ANGEL:
- Кольори: чорний, білий, червоний
- Тканина: атлас та натуральне пір'я
- Чашка: з пушапом або без
- Ціна: 4690 грн
- Довжина: 83 см
- Пір'я потребує дбайливого ставлення. У разі повернення в пошкодженому стані — не приймається

КОРСЕТ ANGEL:
- Кольори: чорний, білий, червоний
- Тканина: атлас та натуральне пір'я
- Чашка: з пушапом або без
- Ціна: 3590 грн
- Довжина: 83 см

СУКНЯ EMI:
- Кольори: темно-синій (довгий рукав), блакитний (короткий рукав)
- Тканина: шифон та стрейчова підкладка
- Розміри: XS, S, M
- Ціна: 3150 грн
- Індивідуальний колір — можливо

СУКНЯ З ЛЬОНУ:
- Кольори: молочний, рожевий, блакитний
- Тканина: льон + віскоза — завдяки віскозі сукня практично не мнеться
- Розміри: S (підходить XS-S), M (підходить M-L) — крій на запах, регулюється по фігурі
- Ціна: 3150 грн

СВЕТР:
- Колір: молочний
- Тканина: 100% віскоза (м'який, дихаючий, не колеться)
- Розміри: S (підходить XS-S), M (підходить M-L)
- Ціна: 2150 грн

СУКНЯ TESSA:
- Кольори: рожева, квітково-рожева, квітково-блакитна (індивідуально — будь-який колір)
- Тканина: преміум органза
- Розміри: XS, S, M (вільний крій — по параметрах НЕ шиємо)
- Ціна: 3650 грн
- Відкрита спина
- Довжина: 79 см (від початку горла, без комірця)

СУКНЯ ГОРТЕНЗІЯ (також: Gortenzia, Гортензия):
- Кольори: квітково-блакитна (сині троянди на молочному), квітково-пастельна (пастельні квіти — блакитний, рожевий, жовтий)
- Тканина: льон + віскоза
- Розміри: XS, S, M (вільний крій)
- Ціна: 3490 грн
- Відкрита спина з бантом
- Короткий пишний рукав, багатоярусна спідниця, V-подібний виріз з гудзиками
- Довжина: 83 см

СУКНЯ ARIEL:
- Кольори: блакитний (індивідуально — будь-який колір, +500 грн)
- Тканина: преміум органза
- Розміри: XS, S, M
- Ціна: 4690 грн (індивідуальний колір — 5190 грн)
- Довжина: права сторона 37 см, ліва сторона 44 см (асиметричний крій)

ТРЕНЧ:
- Варіант 1: котон, кольори — синій та кемел, розміри S (XS-S) і M (M-L), оверсайз фасон
- Варіант 2: штучна шкіра, колір — гіркий шоколад, розміри S (XS-S) і M (M-L)
- Ціна: 4250 грн
- Довжина: 63 см (розрахований на зріст до 185 см)

СУКНЯ BIRTHDAY:
- Кольори: чорний, білий (індивідуально — будь-який колір)
- Тканина: атлас
- Розміри: XS, S, M
- Ціна: 3400 грн
- Довжина: 83 см

СУКНЯ MUSE:
- Колір: білий (індивідуально — будь-який колір)
- Тканина: мереживо (щільне, нічого не просвічує)
- Розміри: XS, S, M
- Ціна: 4300 грн
- Підкладки немає, але мереживо щільне. На грудях волани.
- Довжина: 150 см (від найвищої точки плеча до найнижчого волана ззаду)
- ⚠️ Наразі немає тканини, очікується у червні

СУКНЯ MARCH:
- Варіант жакард: кольори — молочний (білий), чорний; ціна 5100 грн
- Варіант льон: колір — рожевий; ціна 3750 грн
- Тканина: жакард (преміальний, рельєфний візерунок) або льон з віскозою
- Розміри: XS, S, M
- Силует: закрите горло з фігурним вирізом-замочком на грудях, без рукавів, корсетний верх, двоярусна пишна спідниця-міні
- Довжина: 83 см
- ⚠️ Жакард молочний — очікуємо тканину, буде приблизно у червні

КОСТЮМ MERMAID (також: Русалка, Mermaid):
- Колір: шампань/нюд з сріблястим блиском, великі перламутрові пелюстки-декор
- Тканина: напівпрозора сітка з блискітками
- Комплект: топ з відкритою спиною + спідниця (2 довжини на вибір)
- Топ: закрите горло, відкрита спина, короткий
- Спідниця коротка (міні) — ціна костюму: 5500 грн
- Спідниця довга (максі, з розрізом) — ціна костюму: 6100 грн
- Розміри: XS, S, M (прилеглий крій)
- ВАЖЛИВО: при оформленні замовлення обов'язково уточнити зріст клієнтки

СУКНЯ BELLE (вечірня колекція) — МІСТИТЬ НАТУРАЛЬНЕ ПІР'Я:
- Колір: срібний (пайєтки)
- Тканина: пайєтки + підкладка з сітки
- Деталі: натуральне біле пір'я по низу сукні, глибоко відкрита спина, тонкі бретельки зі стразами
- Силует: приталений, у підлогу
- Розміри: XS, S, M
- Ціна: 6400 грн
- Довжина: 83 см
- При запиті уточнити: дата, місто, формат заходу (щоб уникнути збігів)
- Пір'я потребує дбайливого ставлення. У разі повернення в пошкодженому стані — не приймається

БОДІ SOUL (також: Soul, Соул):
- Кольори: білий, чорний, коричневий
- Тканина: мікромасло
- Розміри: XS, S, M (прилеглий крій)
- Ціна: 1490 грн
- Силует: довгий рукав, закрите горло, виріз-замочок на грудях, облягаючий

ЖАКЕТ:
- Кольори: молочний, кемел (camel)
- Тканина: вовна 40% + віскоза 60%
- Розміри: XS, S, M
- Ціна: 4000 грн
- Силует: укорочений, комірець з лацканами, приталений

ЮБКА З ПІР'ЯМ:
- Колір: чорний
- Тканина: джинс
- Ціна: 2250 грн

=== ВІДПРАВКА ===
- Терміни: 4–7 робочих днів (субота і неділя — вихідний)
- Відправляємо з Одеси. Самовивозу немає. Особистих зустрічей та примірок немає — тільки доставка.
- Способи: Нова Пошта, кур'єр по Одесі, автобус (за погодженням)

=== ОБМІН ТА ПОВЕРНЕННЯ ===
- Протягом 3 днів з моменту отримання
- Якщо знято бірки та захисну пломбу — відмовляємо
- Якщо минуло 3 дні — відмовляємо
- Товари зі слідами використання — не повертаються
- Для повернення коштів: заява + фото паспорта
- Для повернення товару: послуга НП "Легке повернення"
- Закордонні замовлення — лише обмін, не повернення

=== ОПЛАТА ===
- Звичайне замовлення: передоплата 300 грн або повна оплата
- Індивідуальне замовлення: ТІЛЬКИ повна оплата
- Закордонні замовлення: ТІЛЬКИ повна оплата + вартість доставки
- Реквізити (гривня, ФОП):
  Отримувач: ФОП Думброва Тетяна Валеріївна
  IBAN: UA933220010000026003350075099
  Банк: Акціонерне товариство УНІВЕРСАЛ БАНК
- PayPal: tetanaglazkova92@gmail.com
- Крипта (TRC20): TTGMtoFq2QQC4jmCPQVbG5TqbxviKLRiUc
- USD SWIFT IBAN: UA053220010000026208356914421, BIC: UNJSUAUKXXX
- EUR SEPA IBAN: GB51CLJU00997181964975, BIC: CLJUGB21

=== ДОСТАВКА ЗА КОРДОН ===
- Відправляємо туди, куди доїжджає Нова Пошта
- До Росії та Білорусі НЕ відправляємо — жодних винятків
- Тільки повна оплата включно з вартістю доставки

=== ІНДИВІДУАЛЬНИЙ ПОШИВ ===
- Боді: +300 грн, інші позиції: +500 грн
- Тільки після повної оплати, без обміну/повернення
- Тканини для Tessa і Ariel: @tkanini_itsmyday (сторіс "Віск принт" і "Воск однотон")
- Тканини для Emi: на сайті, пошук "шифон"

=== РОЗМІРНІ СІТКИ ===

Вільний крій (Тесса, Гортензія):
- XS: груди 79-87, талія 58-64, бедра 89-99
- S: груди 85-95, талія 65-69, бедра 95-100
- M: груди 95-105, талія 70-76, бедра 100-110

Прилеглий крій (Angel, Ariel, Emi, March, Belle, Muse, сукня Melissa, боді Melissa, корсет, Birthday, Mermaid):
- XS: груди 79-85, талія 59-63, бедра 89-93
- S: груди 84-88, талія 64-68, бедра 94-98
- M: груди 88-94, талія 69-74, бедра 97-103

Тренч:
- S: груди 82-91, талія 60-68, бедра 99-100
- M: груди 89-100, талія 69-81, бедра 98-113

Светр, сукня з льону (універсальні):
- S — підходить на XS-S
- M — підходить на M-L

=== ПРАВИЛА ВІДПОВІДЕЙ ===

ВАЖЛИВО: Якщо клієнт питає про щось, чого немає в базі знань (нові колекції, акції, знижки, нестандартні способи оплати тощо) — напиши щось у стилі: "Зараз передам це питання старшому менеджеру, він вам відпише 🤍" або "Переключаю вас на старшого менеджера, він уточнить всі деталі 🤍" — варіюй фразу, щоб звучало природньо.

ІНДИВІДУАЛЬНИЙ ПОШИВ: Якщо клієнт просить змінити щось у моделі — НЕ кажи що це неможливо. Відповідай що у нас є індивідуальний пошив і передавай старшому менеджеру: "Так, індивідуальні зміни ми розглядаємо! Зараз передам це старшому менеджеру, він уточнить всі деталі та вартість 🤍"

ТЕРМІНОВА ВІДПРАВКА: Якщо клієнт питає чи можна відправити сьогодні або терміново — відповідай: "Зараз уточню на виробництві і відпишу вам! 🤍"

НАЯВНІСТЬ: Якщо клієнт питає про сукню MUSE або сукню MARCH молочну — повідом що наразі тканини немає, очікуємо у червні.

ВЗУТТЯ: Взуття не виготовляємо і не продаємо.

=== НАЗВИ МОДЕЛЕЙ — СИНОНІМИ ТА ТРАНСЛІТЕРАЦІЯ ===
- Belle = Бель = Белла = бель
- Гортензія = Gortenzia = Гортензия
- Mermaid = Русалка = мермейд = русалка
- Birthday = бёздей = бездей = бёрздей = бёрсдей
- March = Марч
- Angel = Енджел
- Ariel = Аріель = ариэль
- Muse = Мюз = мьюз
- Emi = Емі = эми
- Melissa = Меліса = мелисса
- Tessa = Теса = тесса
- Soul = Соул

=== МОДЕЛІ З НАТУРАЛЬНИМ ПІР'ЯМ ===
Якщо клієнт питає про моделі з пір'ям — ЗАВЖДИ називай всі три: Сукня ANGEL, Корсет ANGEL, Сукня BELLE.

=== ІНШЕ ===
- Взуття: не виготовляємо і не продаємо
- Дропшипінг: не працюємо
- Опт: від 10 одиниць — знижка 10%
- Кілька позицій: передоплата 300 грн за кожну одиницю окремо
- Параметри Тані (модель): зріст 173 см, розмір XS, ОГ 82, ОТ 60, ОБ 90"""

# Зберігаємо історію розмов по кожному користувачу
conversation_history = {}


def get_claude_reply(user_id, message_text, image_url=None):
    """Отримати відповідь від Claude"""
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Формуємо контент повідомлення
    if image_url:
        try:
            req = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                image_data = base64.b64encode(r.read()).decode()
            content = [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}},
                {"type": "text", "text": message_text or "Що це за модель на фото?"}
            ]
        except Exception as e:
            print(f"Image load error: {e}")
            content = message_text or "Клієнт надіслав фото"
    else:
        content = message_text

    conversation_history[user_id].append({"role": "user", "content": content})

    # Тримаємо не більше 20 повідомлень
    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]

    req_data = json.dumps({
        "model": "claude-sonnet-4-5",
        "max_tokens": 600,
        "system": SYSTEM,
        "messages": conversation_history[user_id]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=req_data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read())
        reply = result["content"][0]["text"]
        conversation_history[user_id].append({"role": "assistant", "content": reply})
        return reply
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Claude API error {e.code}: {body}")
        return "Вибачте, сталася помилка. Спробуйте ще раз 🤍"
    except Exception as e:
        print(f"Claude error: {e}")
        return "Вибачте, сталася помилка. Спробуйте ще раз 🤍"


def send_instagram_message(recipient_id, text):
    """Відправити повідомлення через Facebook Graph API (Instagram Business)"""
    # Розбиваємо довгі повідомлення (ліміт 1000 символів)
    chunks = [text[i:i+950] for i in range(0, len(text), 950)]
    for chunk in chunks:
        data = json.dumps({
            "recipient": {"id": recipient_id},
            "message": {"text": chunk}
        }).encode("utf-8")

        url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
        req = urllib.request.Request(url, data=data,
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req) as r:
                print(f"Sent to {recipient_id}: {r.read()[:100]}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"Send error {e.code}: {body}")
        except Exception as e:
            print(f"Send error: {e}")


def notify_telegram(user_id, user_message, bot_reply):
    """Сповістити власника в Telegram коли потрібен менеджер"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    # Перевіряємо чи бот передає питання менеджеру
    manager_phrases = ["старшому менеджеру", "старшего менеджера", "передам це питання",
                       "уточню на виробництві", "переключаю вас"]
    needs_manager = any(p in bot_reply.lower() for p in manager_phrases)

    if not needs_manager:
        return

    text = (f"🔔 *Потрібен менеджер!*\n\n"
            f"👤 ID клієнта: `{user_id}`\n"
            f"💬 Питання: {user_message}\n"
            f"🤖 Відповідь бота: {bot_reply}")

    data = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }).encode("utf-8")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        urllib.request.urlopen(req)
        print(f"Telegram notified for user {user_id}")
    except Exception as e:
        print(f"Telegram error: {e}")


class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Вимикаємо стандартні логи

    def do_GET(self):
        """Верифікація webhook від Meta"""
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        mode      = params.get("hub.mode",         [""])[0]
        token     = params.get("hub.verify_token", [""])[0]
        challenge = params.get("hub.challenge",    [""])[0]

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print(f"✅ Webhook verified!")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(challenge.encode())
        else:
            print(f"❌ Webhook verification failed. Token: {token}")
            self.send_response(403)
            self.end_headers()

    def do_POST(self):
        """Отримання повідомлень від Instagram"""
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length))
        except Exception:
            self.send_response(200)
            self.end_headers()
            return

        # Відповідаємо Meta одразу (вимога — відповісти протягом 20 сек)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

        print(f"Event: {json.dumps(body, ensure_ascii=False)[:300]}")

        if body.get("object") not in ("instagram", "page"):
            return

        for entry in body.get("entry", []):
            for event in entry.get("messaging", []):
                sender_id = event.get("sender", {}).get("id")
                if not sender_id:
                    continue

                message = event.get("message", {})
                if not message or message.get("is_echo"):
                    continue

                message_text = message.get("text", "")
                image_url    = None

                # Обробка зображень та сторіс
                for att in message.get("attachments", []):
                    att_type = att.get("type", "")
                    if att_type in ("image", "story_mention", "story_reply", "ig_reel"):
                        image_url = att.get("payload", {}).get("url")
                        if not message_text:
                            message_text = att.get("title", "") or "Що це за модель на фото?"

                if not message_text and not image_url:
                    continue

                print(f"Message from {sender_id}: {message_text[:100]}")

                # Отримуємо відповідь від Claude
                reply = get_claude_reply(sender_id, message_text, image_url)
                print(f"Reply: {reply[:100]}")

                # Відправляємо відповідь в Instagram
                send_instagram_message(sender_id, reply)

                # Сповіщуємо Telegram якщо потрібен менеджер
                notify_telegram(sender_id, message_text, reply)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"✅ Tessa Instagram Bot запущено на порту {port}")
    print(f"   Webhook: POST/GET /webhook")
    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    server.serve_forever()
