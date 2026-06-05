import os
import json
import urllib.request
import urllib.error
import urllib.parse
import base64
from http.server import BaseHTTPRequestHandler
from socketserver import ThreadingMixIn, TCPServer

class ThreadingHTTPServer(ThreadingMixIn, TCPServer):
    allow_reuse_address = True

# === НАЛАШТУВАННЯ ===
VERIFY_TOKEN       = os.environ.get("VERIFY_TOKEN", "tessa_verify_2024")
PAGE_ACCESS_TOKEN  = os.environ.get("PAGE_ACCESS_TOKEN", "")
ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")

# === СИСТЕМНИЙ ПРОМПТ ===
SYSTEM = """Ти — дружелюбний менеджер інтернет-магазину Tessa Brand. Спілкуєшся з клієнтами в Instagram Direct. Відповідай ЗАВЖДИ українською мовою, ОКРІМ випадку коли клієнт пише англійською — тоді відповідай англійською. Якщо клієнт пише російською — відповідай українською. Відповіді короткі — 2–5 речень. Можна 1 емодзі. Ніколи не вигадуй деталей яких немає в базі знань. Коли фіксуєш замовлення — завжди уточнюй колір, розмір і всі деталі.
ВАЖЛИВО: Використовуй ТІЛЬКИ правильну українську лексику. НЕ змішуй з російськими словами. Правильно: "наявності" (не "наличності"), "замовлення" (не "заказ"), "доставка" (не "отправка"), "розмір" (не "размер").

🔴 ОБОВ'ЯЗКОВЕ ПРАВИЛО ПРО ФОТО: Щоразу коли клієнт просить фото або ти згадуєш конкретну модель — ТИ ЗОБОВ'ЯЗАНИЙ додати тег [IMG:назва] в кінці відповіді. БЕЗ тегу відповідь є НЕПОВНОЮ. Якщо не знаєш який тег — дивись список нижче в розділі ФОТО МОДЕЛЕЙ.
🔴 ОБОВ'ЯЗКОВЕ ПРАВИЛО ПРО РОЗМІРИ: Коли клієнт просить розмірну сітку — ЗАБОРОНЕНО писати цифри. Тільки тег [IMG:size_...] + одне речення.

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
Розміри є в таблицях-фото. Коли клієнт питає про розміри — ЗАВЖДИ надсилай фото сітки тегом, НЕ пиши цифри в тексті:
- Tessa, Гортензія → [IMG:size_tessa]
- Angel, Ariel, Emi, March, Belle, Muse, Melissa, корсет, Birthday, Mermaid → [IMG:size_fitted]
- Тренч → [IMG:size_trench]
- Светр, льон → тільки текст: "S = XS-S, M = M-L"
Приклад: "Ось розмірна сітка 🤍 [IMG:size_fitted] Який розмір вам підходить?"

=== ПРАВИЛА ВІДПОВІДЕЙ ===

ПОКАЗ КАТАЛОГУ: Якщо клієнт питає "які є сукні/варіанти/моделі" без уточнення — спочатку спитай про стиль або нагоду ("Для якого приводу шукаєш? Вечірня, повсякденна, літня?"). Якщо клієнт вже уточнив або хоче побачити конкретні моделі — показуй максимум 3-4 варіанти, кожен з коротким описом і тегом фото. Формат: "**НАЗВА** — опис, ціна. [IMG:ключ]" — по одній моделі на абзац.

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
- Параметри Тані (модель): зріст 173 см, розмір XS, ОГ 82, ОТ 60, ОБ 90

=== РОЗМІРНІ СІТКИ (фото) ===
Коли клієнт питає про розміри або розмірну сітку — НІКОЛИ не пиши цифри параметрів у тексті! ЗАВЖДИ відповідай тільки коротким текстом + тегом:
- Tessa, Гортензія → [IMG:size_tessa]
- Angel, Ariel, Emi, March, Belle, Muse, Melissa, корсет, Birthday, Mermaid → [IMG:size_fitted]
- Тренч → [IMG:size_trench]
- Светр, льон — ТІЛЬКИ текст: "S підходить на XS-S, M підходить на M-L"
Приклад правильної відповіді: "Ось розмірна сітка 🤍 [IMG:size_fitted]"

=== ФОТО МОДЕЛЕЙ ===
Коли клієнт питає про конкретну модель або просить показати фото — додай відповідний тег в кінці відповіді:
- ANGEL чорна → [IMG:angel_black]
- ANGEL червона → [IMG:angel_red]
- ANGEL біла → [IMG:angel_white]
- ANGEL (колір не уточнено) → [IMG:angel_black][IMG:angel_red][IMG:angel_white]
- Корсет ANGEL чорний → [IMG:corset_black]
- Корсет ANGEL червоний → [IMG:corset_red]
- Корсет ANGEL (не уточнено) → [IMG:corset_black][IMG:corset_red]
- EMI блакитна → [IMG:emi_blue]
- EMI темно-синя → [IMG:emi_dark]
- MARCH жакард молочний → [IMG:march_white]
- MARCH жакард чорний → [IMG:march_black]
- MARCH жакард (не уточнено) → [IMG:march_white][IMG:march_black]
- MARCH льон → [IMG:march_linen]
- MUSE → [IMG:muse]
- BELLE → [IMG:belle]
- ГОРТЕНЗІЯ → [IMG:gortenzia_1][IMG:gortenzia_2]
- MELISSA сукня біла → [IMG:melissa_dress_white]
- MELISSA сукня чорна → [IMG:melissa_dress_black]
- MELISSA сукня (не уточнено) → [IMG:melissa_dress_white][IMG:melissa_dress_black]
- MELISSA боді молочний → [IMG:melissa_bodi]
- MELISSA боді чорний → [IMG:melissa_bodi_black]
- MELISSA боді (не уточнено) → [IMG:melissa_bodi][IMG:melissa_bodi_black]
- Сукня з льону → [IMG:linen_dress]
- Светр → [IMG:sweater]
- Тренч → [IMG:trench]
- ARIEL → [IMG:ariel]
- SOUL боді → [IMG:soul_bodi]
- Жакет → [IMG:jacket]
- BIRTHDAY → [IMG:birthday]
- TESSA → [IMG:tessa]
- MERMAID (Русалка) → [IMG:mermaid]"""

# Базовий URL для фото (GitHub raw — завжди доступний для Instagram)
BASE_URL = "https://raw.githubusercontent.com/tetanaglazkova92-debug/tessabot/main"

# Маппінг IMG-тегів до файлів
IMG_MAP = {
    "angel": "angel.jpg", "angel_black": "angel_black.jpg",
    "angel_red": "angel_red.jpg", "angel_white": "angel_white.jpg",
    "corset_angel": "corset_angel.jpg", "corset_black": "corset_black.jpg",
    "corset_red": "corset_red.jpg", "emi_blue": "emi_blue.jpg",
    "emi_dark": "emi_dark.jpg", "march": "march.jpg",
    "march_white": "march_white.jpg", "march_black": "march_black.jpg",
    "march_linen": "march_linen.jpg", "muse": "muse.jpg",
    "belle": "belle.jpg", "gortenzia": "gortenzia.jpg",
    "gortenzia_1": "gortenzia_1.jpg", "gortenzia_2": "gortenzia_2.jpg",
    "melissa_dress": "melissa_dress.jpg", "melissa_dress_white": "melissa_dress_white.jpg",
    "melissa_dress_black": "melissa_dress_black.jpg", "melissa_bodi": "melissa_bodi.jpg",
    "melissa_bodi_black": "melissa_bodi_black.jpg", "linen_dress": "linen_dress.jpg",
    "sweater": "sweater.jpg", "trench": "trench.jpg", "ariel": "ariel.jpg",
    "soul_bodi": "soul_bodi.jpg", "jacket": "jacket.jpg",
    "birthday": "birthday.jpg", "tessa": "tessa.jpg", "mermaid": "mermaid.jpg",
    "size_tessa": "size_tessa.png", "size_fitted": "size_fitted.png",
    "size_trench": "size_trench.png",
}

# Зберігаємо історію розмов по кожному користувачу
conversation_history = {}
# Дедуплікація — зберігаємо оброблені ID повідомлень
processed_mids = set()
MAX_PROCESSED = 1000  # щоб не переповнювати пам'ять
# Клієнти для яких бот на паузі (менеджер відповідає)
paused_users = set()


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
    """Відправити текстове повідомлення"""
    chunks = [text[i:i+950] for i in range(0, len(text), 950)]
    for chunk in chunks:
        if not chunk.strip():
            continue
        data = json.dumps({
            "recipient": {"id": recipient_id},
            "message": {"text": chunk}
        }).encode("utf-8")
        url = f"https://graph.instagram.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
        req = urllib.request.Request(url, data=data,
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req) as r:
                print(f"Sent text to {recipient_id}: {r.read()[:80]}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"Send text error {e.code}: {body}")
        except Exception as e:
            print(f"Send text error: {e}")


def send_instagram_image(recipient_id, img_key):
    """Відправити фото через Instagram"""
    filename = IMG_MAP.get(img_key)
    if not filename:
        return
    img_url = f"{BASE_URL}/photos/{filename}"
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "image",
                "payload": {"url": img_url, "is_reusable": True}
            }
        }
    }).encode("utf-8")
    url = f"https://graph.instagram.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            print(f"Sent image {img_key} to {recipient_id}: {r.read()[:80]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Send image error {e.code}: {body}")
    except Exception as e:
        print(f"Send image error: {e}")


def get_instagram_name(user_id):
    """Отримати ім'я клієнта з Instagram"""
    try:
        url = f"https://graph.instagram.com/v21.0/{user_id}?fields=name&access_token={PAGE_ACCESS_TOKEN}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
            return data.get("name", user_id)
    except:
        return user_id


def notify_telegram(user_id, user_message, bot_reply):
    """Сповістити власника в Telegram коли потрібен менеджер"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    manager_phrases = ["старшому менеджеру", "старшего менеджера", "передам це питання",
                       "уточню на виробництві", "переключаю вас"]
    needs_manager = any(p in bot_reply.lower() for p in manager_phrases)

    if not needs_manager:
        return

    # Отримуємо ім'я клієнта
    client_name = get_instagram_name(user_id)

    text = (f"🔔 *Потрібен менеджер!*\n\n"
            f"👤 Клієнт: {client_name}\n"
            f"💬 Питання: {user_message}\n"
            f"🤖 Бот відповів: {bot_reply}")

    # Кнопки: Пауза бота / Бот активний
    keyboard = {
        "inline_keyboard": [[
            {"text": "⏸ Взяти в роботу", "callback_data": f"pause_{user_id}"},
            {"text": "▶️ Бот активний", "callback_data": f"resume_{user_id}"}
        ]]
    }

    data = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": keyboard
    }).encode("utf-8")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        urllib.request.urlopen(req)
        print(f"Telegram notified for user {user_id} ({client_name})")
    except Exception as e:
        print(f"Telegram error: {e}")


def handle_telegram_callback(callback_query):
    """Обробка натискання кнопок в Telegram"""
    callback_id = callback_query.get("id")
    data = callback_query.get("data", "")
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")

    if data.startswith("pause_"):
        user_id = data[6:]
        paused_users.add(user_id)
        answer_text = f"⏸ Бот на паузі для клієнта. Відповідай сам!"
        print(f"Bot paused for {user_id}")
    elif data.startswith("resume_"):
        user_id = data[7:]
        paused_users.discard(user_id)
        answer_text = f"▶️ Бот знову активний для клієнта!"
        print(f"Bot resumed for {user_id}")
    else:
        answer_text = "OK"

    # Підтверджуємо натискання кнопки
    confirm_data = json.dumps({"callback_query_id": callback_id, "text": answer_text}).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery",
        data=confirm_data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        urllib.request.urlopen(req)
    except:
        pass


class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Вимикаємо стандартні логи

    def do_GET(self):
        """Верифікація webhook від Meta + Privacy Policy"""
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        # Serve photos
        if parsed.path.startswith("/photos/"):
            filename = parsed.path[8:]  # remove /photos/
            photo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photos", filename)
            if os.path.exists(photo_path) and (filename.endswith(".jpg") or filename.endswith(".png")):
                with open(photo_path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                mime = "image/png" if filename.endswith(".png") else "image/jpeg"
                self.send_header("Content-Type", mime)
                self.send_header("Cache-Control", "public, max-age=86400")
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_response(404)
                self.end_headers()
            return

        # Privacy Policy page
        if parsed.path == "/privacy":
            html = b"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Privacy Policy - Tessa Brand Bot</title></head><body>
<h1>Privacy Policy</h1><p>Last updated: June 2026</p>
<p>Tessa Brand ("we") operates the Tessa Brand Instagram messaging bot.</p>
<h2>Information We Collect</h2>
<p>We collect messages sent to our Instagram account to provide customer support and product information. We do not store personal data beyond the conversation session.</p>
<h2>How We Use Information</h2>
<p>Messages are processed to provide automated responses about our products. We do not share, sell, or transfer your data to third parties.</p>
<h2>Contact</h2>
<p>Questions? Contact us at tessa_brand_store on Instagram.</p>
</body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html)
            return

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
        """Отримання повідомлень від Instagram та Telegram"""
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length))
        except Exception:
            self.send_response(200)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

        # Обробка Telegram callback (кнопки)
        if "callback_query" in body:
            handle_telegram_callback(body["callback_query"])
            return

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

                # Дедуплікація по message ID
                mid = message.get("mid", "")
                if mid and mid in processed_mids:
                    print(f"⚠️ Duplicate message {mid}, skipping")
                    continue
                if mid:
                    processed_mids.add(mid)
                    if len(processed_mids) > MAX_PROCESSED:
                        processed_mids.pop()

                # Відхиляємо старі повідомлення (Instagram retry >5 хв)
                import time
                msg_time = event.get("timestamp", 0) / 1000
                if msg_time and (time.time() - msg_time) > 300:
                    print(f"⚠️ Old message ({int(time.time()-msg_time)}s ago), skipping")
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

                # Якщо бот на паузі для цього клієнта — мовчимо
                if sender_id in paused_users:
                    print(f"⏸ Bot paused for {sender_id}, skipping")
                    continue

                print(f"Message from {sender_id}: {message_text[:100]}")

                # Отримуємо відповідь від Claude
                reply = get_claude_reply(sender_id, message_text, image_url)
                print(f"Reply: {reply[:100]}")

                # Парсимо [IMG:key] теги
                import re
                img_keys = re.findall(r'\[IMG:(\w+)\]', reply)
                clean_reply = re.sub(r'\[IMG:[^\]]+\]', '', reply).strip()

                # Відправляємо текст
                if clean_reply:
                    send_instagram_message(sender_id, clean_reply)

                # Відправляємо фото
                for key in img_keys:
                    send_instagram_image(sender_id, key)

                # Сповіщуємо Telegram якщо потрібен менеджер
                notify_telegram(sender_id, message_text, reply)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"✅ Tessa Instagram Bot запущено на порту {port}")
    print(f"   Webhook: POST/GET /webhook")
    server = ThreadingHTTPServer(("0.0.0.0", port), WebhookHandler)
    server.serve_forever()
